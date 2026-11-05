"""Groq-backed DeepEval judge using JSON mode plus Pydantic validation.

Why this wrapper exists:
- DeepEval metrics request structured Pydantic outputs from their judge model.
- LiteLLM's Groq route can hit provider-side best-effort JSON-schema validation
  errors for some metric schemas/model responses.
- Groq JSON Object Mode guarantees syntactically valid JSON; this wrapper then
  validates the payload against DeepEval's requested Pydantic schema and retries
  a small number of times if the shape is incomplete.

This class is used only for evaluation. The application-under-test continues to
call Groq through app.service._call_groq.
"""
from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from groq import Groq
from pydantic import BaseModel, ValidationError
from deepeval.models import DeepEvalBaseLLM


class GroqJSONJudge(DeepEvalBaseLLM):
    """A DeepEval-compatible judge powered by Groq's Chat Completions API."""

    def __init__(self, model: str | None = None, api_key: str | None = None, max_retries: int = 3):
        self.model = (model or os.getenv("DEEPEVAL_MODEL_ID") or os.getenv("GROQ_MODEL_ID") or "openai/gpt-oss-20b").strip()
        self.api_key = (api_key or os.getenv("GROQ_API_KEY") or "").strip()
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is required to run live DeepEval evaluations.")
        self.max_retries = max(1, int(max_retries))
        self.client = Groq(api_key=self.api_key)

    def load_model(self) -> Groq:
        return self.client

    def get_model_name(self) -> str:
        return f"Groq JSON Judge ({self.model})"

    @staticmethod
    def _is_schema_class(schema: Any) -> bool:
        return isinstance(schema, type) and issubclass(schema, BaseModel)

    def generate(self, prompt: str, schema: type[BaseModel] | None = None) -> str | BaseModel:
        """Generate text, or return a validated Pydantic object when schema is supplied."""
        request_prompt = prompt
        if schema is not None:
            if not self._is_schema_class(schema):
                raise TypeError("DeepEval schema must be a Pydantic BaseModel class.")
            schema_json = json.dumps(schema.model_json_schema(), ensure_ascii=False)
            request_prompt += (
                "\n\nReturn exactly one JSON object. Do not use Markdown fences or add prose. "
                "The object must conform to this JSON schema:\n" + schema_json
            )

        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a precise evaluation judge for software quality testing. "
                            "Follow the user instructions exactly. When JSON is requested, return "
                            "only a valid JSON object with no Markdown or commentary."
                        ),
                    },
                    {"role": "user", "content": request_prompt},
                ],
                "temperature": 0,
                "max_completion_tokens": 2048,
            }
            # Groq documents low/medium/high reasoning_effort for GPT-OSS models.
            if self.model.startswith("openai/gpt-oss-"):
                kwargs["reasoning_effort"] = "low"
            if schema is not None:
                # JSON Object Mode avoids intermittent best-effort json_schema 400s.
                kwargs["response_format"] = {"type": "json_object"}

            response = self.load_model().chat.completions.create(**kwargs)
            content = (response.choices[0].message.content or "").strip()
            if schema is None:
                return content
            if not content:
                last_error = ValueError("Groq returned an empty response for the requested JSON object.")
            else:
                try:
                    return schema.model_validate_json(content)
                except (ValidationError, ValueError, TypeError) as exc:
                    last_error = exc

            if attempt + 1 < self.max_retries:
                request_prompt = (
                    prompt
                    + "\n\nYour previous response did not satisfy the required JSON schema. "
                    + f"Validation issue: {str(last_error)[:700]}. "
                    + "Return a corrected JSON object only, matching this schema exactly:\n"
                    + json.dumps(schema.model_json_schema(), ensure_ascii=False)
                )

        raise ValueError(
            f"Groq judge could not produce a response matching {schema.__name__} "
            f"after {self.max_retries} attempts: {last_error}"
        ) from last_error

    async def a_generate(self, prompt: str, schema: type[BaseModel] | None = None) -> str | BaseModel:
        """Async DeepEval interface; keep blocking SDK work off the event loop."""
        return await asyncio.to_thread(self.generate, prompt, schema)
