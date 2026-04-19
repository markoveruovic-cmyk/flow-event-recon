"""
Reads events.csv and generates index.html - a Flow-branded dashboard.
Single file, no frameworks, fully offline.

Brand: Etnetera Flow (light mode)
  - Background: white
  - Primary accent: mint/emerald green (#3DBE7A)
  - Text: near-black
  - Typography: Montserrat
"""

from __future__ import annotations

import csv
import html
import json
from datetime import datetime
from pathlib import Path

from config import CSV_OUTPUT, HTML_OUTPUT, SCORE_TIER_HIGH, SCORE_TIER_MEDIUM


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Flow Event Recon</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  :root {
    /* Brand colors — Etnetera Flow */
    --bg: #FFFFFF;
    --bg-soft: #F7F8F9;
    --bg-hover: #F0FAF4;
    --border: #E5E7EB;
    --border-soft: #F0F1F3;
    --text: #0A0A0A;
    --text-muted: #6B7280;
    --text-dim: #9CA3AF;

    --accent: #3DBE7A;          /* Flow green */
    --accent-hover: #34A86A;
    --accent-soft: #E8F7EF;
    --accent-tint: #F3FBF6;

    --score-high: #3DBE7A;
    --score-mid: #0A0A0A;
    --score-low: #9CA3AF;

    --radius-pill: 999px;
    --radius-card: 16px;
  }

  * { box-sizing: border-box; }

  html, body {
    margin: 0;
    padding: 0;
    background: var(--bg);
    color: var(--text);
    font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, sans-serif;
    font-weight: 400;
    line-height: 1.55;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  .container {
    max-width: 1240px;
    margin: 0 auto;
    padding: 40px 40px 120px;
  }

  /* ── Top bar ─────────────────────────────────────────── */
  .topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 32px;
    margin-bottom: 72px;
    border-bottom: 1px solid var(--border-soft);
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 12px;
    font-weight: 600;
    font-size: 15px;
    color: var(--text);
    letter-spacing: -0.01em;
  }

  .logo-mark {
    position: relative;
    width: 32px;
    height: 32px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
  .logo-mark span {
    font-weight: 800;
    font-size: 26px;
    line-height: 1;
    color: var(--text);
  }

  .logo-title { display: flex; flex-direction: column; line-height: 1.15; }
  .logo-title .product {
    color: var(--text);
    font-weight: 700;
    font-size: 16px;
    letter-spacing: -0.015em;
  }
  .logo-title .by {
    color: var(--text-muted);
    font-weight: 500;
    font-size: 11px;
    letter-spacing: 0.01em;
    margin-top: 2px;
  }
  .logo-title .by .etnetera { color: var(--text-muted); font-weight: 500; }
  .logo-title .by .flow { color: var(--accent); font-weight: 600; }

  .topbar-right {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 13px;
    color: var(--text-muted);
    font-weight: 500;
  }
  .topbar-right .tag {
    padding: 6px 12px;
    background: var(--bg-soft);
    border-radius: var(--radius-pill);
    font-size: 12px;
    letter-spacing: 0.01em;
  }
  .topbar-right strong { color: var(--text); font-weight: 600; }

  /* ── Hero ────────────────────────────────────────────── */
  header { margin-bottom: 56px; }

  h1 {
    font-family: 'Montserrat', sans-serif;
    font-size: clamp(44px, 7vw, 88px);
    font-weight: 700;
    line-height: 1.05;
    letter-spacing: -0.025em;
    color: var(--accent);
    margin: 0 0 28px;
    max-width: 16ch;
  }
  h1 .black {
    color: var(--text);
  }

  .subtitle {
    max-width: 640px;
    font-size: 17px;
    color: var(--text-muted);
    line-height: 1.6;
    font-weight: 400;
    margin-bottom: 0;
  }

  /* ── Controls bar ────────────────────────────────────── */
  .controls {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
    padding: 24px 0;
    border-top: 1px solid var(--border-soft);
    border-bottom: 1px solid var(--border-soft);
    margin-bottom: 56px;
  }

  .filter-group {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
  }

  .filter-label {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-muted);
    margin-right: 6px;
  }

  .pill {
    display: inline-flex;
    align-items: center;
    padding: 7px 14px;
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text-muted);
    font-family: 'Montserrat', sans-serif;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
    border-radius: var(--radius-pill);
    letter-spacing: -0.005em;
  }

  .pill:hover {
    border-color: var(--text);
    color: var(--text);
  }

  .pill.active {
    background: var(--text);
    border-color: var(--text);
    color: #fff;
    font-weight: 600;
  }

  .score-slider-wrap {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-left: auto;
  }

  input[type="range"] {
    -webkit-appearance: none;
    appearance: none;
    width: 140px;
    height: 4px;
    background: var(--border);
    border-radius: 999px;
    outline: none;
  }
  input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 16px;
    height: 16px;
    background: var(--accent);
    border-radius: 50%;
    cursor: pointer;
    border: 3px solid var(--bg);
    box-shadow: 0 0 0 1px var(--accent);
  }
  input[type="range"]::-moz-range-thumb {
    width: 16px;
    height: 16px;
    background: var(--accent);
    border-radius: 50%;
    cursor: pointer;
    border: 3px solid var(--bg);
    box-shadow: 0 0 0 1px var(--accent);
  }
  .score-value {
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
    min-width: 30px;
    text-align: right;
  }

  .download-btn {
    padding: 10px 22px;
    background: var(--accent);
    border: none;
    color: #fff;
    font-family: 'Montserrat', sans-serif;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: -0.005em;
    cursor: pointer;
    transition: background 0.15s ease, transform 0.15s ease;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    border-radius: var(--radius-pill);
  }
  .download-btn:hover {
    background: var(--accent-hover);
    transform: translateY(-1px);
  }
  .download-btn svg { width: 14px; height: 14px; }

  /* ── Section headings ────────────────────────────────── */
  .section-header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    padding-bottom: 16px;
    margin: 56px 0 0;
    border-bottom: 1px solid var(--border);
  }
  .section-header:first-of-type { margin-top: 0; }

  .section-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--text);
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 0;
  }

  .section-title .marker {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: var(--accent);
    border-radius: 50%;
  }
  .section-title.muted { color: var(--text-muted); }
  .section-title.muted .marker { background: var(--text-dim); }

  .section-count {
    font-size: 12px;
    color: var(--text-muted);
    font-weight: 500;
  }

  /* ── Event row ───────────────────────────────────────── */
  .event {
    display: grid;
    grid-template-columns: 88px 1fr auto;
    gap: 28px;
    padding: 28px 0;
    border-bottom: 1px solid var(--border-soft);
    transition: background 0.2s ease, padding 0.2s ease;
    position: relative;
  }

  .event:hover {
    background: var(--accent-tint);
    padding-left: 20px;
    padding-right: 20px;
  }

  .event::before {
    content: "";
    position: absolute;
    left: 0;
    top: 12px;
    bottom: 12px;
    width: 3px;
    background: var(--accent);
    border-radius: 0 3px 3px 0;
    transform: scaleY(0);
    transform-origin: center;
    transition: transform 0.25s ease;
  }
  .event:hover::before { transform: scaleY(1); }

  .event-date {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding-top: 8px;
  }
  .event-date .day {
    display: block;
    font-size: 30px;
    color: var(--text);
    margin-bottom: 2px;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1;
  }

  .event-main { min-width: 0; }

  .event-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--text);
    text-decoration: none;
    line-height: 1.25;
    display: inline-block;
    margin-bottom: 10px;
    transition: color 0.15s ease;
  }
  .event-title:hover { color: var(--accent); }
  .event-title .arrow {
    display: inline-block;
    margin-left: 4px;
    font-size: 16px;
    color: var(--text-muted);
    transition: color 0.15s ease, transform 0.15s ease;
  }
  .event-title:hover .arrow {
    color: var(--accent);
    transform: translate(2px, -2px);
  }

  .event-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    font-size: 13px;
    color: var(--text-muted);
    font-weight: 500;
    margin-bottom: 12px;
  }
  .event-meta .sep { color: var(--text-dim); }
  .event-meta .free {
    color: var(--accent);
    background: var(--accent-soft);
    padding: 3px 10px;
    border-radius: var(--radius-pill);
    font-weight: 600;
    font-size: 12px;
    letter-spacing: 0.01em;
  }

  .event-description {
    color: var(--text-muted);
    font-size: 14px;
    line-height: 1.55;
    margin-bottom: 14px;
    max-width: 760px;
  }

  .event-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .tag {
    font-size: 11px;
    font-weight: 500;
    padding: 4px 10px;
    background: var(--bg-soft);
    border: 1px solid var(--border-soft);
    color: var(--text-muted);
    border-radius: var(--radius-pill);
  }

  /* ── Score badge ─────────────────────────────────────── */
  .score {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    justify-content: flex-start;
    padding-top: 6px;
    min-width: 80px;
  }
  .score-num {
    font-family: 'Montserrat', sans-serif;
    font-size: 44px;
    font-weight: 700;
    line-height: 1;
    letter-spacing: -0.04em;
    color: var(--score-mid);
  }
  .score-label {
    font-size: 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-top: 6px;
    font-weight: 600;
  }
  .score.tier-high .score-num { color: var(--score-high); }
  .score.tier-high .score-label { color: var(--accent); }
  .score.tier-low .score-num { color: var(--score-low); }

  /* ── Empty state ─────────────────────────────────────── */
  .empty {
    text-align: center;
    padding: 80px 0;
    color: var(--text-muted);
    font-size: 14px;
    background: var(--bg-soft);
    border-radius: var(--radius-card);
    margin-top: 32px;
  }

  /* ── Footer ──────────────────────────────────────────── */
  footer {
    margin-top: 96px;
    padding-top: 32px;
    border-top: 1px solid var(--border-soft);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: var(--text-muted);
    font-weight: 500;
  }
  footer a {
    color: var(--text-muted);
    text-decoration: none;
    transition: color 0.15s ease;
  }
  footer a:hover { color: var(--accent); }

  /* ── Responsive ──────────────────────────────────────── */
  @media (max-width: 720px) {
    .container { padding: 28px 20px 80px; }
    .topbar { flex-direction: column; gap: 20px; align-items: flex-start; margin-bottom: 40px; padding-bottom: 24px; }
    header { margin-bottom: 40px; }
    h1 { font-size: 42px; }
    .subtitle { font-size: 15px; }
    .controls { flex-direction: column; align-items: stretch; gap: 16px; padding: 20px 0; }
    .score-slider-wrap { margin-left: 0; }
    .download-btn { justify-content: center; }
    .event { grid-template-columns: 1fr auto; gap: 16px; padding: 22px 0; }
    .event:hover { padding-left: 12px; padding-right: 12px; }
    .event-date {
      grid-column: 1 / -1;
      display: flex;
      gap: 8px;
      align-items: baseline;
      padding-top: 0;
    }
    .event-date .day { display: inline; font-size: 16px; }
    .score-num { font-size: 32px; }
    .event-title { font-size: 18px; }
  }
</style>
</head>
<body>
  <div class="container">
    <div class="topbar">
      <div class="logo">
        <div class="logo-mark"><span>&amp;</span></div>
        <div class="logo-title">
          <span class="product">Flow Event Recon</span>
          <span class="by">by <span class="etnetera">etnetera</span> <span class="flow">flow</span></span>
        </div>
      </div>
      <div class="topbar-right">
        <span class="tag">Updated <strong>__UPDATED__</strong></span>
        <span class="tag"><strong>__TOTAL__</strong> events</span>
      </div>
    </div>

    <header>
      <h1>Events<br><span class="black">worth showing up.</span></h1>
      <p class="subtitle">
        Automated watch on tech &amp; business events across Denmark — filtered by ICPs,
        scored by relevance, ready to export when you need it.
      </p>
    </header>

    <div class="controls">
      <div class="filter-group">
        <span class="filter-label">City</span>
        <button class="pill active" data-filter="city" data-value="all">All</button>
__CITY_PILLS__
      </div>
      <div class="filter-group">
        <span class="filter-label">Cost</span>
        <button class="pill active" data-filter="cost" data-value="all">All</button>
        <button class="pill" data-filter="cost" data-value="free">Free only</button>
      </div>
      <div class="score-slider-wrap">
        <span class="filter-label">Min. score</span>
        <input type="range" id="score-range" min="0" max="100" step="5" value="0" />
        <span class="score-value" id="score-value">0</span>
      </div>
      <a class="download-btn" href="events.csv" download>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M12 3v12m0 0l-4-4m4 4l4-4M5 21h14" />
        </svg>
        Download CSV
      </a>
    </div>

    <main id="events-container"></main>

    <footer>
      <span>Flow Event Recon — v0.1</span>
      <span>Source: Luma · Keywords editable in config.py</span>
    </footer>
  </div>

<script>
  const EVENTS = __EVENTS_JSON__;
  const SCORE_HIGH = __SCORE_HIGH__;
  const SCORE_MEDIUM = __SCORE_MEDIUM__;

  const state = {
    city: "all",
    cost: "all",
    minScore: 0,
  };

  function tierClass(score) {
    if (score >= SCORE_HIGH) return "tier-high";
    if (score >= SCORE_MEDIUM) return "";
    return "tier-low";
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function parseDateParts(d) {
    const parts = (d || "").split(" ");
    return {
      day: parts[0] || "—",
      month: (parts[1] || "").toUpperCase(),
      year: parts[2] || "",
    };
  }

  function renderEvent(e) {
    const tier = tierClass(e.score);
    const parts = parseDateParts(e.date);
    const tags = (e.keywords_match || "")
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);

    const tagHtml = tags
      .slice(0, 6)
      .map((t) => `<span class="tag">${escapeHtml(t)}</span>`)
      .join("");
    const moreTags = tags.length > 6 ? `<span class="tag">+${tags.length - 6}</span>` : "";

    const isFree = (e.price || "").toLowerCase() === "free";
    const priceHtml = isFree
      ? `<span class="free">Free</span>`
      : `<span>${escapeHtml(e.price)}</span>`;

    return `
      <article class="event">
        <div class="event-date">
          <span class="day">${escapeHtml(parts.day)}</span>
          ${escapeHtml(parts.month)} ${escapeHtml(parts.year)}
        </div>
        <div class="event-main">
          <a class="event-title" href="${escapeHtml(e.url)}" target="_blank" rel="noopener">${escapeHtml(e.title)}<span class="arrow">↗</span></a>
          <div class="event-meta">
            <span>${escapeHtml(e.city || "—")}</span>
            <span class="sep">·</span>
            <span>${escapeHtml(e.mode || "")}</span>
            <span class="sep">·</span>
            ${priceHtml}
          </div>
          ${e.description_short ? `<p class="event-description">${escapeHtml(e.description_short)}</p>` : ""}
          ${tags.length ? `<div class="event-tags">${tagHtml}${moreTags}</div>` : ""}
        </div>
        <div class="score ${tier}">
          <span class="score-num">${e.score}</span>
          <span class="score-label">Score</span>
        </div>
      </article>
    `;
  }

  function render() {
    const filtered = EVENTS.filter((e) => {
      if (state.city !== "all" && (e.city || "").toLowerCase() !== state.city.toLowerCase()) return false;
      if (state.cost === "free" && (e.price || "").toLowerCase() !== "free") return false;
      if (e.score < state.minScore) return false;
      return true;
    });

    const topEvents = filtered.filter((e) => e.score >= SCORE_HIGH);
    const midEvents = filtered.filter((e) => e.score >= SCORE_MEDIUM && e.score < SCORE_HIGH);
    const lowEvents = filtered.filter((e) => e.score < SCORE_MEDIUM);

    const container = document.getElementById("events-container");
    const sections = [];

    if (topEvents.length) {
      sections.push(`
        <div class="section-header">
          <h2 class="section-title"><span class="marker"></span>Don't miss</h2>
          <span class="section-count">${topEvents.length} event${topEvents.length === 1 ? "" : "s"} · score ≥ ${SCORE_HIGH}</span>
        </div>
        ${topEvents.map(renderEvent).join("")}
      `);
    }

    if (midEvents.length) {
      sections.push(`
        <div class="section-header">
          <h2 class="section-title"><span class="marker"></span>Worth considering</h2>
          <span class="section-count">${midEvents.length} event${midEvents.length === 1 ? "" : "s"} · score ${SCORE_MEDIUM}–${SCORE_HIGH - 1}</span>
        </div>
        ${midEvents.map(renderEvent).join("")}
      `);
    }

    if (lowEvents.length) {
      sections.push(`
        <div class="section-header">
          <h2 class="section-title muted"><span class="marker"></span>Low relevance</h2>
          <span class="section-count">${lowEvents.length} event${lowEvents.length === 1 ? "" : "s"} · score &lt; ${SCORE_MEDIUM}</span>
        </div>
        ${lowEvents.map(renderEvent).join("")}
      `);
    }

    if (!sections.length) {
      container.innerHTML = `<div class="empty">No events match these filters.</div>`;
    } else {
      container.innerHTML = sections.join("");
    }
  }

  document.querySelectorAll(".pill").forEach((pill) => {
    pill.addEventListener("click", () => {
      const filter = pill.dataset.filter;
      const value = pill.dataset.value;
      state[filter] = value;

      document.querySelectorAll(`.pill[data-filter="${filter}"]`).forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");

      render();
    });
  });

  const range = document.getElementById("score-range");
  const rangeValue = document.getElementById("score-value");
  range.addEventListener("input", () => {
    state.minScore = Number(range.value);
    rangeValue.textContent = range.value;
    render();
  });

  render();
</script>
</body>
</html>
"""


def _load_events() -> list[dict]:
    csv_path = Path(CSV_OUTPUT)
    if not csv_path.exists():
        return []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        events = []
        for row in reader:
            try:
                row["score"] = int(row.get("score", 0))
            except ValueError:
                row["score"] = 0
            events.append(row)
    return sorted(events, key=lambda e: e["score"], reverse=True)


def _city_pills(events: list[dict]) -> str:
    cities = sorted({e.get("city", "") for e in events if e.get("city")})
    pills = []
    for c in cities:
        safe = html.escape(c)
        pills.append(
            f'        <button class="pill" data-filter="city" data-value="{safe}">{safe}</button>'
        )
    return "\n".join(pills)


def build_dashboard() -> None:
    events = _load_events()

    html_str = HTML_TEMPLATE
    html_str = html_str.replace("__EVENTS_JSON__", json.dumps(events, ensure_ascii=False))
    html_str = html_str.replace("__TOTAL__", str(len(events)))
    html_str = html_str.replace("__UPDATED__", datetime.now().strftime("%d %b %Y"))
    html_str = html_str.replace("__SCORE_HIGH__", str(SCORE_TIER_HIGH))
    html_str = html_str.replace("__SCORE_MEDIUM__", str(SCORE_TIER_MEDIUM))
    html_str = html_str.replace("__CITY_PILLS__", _city_pills(events))

    with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_str)

    print(f"✓ Generated {HTML_OUTPUT}")


if __name__ == "__main__":
    build_dashboard()
