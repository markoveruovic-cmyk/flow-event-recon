"""
Flow Event Recon configuration.
Upravuj tady klíčová slova a nastavení - je to jediný soubor, kterého se musíš dotknout.
"""

# ICP keywords - top priority (retail, banking, e-commerce, insurance)
ICP_KEYWORDS = [
    "retail",
    "banking",
    "fintech",
    "e-commerce",
    "ecommerce",
    "e-com",
    "insurance",
    "BFSI",
    "digital banking",
    "payments",
    "open banking",
    "neobank",
]

# Tech / service area keywords
TECH_KEYWORDS = [
    "mobile app",
    "mobile development",
    "iOS",
    "Android",
    "UX",
    "UI",
    "product design",
    "design system",
    "AI",
    "AI agents",
    "AI assistants",
    "multiplatform",
    "kotlin multiplatform",
    "flutter",
    "react native",
    "app store optimization",
    "ASO",
    "customer experience",
    "CX",
]

# Target cities (Denmark focus)
TARGET_CITIES = [
    "copenhagen",
    "kobenhavn",
    "københavn",
    "aarhus",
    "odense",
    "aalborg",
]

# Online events with Danish community are also relevant
DANISH_ONLINE_KEYWORDS = ["denmark", "danish", "nordic", "dansk"]

# Scoring weights
SCORE_ICP_IN_TITLE = 20
SCORE_ICP_IN_DESCRIPTION = 10
SCORE_TECH_IN_TITLE = 10
SCORE_TECH_IN_DESCRIPTION = 5
SCORE_CITY_MATCH = 10
SCORE_IS_FREE = 5
SCORE_MAX = 100

# Score tiers for UI
SCORE_TIER_HIGH = 80  # green badge - "Don't miss"
SCORE_TIER_MEDIUM = 50  # neutral badge - "Worth considering"

# Sources to scrape
SOURCES = {
    "luma_copenhagen": {
        "enabled": True,
        "url": "https://lu.ma/copenhagen",
        "city_default": "Copenhagen",
    },
    "luma_aarhus": {
        "enabled": True,
        "url": "https://lu.ma/aarhus",
        "city_default": "Aarhus",
    },
}

# Output files
CSV_OUTPUT = "events.csv"
HTML_OUTPUT = "index.html"

# Description truncation
DESCRIPTION_MAX_LENGTH = 300
