"""
Flow Event Recon v0.4 configuration.
Upravuj tady klíčová slova, kategorie, zdroje a sledované firmy.
"""

# ─────────────────────────────────────────────────────────────
# KEYWORDS
# ─────────────────────────────────────────────────────────────

ICP_KEYWORDS = [
    "retail", "banking", "fintech", "e-commerce", "ecommerce", "e-com",
    "insurance", "BFSI", "digital banking", "payments", "open banking",
    "neobank", "wealth", "asset management", "capital markets", "forsikring",
    "pension", "handel",
]

TECH_KEYWORDS = [
    "mobile app", "mobile development", "iOS", "Android",
    "UX", "UI", "product design", "design system",
    "AI", "AI agents", "AI assistants", "GenAI",
    "multiplatform", "kotlin multiplatform", "flutter", "react native",
    "app store optimization", "ASO",
    "customer experience", "CX",
]

TARGET_CITIES = [
    "copenhagen", "kobenhavn", "københavn", "aarhus", "odense", "aalborg",
    "bella center", "amsterdam",
]

DANISH_ONLINE_KEYWORDS = ["denmark", "danish", "nordic", "dansk", "copenhagen"]

# ─────────────────────────────────────────────────────────────
# KEY COMPANIES — sledujeme, zda se objevují jako speakers/partners
# Tyhle firmy mají B2C appky nebo by je mohli chtít.
# ─────────────────────────────────────────────────────────────

KEY_COMPANIES = [
    # Banking & Finance
    "Danske Bank", "Nordea", "Nykredit", "Jyske Bank", "Spar Nord", "Sydbank",
    "Arbejdernes Landsbank", "Saxo Bank", "Lunar", "Pleo", "Vivino",
    # Insurance
    "Tryg", "Topdanmark", "Codan", "Alm. Brand", "If Forsikring", "PFA",
    "Velliv", "AP Pension",
    # Retail & E-commerce
    "Matas", "Coop", "Netto", "Bilka", "Salling Group", "Rossmann",
    "Magasin", "Zalando", "Dansk Supermarked", "Rema 1000", "Føtex",
    "Silvan", "Jem & Fix", "Ilva",
    # Automotive
    "Škoda", "Skoda", "BMW", "Volkswagen", "Audi", "Toyota", "Volvo",
    # Telco
    "TDC", "Telia", "Telenor", "3 Denmark", "Stofa",
    # Airlines / Travel
    "SAS", "Norwegian",
    # Energy & Utilities
    "Ørsted", "Orsted", "DONG Energy", "Norlys",
    # Food delivery / mobility
    "Just Eat", "Wolt", "Too Good To Go", "Donkey Republic",
    # Others with strong app presence
    "Maersk", "Novo Nordisk", "Vestas", "LEGO", "Carlsberg", "Ecco",
    "Pandora", "Bang & Olufsen",
]

# ─────────────────────────────────────────────────────────────
# CATEGORIZATION
# ─────────────────────────────────────────────────────────────

FORMAT_RULES = [
    ("Demo Day",   ["demo day", "pitch day", "showcase"]),
    ("Summit",     ["summit"]),
    ("Conference", ["conference", "kongres", "konference"]),
    ("Workshop",   ["workshop", "masterclass", "bootcamp", "training"]),
    ("Webinar",    ["webinar", "online session", "virtual session"]),
    ("Meetup",     ["meetup", "networking", "meet-up", "meet up", "breakfast", "lunch session"]),
    ("Delegation", ["delegation"]),
]

TOPIC_RULES = [
    ("Fintech & Banking",
     ["fintech", "banking", "bank ", "payments", "open banking", "digital finance",
      "wealth", "neobank", "money20", "aml", "regtech", "capital markets"]),
    ("Insurance & BFSI",
     ["insurance", "insurtech", "bfsi", "risk management", "forsikring", "pension"]),
    ("Retail & E-commerce",
     ["retail", "e-commerce", "ecommerce", "commerce", "customer experience",
      "conversion", "cx", "merchandising", "handel"]),
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

SCORE_TIER_HIGH = 80
SCORE_TIER_MEDIUM = 50

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

# Bonus per key company mentioned (speaker/partner detection)
SCORE_KEY_COMPANY_BONUS = 5

# ─────────────────────────────────────────────────────────────
# SOURCES — v0.4 expanded to 12+
# ─────────────────────────────────────────────────────────────

SOURCES = {
    # Tier 1: proven & bohaté
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

    # Eventbrite — 4 různé search URL
    "eventbrite_business_cph": {
        "enabled": True,
        "type": "eventbrite",
        "url": "https://www.eventbrite.dk/d/denmark--copenhagen/business--events/",
        "city_default": "Copenhagen",
    },
    "eventbrite_tech_cph": {
        "enabled": True,
        "type": "eventbrite",
        "url": "https://www.eventbrite.dk/d/denmark--copenhagen/science-and-tech--events/",
        "city_default": "Copenhagen",
    },
    "eventbrite_retail_cph": {
        "enabled": True,
        "type": "eventbrite",
        "url": "https://www.eventbrite.dk/d/denmark--copenhagen/retail/",
        "city_default": "Copenhagen",
    },
    "eventbrite_fintech_cph": {
        "enabled": True,
        "type": "eventbrite",
        "url": "https://www.eventbrite.dk/d/denmark--copenhagen/fintech/",
        "city_default": "Copenhagen",
    },

    # Tier 2: nové specializované zdroje (uvidíme, které projdou)
    "innovation_district_cph": {
        "enabled": True,
        "type": "generic_html",
        "url": "https://innovationdistrictcopenhagen.dk/events/",
        "city_default": "Copenhagen",
        "event_selector": "article, .event-card, .event-item, [class*='event']",
        "date_selector": ".date, time, [class*='date']",
        "title_selector": "h1, h2, h3, .title, [class*='title']",
        "link_selector": "a",
    },
    "it_branchen": {
        "enabled": True,
        "type": "generic_html",
        "url": "https://itb.dk/arrangementer/",
        "city_default": "Copenhagen",
        "event_selector": "article, .event, .arrangement, li",
        "date_selector": ".date, time, [class*='date']",
        "title_selector": "h1, h2, h3, .title",
        "link_selector": "a",
    },
    "fdih": {
        "enabled": True,
        "type": "generic_html",
        "url": "https://www.fdih.dk/arrangementer-kurser/kommende",
        "city_default": "Copenhagen",
        "event_selector": "article, .event, .arrangement, li.list-item",
        "date_selector": ".date, time, [class*='date']",
        "title_selector": "h1, h2, h3, .title",
        "link_selector": "a",
    },

    # Manual seed — user-curated, merged via localStorage in UI
    # (no scraper needed, handled entirely in frontend)
}

CSV_OUTPUT = "events.csv"
HTML_OUTPUT = "index.html"

DESCRIPTION_MAX_LENGTH = 300
