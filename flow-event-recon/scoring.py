"""
Scoring logic - assigns a 0-100 relevance score to each event based on keyword matches.
"""

from config import (
    ICP_KEYWORDS,
    TECH_KEYWORDS,
    TARGET_CITIES,
    DANISH_ONLINE_KEYWORDS,
    SCORE_ICP_IN_TITLE,
    SCORE_ICP_IN_DESCRIPTION,
    SCORE_TECH_IN_TITLE,
    SCORE_TECH_IN_DESCRIPTION,
    SCORE_CITY_MATCH,
    SCORE_IS_FREE,
    SCORE_MAX,
)


def _find_keywords(text: str, keywords: list[str]) -> list[str]:
    """Return the keywords found in the given text (case-insensitive).

    We match on substring because keywords like 'AI' should also match 'AI-powered'.
    """
    if not text:
        return []
    text_lower = text.lower()
    hits = []
    for kw in keywords:
        if kw.lower() in text_lower:
            hits.append(kw)
    return hits


def score_event(event: dict) -> tuple[int, list[str]]:
    """Compute score (0-100) and return matched keywords.

    Event dict is expected to contain: title, description, city, is_online, is_free.
    """
    title = event.get("title", "") or ""
    description = event.get("description", "") or ""
    city = (event.get("city", "") or "").lower()
    is_online = event.get("is_online", False)
    is_free = event.get("is_free", False)

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

    # City match (Danish city) OR online event mentioning Danish community
    if any(c in city for c in TARGET_CITIES):
        score += SCORE_CITY_MATCH
    elif is_online:
        combined = (title + " " + description).lower()
        if any(kw in combined for kw in DANISH_ONLINE_KEYWORDS):
            score += SCORE_CITY_MATCH

    # Free event bonus
    if is_free:
        score += SCORE_IS_FREE

    # Cap at max
    score = min(score, SCORE_MAX)

    return score, sorted(matched)
