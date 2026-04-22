"""
Scoring & categorization logic.
"""

from config import (
    ICP_KEYWORDS, TECH_KEYWORDS, TARGET_CITIES, DANISH_ONLINE_KEYWORDS,
    FORMAT_RULES, TOPIC_RULES, TOPIC_SCORE_BONUS, FORMAT_SCORE_BONUS,
    SCORE_ICP_IN_TITLE, SCORE_ICP_IN_DESCRIPTION,
    SCORE_TECH_IN_TITLE, SCORE_TECH_IN_DESCRIPTION,
    SCORE_CITY_MATCH, SCORE_IS_FREE, SCORE_MAX,
)


def _find_keywords(text: str, keywords: list[str]) -> list[str]:
    """Return keywords found in text (case-insensitive)."""
    if not text:
        return []
    text_lower = text.lower()
    hits = []
    for kw in keywords:
        if kw.lower() in text_lower:
            hits.append(kw)
    return hits


def categorize_format(title: str, description: str) -> str:
    """Return format label (Conference, Meetup, Workshop, etc.) or 'Other'."""
    text = f"{title} {description}".lower()
    for label, keywords in FORMAT_RULES:
        for kw in keywords:
            if kw.lower() in text:
                return label
    return "Other"


def categorize_topic(title: str, description: str) -> str:
    """Return topic label (Fintech, Retail, AI, etc.) or 'Other'.

    Title matches are weighted more heavily — if a keyword matches in title, it wins.
    """
    title_lower = (title or "").lower()
    desc_lower = (description or "").lower()

    # First pass: try to match in title
    for label, keywords in TOPIC_RULES:
        for kw in keywords:
            if kw.lower() in title_lower:
                return label

    # Second pass: match in description
    for label, keywords in TOPIC_RULES:
        for kw in keywords:
            if kw.lower() in desc_lower:
                return label

    return "Other"


def score_event(event: dict) -> tuple[int, list[str]]:
    """Compute score (0-100) and return matched keywords."""
    title = event.get("title", "") or ""
    description = event.get("description", "") or ""
    city = (event.get("city", "") or "").lower()
    is_online = event.get("is_online", False)
    is_free = event.get("is_free", False)
    topic = event.get("topic", "Other")
    format_label = event.get("format", "Other")

    score = 0
    matched = set()

    # ICP keywords
    icp_in_title = _find_keywords(title, ICP_KEYWORDS)
    icp_in_desc = _find_keywords(description, ICP_KEYWORDS)
    score += len(icp_in_title) * SCORE_ICP_IN_TITLE
    score += len(icp_in_desc) * SCORE_ICP_IN_DESCRIPTION
    matched.update(icp_in_title)
    matched.update(icp_in_desc)

    # Tech keywords
    tech_in_title = _find_keywords(title, TECH_KEYWORDS)
    tech_in_desc = _find_keywords(description, TECH_KEYWORDS)
    score += len(tech_in_title) * SCORE_TECH_IN_TITLE
    score += len(tech_in_desc) * SCORE_TECH_IN_DESCRIPTION
    matched.update(tech_in_title)
    matched.update(tech_in_desc)

    # City match
    if any(c in city for c in TARGET_CITIES):
        score += SCORE_CITY_MATCH
    elif is_online:
        combined = (title + " " + description).lower()
        if any(kw in combined for kw in DANISH_ONLINE_KEYWORDS):
            score += SCORE_CITY_MATCH

    # Free event bonus
    if is_free:
        score += SCORE_IS_FREE

    # Topic relevance bonus
    score += TOPIC_SCORE_BONUS.get(topic, 0)

    # Format bonus (Conferences > Meetups for business use cases)
    score += FORMAT_SCORE_BONUS.get(format_label, 0)

    # Cap
    score = min(score, SCORE_MAX)
    return score, sorted(matched)
