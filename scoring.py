"""
Scoring, categorization & key company detection.
"""

import re

from config import (
    ICP_KEYWORDS, TECH_KEYWORDS, TARGET_CITIES, DANISH_ONLINE_KEYWORDS,
    FORMAT_RULES, TOPIC_RULES, TOPIC_SCORE_BONUS, FORMAT_SCORE_BONUS,
    KEY_COMPANIES, SCORE_KEY_COMPANY_BONUS,
    SCORE_ICP_IN_TITLE, SCORE_ICP_IN_DESCRIPTION,
    SCORE_TECH_IN_TITLE, SCORE_TECH_IN_DESCRIPTION,
    SCORE_CITY_MATCH, SCORE_IS_FREE, SCORE_MAX,
)


def _find_keywords(text: str, keywords: list[str]) -> list[str]:
    if not text:
        return []
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]


def categorize_format(title: str, description: str) -> str:
    text = f"{title} {description}".lower()
    for label, keywords in FORMAT_RULES:
        for kw in keywords:
            if kw.lower() in text:
                return label
    return "Other"


def categorize_topic(title: str, description: str) -> str:
    title_lower = (title or "").lower()
    desc_lower = (description or "").lower()

    for label, keywords in TOPIC_RULES:
        for kw in keywords:
            if kw.lower() in title_lower:
                return label
    for label, keywords in TOPIC_RULES:
        for kw in keywords:
            if kw.lower() in desc_lower:
                return label
    return "Other"


def extract_key_companies(title: str, description: str, organizer: str = "") -> list[str]:
    """Return key companies mentioned anywhere in title/description/organizer."""
    text = f"{title} {description} {organizer}"
    text_lower = text.lower()
    found = []
    for company in KEY_COMPANIES:
        if company.lower() in text_lower and company not in found:
            found.append(company)
    return found


# Names: simple heuristic — "Firstname Lastname, Firm" OR "by Firstname Lastname"
NAME_PATTERN = re.compile(
    r"\b([A-Z][a-z]{1,15})\s+([A-Z][a-z]{1,20}(?:sen|son|sson|berg|strøm|holm|lund|gaard|sted)?)\b"
)


def extract_speaker_names(description: str, key_companies_in_event: list[str]) -> list[str]:
    """Extract potential speaker names from description.

    High-precision heuristic: only name patterns that appear close to
    a known company (within ~60 chars) or after 'speaker:', 'with', 'by',
    'featuring'. Returns unique names, max 6.
    """
    if not description or len(description) < 20:
        return []

    found: list[str] = []
    text = description

    # Patterns like "Speaker: John Smith" / "speakers include John Smith and Jane Doe"
    cue_patterns = [
        r"(?:speakers?|featuring|with|keynote by|by|host(?:ed)? by|presented by)\s*:?\s*([A-Z][a-z]{1,15}\s+[A-Z][a-z]{1,20})",
    ]
    for p in cue_patterns:
        for m in re.finditer(p, text, re.IGNORECASE):
            name = m.group(1).strip()
            if _looks_like_name(name) and name not in found:
                found.append(name)

    # Names near a known company within a window
    for company in key_companies_in_event:
        for m in re.finditer(re.escape(company), text, re.IGNORECASE):
            start = max(0, m.start() - 60)
            end = min(len(text), m.end() + 60)
            window = text[start:end]
            for nm in NAME_PATTERN.finditer(window):
                candidate = nm.group(0)
                if _looks_like_name(candidate) and candidate not in found:
                    found.append(candidate)

    # Cap output
    return found[:6]


NAME_STOPWORDS = {
    "Copenhagen", "Denmark", "Nordic", "Fintech", "Mobile", "Digital", "Event",
    "Summit", "Conference", "Workshop", "Demo", "Open", "General", "Read",
    "Join", "Free", "Virtual", "Online", "Tech", "Innovation", "Startup",
}


def _looks_like_name(s: str) -> bool:
    parts = s.split()
    if len(parts) != 2:
        return False
    first, last = parts
    if first in NAME_STOPWORDS or last in NAME_STOPWORDS:
        return False
    if not (first[0].isupper() and last[0].isupper()):
        return False
    # Reject if the full string is a known company (case-insensitive)
    s_lower = s.lower()
    for c in KEY_COMPANIES:
        if c.lower() == s_lower:
            return False
    # Also reject if "last" word is a company-indicator noun
    company_nouns = {"Bank", "Group", "Inc", "Ltd", "Pension", "Insurance", "Tech",
                     "Solutions", "Networks", "Foundation", "Institute"}
    if last in company_nouns:
        return False
    return True


def score_event(event: dict) -> tuple[int, list[str], list[str]]:
    """Compute score, matched keywords, and key companies.

    Returns (score, matched_keywords, key_companies).
    """
    title = event.get("title", "") or ""
    description = event.get("description", "") or ""
    organizer = event.get("organizer", "") or ""
    city = (event.get("city", "") or "").lower()
    is_online = event.get("is_online", False)
    is_free = event.get("is_free", False)
    topic = event.get("topic", "Other")
    format_label = event.get("format", "Other")

    score = 0
    matched = set()

    icp_in_title = _find_keywords(title, ICP_KEYWORDS)
    icp_in_desc = _find_keywords(description, ICP_KEYWORDS)
    score += len(icp_in_title) * SCORE_ICP_IN_TITLE
    score += len(icp_in_desc) * SCORE_ICP_IN_DESCRIPTION
    matched.update(icp_in_title + icp_in_desc)

    tech_in_title = _find_keywords(title, TECH_KEYWORDS)
    tech_in_desc = _find_keywords(description, TECH_KEYWORDS)
    score += len(tech_in_title) * SCORE_TECH_IN_TITLE
    score += len(tech_in_desc) * SCORE_TECH_IN_DESCRIPTION
    matched.update(tech_in_title + tech_in_desc)

    if any(c in city for c in TARGET_CITIES):
        score += SCORE_CITY_MATCH
    elif is_online:
        combined = (title + " " + description).lower()
        if any(kw in combined for kw in DANISH_ONLINE_KEYWORDS):
            score += SCORE_CITY_MATCH

    if is_free:
        score += SCORE_IS_FREE

    score += TOPIC_SCORE_BONUS.get(topic, 0)
    score += FORMAT_SCORE_BONUS.get(format_label, 0)

    # Key company detection + bonus
    companies = extract_key_companies(title, description, organizer)
    score += len(companies) * SCORE_KEY_COMPANY_BONUS

    score = min(score, SCORE_MAX)
    return score, sorted(matched), companies
