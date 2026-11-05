# DeepEval + Groq judge adapter

Northstar uses a custom DeepEval judge adapter instead of DeepEval's direct
LiteLLM Groq model route. The adapter calls Groq Chat Completions in JSON Object
Mode, then validates the returned JSON against the Pydantic schema supplied by
DeepEval. It retries schema validation up to three times.

This is deliberate: Groq's best-effort JSON Schema mode can return HTTP 400 when
model output does not validate. JSON Object Mode guarantees JSON syntax but not
schema adherence, so the project adds Pydantic validation and bounded retries.

Run:

```powershell
pip install -r requirements-eval.txt
# In .env: RUN_LLM_EVALS=true and a valid GROQ_API_KEY
deepeval test run tests/test_llm_eval.py -v
```

The judge may make multiple provider calls and consume API quota. Never commit
`.env` or share logs containing `Authorization: Bearer ...` headers.
