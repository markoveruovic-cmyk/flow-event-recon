"""
Flow Event Recon configuration.
Upravuj tady klíčová slova, kategorie a zdroje.
"""

# ─────────────────────────────────────────────────────────────
# KEYWORDS — used for scoring + topic categorization
# ─────────────────────────────────────────────────────────────

# ICP keywords - top priority (retail, banking, e-commerce, insurance)
ICP_KEYWORDS = [
    "retail", "banking", "fintech", "e-commerce", "ecommerce", "e-com",
    "insurance", "BFSI", "digital banking", "payments", "open banking",
    "neobank", "wealth", "asset management", "capital markets",
]

# Tech / service area keywords
TECH_KEYWORDS = [
    "mobile app", "mobile development", "iOS", "Android",
    "UX", "UI", "product design", "design system",
    "AI", "AI agents", "AI assistants", "GenAI",
    "multiplatform", "kotlin multiplatform", "flutter", "react native",
    "app store optimization", "ASO",
    "customer experience", "CX",
]

# Target cities (Denmark focus)
TARGET_CITIES = [
    "copenhagen", "kobenhavn", "københavn", "aarhus", "odense", "aalborg",
    "bella center", "amsterdam",  # bella center used by techbbq; amsterdam for money20/20 delegations
]

# Online events with Danish community are also relevant
DANISH_ONLINE_KEYWORDS = ["denmark", "danish", "nordic", "dansk", "copenhagen"]

# ─────────────────────────────────────────────────────────────
# CATEGORIZATION TAXONOMY
# Each event gets ONE format and ONE topic (or "Other" if unclear).
# Rules are applied in order — first match wins.
# ─────────────────────────────────────────────────────────────

# Format = what kind of event it is
FORMAT_RULES = [
    # (label, keywords to match in title + description, case-insensitive)
    ("Demo Day",   ["demo day", "pitch day", "showcase"]),
    ("Summit",     ["summit"]),
    ("Conference", ["conference", "kongres"]),
    ("Workshop",   ["workshop", "masterclass", "bootcamp", "training"]),
    ("Webinar",    ["webinar", "online session", "virtual session"]),
    ("Meetup",     ["meetup", "networking", "meet-up", "meet up", "breakfast", "lunch session"]),
    ("Delegation", ["delegation"]),
]

# Topic = what it's about
TOPIC_RULES = [
    ("Fintech & Banking",
     ["fintech", "banking", "bank ", "payments", "open banking", "digital finance",
      "wealth", "neobank", "money20", "aml", "regtech", "capital markets"]),
    ("Insurance & BFSI",
     ["insurance", "insurtech", "bfsi", "risk management"]),
    ("Retail & E-commerce",
     ["retail", "e-commerce", "ecommerce", "commerce", "customer experience",
      "conversion", "cx", "merchandising"]),
    ("AI",
     ["ai agents", "ai assistants", "genai", "llm", "generative ai",
      " ai ", "ai-", "artificial intelligence", "machine learning"]),
    ("Mobile & Design",
     ["mobile app", "ios", "android", "kotlin multiplatform", "flutter",
      "react native", "ux", "ui ", "product design", "design system", "aso"]),
    ("Crypto & Web3",
     ["crypto", "blockchain", "web3", "digital assets", "defi", "nft"]),
    ("General Tech",
     ["tech", "software", "developer", "engineering", "startup"]),
]

# ─────────────────────────────────────────────────────────────
# SCORING
# ─────────────────────────────────────────────────────────────

SCORE_ICP_IN_TITLE = 20
SCORE_ICP_IN_DESCRIPTION = 10
SCORE_TECH_IN_TITLE = 10
SCORE_TECH_IN_DESCRIPTION = 5
SCORE_CITY_MATCH = 10
SCORE_IS_FREE = 5
SCORE_MAX = 100

# Score tiers
SCORE_TIER_HIGH = 80
SCORE_TIER_MEDIUM = 50

# Bonus for specific high-value topics (encourages fintech/retail/insurance to rise)
TOPIC_SCORE_BONUS = {
    "Fintech & Banking": 20,
    "Retail & E-commerce": 20,
    "Insurance & BFSI": 20,
    "AI": 15,
    "Mobile & Design": 15,
    "Crypto & Web3": 0,
    "General Tech": 5,
    "Other": 0,
}

# Bonus for event formats that are typically high-value for networking / business
FORMAT_SCORE_BONUS = {
    "Conference": 15,
    "Summit": 15,
    "Demo Day": 10,
    "Workshop": 5,
    "Delegation": 5,
    "Meetup": 0,
    "Webinar": 0,
    "Other": 0,
}

# ─────────────────────────────────────────────────────────────
# SOURCES
# ─────────────────────────────────────────────────────────────

SOURCES = {
    "copenhagen_fintech": {
        "enabled": True,
        "type": "copenhagen_fintech",
        "url": "https://www.copenhagenfintech.dk/events",
    },
    "luma_copenhagen": {
        "enabled": True,
        "type": "luma",
        "url": "https://lu.ma/copenhagen",
        "city_default": "Copenhagen",
    },
    "luma_aarhus": {
        "enabled": True,
        "type": "luma",
        "url": "https://lu.ma/aarhus",
        "city_default": "Aarhus",
    },
    "eventbrite_cph": {
        "enabled": True,
        "type": "eventbrite",
        "url": "https://www.eventbrite.dk/d/denmark--copenhagen/business--events/",
        "city_default": "Copenhagen",
    },
    "eventbrite_cph_tech": {
        "enabled": True,
        "type": "eventbrite",
        "url": "https://www.eventbrite.dk/d/denmark--copenhagen/science-and-tech--events/",
        "city_default": "Copenhagen",
    },
}

# Output files
CSV_OUTPUT = "events.csv"
HTML_OUTPUT = "index.html"

# Description truncation
DESCRIPTION_MAX_LENGTH = 300
