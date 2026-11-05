"""Synthetic knowledge base for the fictional Northstar Home support assistant."""

FAQS = [
    {
        "id": "returns",
        "title": "Returns and exchanges",
        "keywords": {"return", "returns", "refund", "exchange", "unused", "packaging"},
        "answer": "Eligible products can be returned within 7 days of delivery if they are unused and in their original packaging.",
        "context": "Return policy: Eligible products can be returned within 7 days of delivery if unused and in original packaging.",
        "must_include": ["7 days", "unused", "original packaging"],
    },
    {
        "id": "shipping",
        "title": "Shipping and delivery",
        "keywords": {"shipping", "delivery", "deliver", "track", "tracking", "dispatch", "order"},
        "answer": "Standard delivery usually takes 3 to 5 business days.",
        "context": "Shipping policy: Standard delivery usually takes 3 to 5 business days. A tracking link is sent in the dispatch email.",
        "must_include": ["3 to 5 business days"],
    },
    {
        "id": "warranty",
        "title": "Warranty and repairs",
        "keywords": {"warranty", "guarantee", "repair", "defect", "broken", "faulty"},
        "answer": "Northstar Home products include a 2-year limited warranty from the date of purchase. Keep your proof of purchase for warranty support.",
        "context": "Warranty policy: Northstar Home products include a 2-year limited warranty from the date of purchase. Proof of purchase is required.",
        "must_include": ["2-year", "date of purchase", "proof of purchase"],
    },
    {
        "id": "support",
        "title": "Customer support",
        "keywords": {"contact", "support", "email", "phone", "help", "agent"},
        "answer": "You can contact Northstar Home support at support@example.test. Our support hours are Monday to Friday, 9:00 AM to 6:00 PM IST.",
        "context": "Support policy: Contact support@example.test, Monday to Friday, 9:00 AM to 6:00 PM IST.",
        "must_include": ["support@example.test", "Monday to Friday", "6:00 PM IST"],
    },
    {
        "id": "payments",
        "title": "Payment methods",
        "keywords": {"payment", "payments", "card", "cards", "upi", "cash", "cod", "wallet", "banking"},
        "answer": "Northstar Home accepts major credit and debit cards, UPI, and net banking. Cash on delivery is not available in this demo store.",
        "context": "Payment policy: Accepted methods are major credit cards, debit cards, UPI, and net banking. Cash on delivery is not available.",
        "must_include": ["credit", "debit", "UPI", "net banking"],
    },
    {
        "id": "products",
        "title": "Product categories",
        "keywords": {"product", "products", "category", "categories", "fan", "purifier", "mixer", "smart"},
        "answer": "Northstar Home's demo catalogue includes smart fans, mixer grinders, air purifiers, and smart plugs.",
        "context": "Product catalogue: smart fans, mixer grinders, air purifiers, and smart plugs.",
        "must_include": ["smart fans", "mixer grinders", "air purifiers", "smart plugs"],
    },
]

FALLBACK_MESSAGE = (
    "I don't have enough information in the support knowledge base to answer that reliably. "
    "Please contact Northstar Home support."
)

# Synthetic fixtures only. No real customer/order data is used.
ORDERS = {
    "NH-1001": {"status": "In transit", "eta": "2026-11-08", "carrier": "DemoShip"},
    "NH-1002": {"status": "Delivered", "eta": "2026-11-03", "carrier": "DemoShip"},
    "NH-1003": {"status": "Processing", "eta": "Not available yet", "carrier": "Not assigned"},
}
