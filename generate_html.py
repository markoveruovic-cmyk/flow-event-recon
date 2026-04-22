"""
Flow Event Recon v0.3 — Sales-focused dashboard.

Features:
- NEW badge for first-seen events
- Add to Calendar (.ics download)
- ★ Save events (localStorage, per-user)
- 📝 Sales notes per event (localStorage)
- Date range filter
- "My shortlist" tab
- "Past events" tab (90-day archive)
- Print-friendly weekly digest view
- Organizer filter
- Stats strip
- Topic / Format / City filters
- Export / Import saves & notes
"""

from __future__ import annotations

import csv
import html
import json
from datetime import datetime
from pathlib import Path

from config import CSV_OUTPUT, HTML_OUTPUT, SCORE_TIER_HIGH, SCORE_TIER_MEDIUM

PAST_EVENTS_CSV = "past_events.csv"


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
    --bg: #FFFFFF;
    --bg-soft: #F7F8F9;
    --bg-hover: #F0FAF4;
    --border: #E5E7EB;
    --border-soft: #F0F1F3;
    --text: #0A0A0A;
    --text-muted: #6B7280;
    --text-dim: #9CA3AF;

    --accent: #3DBE7A;
    --accent-hover: #34A86A;
    --accent-soft: #E8F7EF;
    --accent-tint: #F3FBF6;

    --score-high: #3DBE7A;
    --score-mid: #0A0A0A;
    --score-low: #9CA3AF;

    --amber: #F59E0B;
    --amber-soft: #FEF3C7;

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

  .container { max-width: 1240px; margin: 0 auto; padding: 40px 40px 120px; }

  /* ── Top bar ─────────────────────────────────────────── */
  .topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 32px;
    margin-bottom: 56px;
    border-bottom: 1px solid var(--border-soft);
    gap: 24px;
    flex-wrap: wrap;
  }

  .logo { display: flex; align-items: center; gap: 12px; font-weight: 600; font-size: 15px; color: var(--text); }
  .logo-mark { position: relative; width: 32px; height: 32px; display: inline-flex; align-items: center; justify-content: center; }
  .logo-mark span { font-weight: 800; font-size: 26px; line-height: 1; color: var(--text); }
  .logo-title { display: flex; flex-direction: column; line-height: 1.15; }
  .logo-title .product { color: var(--text); font-weight: 700; font-size: 16px; letter-spacing: -0.015em; }
  .logo-title .by { color: var(--text-muted); font-weight: 500; font-size: 11px; margin-top: 2px; }
  .logo-title .by .flow { color: var(--accent); font-weight: 600; }

  .topbar-right { display: flex; align-items: center; gap: 10px; font-size: 13px; color: var(--text-muted); font-weight: 500; flex-wrap: wrap; }
  .topbar-right .tag { padding: 6px 12px; background: var(--bg-soft); border-radius: var(--radius-pill); font-size: 12px; }
  .topbar-right strong { color: var(--text); font-weight: 600; }

  .icon-btn {
    width: 32px; height: 32px;
    border-radius: 50%;
    background: var(--bg-soft);
    border: 1px solid var(--border);
    color: var(--text-muted);
    display: inline-flex; align-items: center; justify-content: center;
    cursor: pointer;
    transition: all 0.15s ease;
    font-size: 14px;
  }
  .icon-btn:hover { background: var(--accent-soft); color: var(--accent-hover); border-color: var(--accent); }

  /* ── Hero ────────────────────────────────────────────── */
  header { margin-bottom: 48px; }
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
  h1 .black { color: var(--text); }
  .subtitle { max-width: 640px; font-size: 17px; color: var(--text-muted); line-height: 1.6; margin-bottom: 0; }

  /* ── Tabs ────────────────────────────────────────────── */
  .tabs {
    display: flex;
    gap: 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 32px;
  }
  .tab {
    padding: 14px 22px;
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    color: var(--text-muted);
    font-family: 'Montserrat', sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: -1px;
  }
  .tab:hover { color: var(--text); }
  .tab.active { color: var(--text); border-bottom-color: var(--accent); }
  .tab .count {
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    background: var(--bg-soft);
    border-radius: var(--radius-pill);
    color: var(--text-muted);
  }
  .tab.active .count { background: var(--accent-soft); color: var(--accent-hover); }

  /* ── Controls bar ────────────────────────────────────── */
  .controls {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 14px;
    padding: 20px 0;
    border-bottom: 1px solid var(--border-soft);
    margin-bottom: 32px;
  }

  .filter-group { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .filter-label { font-size: 12px; font-weight: 600; color: var(--text-muted); margin-right: 4px; }

  .select-wrap { position: relative; display: inline-flex; }
  select {
    appearance: none; -webkit-appearance: none; -moz-appearance: none;
    padding: 7px 32px 7px 14px;
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text);
    font-family: 'Montserrat', sans-serif;
    font-size: 13px; font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
    border-radius: var(--radius-pill);
    outline: none;
    max-width: 200px;
    text-overflow: ellipsis;
  }
  select:hover { border-color: var(--text); }
  select:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
  .select-wrap::after {
    content: ""; position: absolute; right: 12px; top: 50%;
    width: 7px; height: 7px;
    border-right: 2px solid var(--text-muted);
    border-bottom: 2px solid var(--text-muted);
    transform: translateY(-70%) rotate(45deg);
    pointer-events: none;
  }
  select.active { background: var(--text); color: #fff; border-color: var(--text); }
  .select-wrap:has(select.active)::after { border-color: #fff; }

  .pill {
    display: inline-flex; align-items: center;
    padding: 7px 14px;
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text-muted);
    font-family: 'Montserrat', sans-serif;
    font-size: 13px; font-weight: 500;
    cursor: pointer; transition: all 0.15s ease;
    border-radius: var(--radius-pill);
  }
  .pill:hover { border-color: var(--text); color: var(--text); }
  .pill.active { background: var(--text); border-color: var(--text); color: #fff; font-weight: 600; }

  .score-slider-wrap { display: flex; align-items: center; gap: 12px; }
  input[type="range"] { -webkit-appearance: none; appearance: none; width: 120px; height: 4px; background: var(--border); border-radius: 999px; outline: none; }
  input[type="range"]::-webkit-slider-thumb { -webkit-appearance: none; appearance: none; width: 16px; height: 16px; background: var(--accent); border-radius: 50%; cursor: pointer; border: 3px solid var(--bg); box-shadow: 0 0 0 1px var(--accent); }
  input[type="range"]::-moz-range-thumb { width: 16px; height: 16px; background: var(--accent); border-radius: 50%; cursor: pointer; border: 3px solid var(--bg); box-shadow: 0 0 0 1px var(--accent); }
  .score-value { font-size: 13px; font-weight: 600; color: var(--text); min-width: 30px; text-align: right; }

  .controls-right { margin-left: auto; display: flex; gap: 8px; align-items: center; }

  .btn {
    padding: 10px 18px;
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text);
    font-family: 'Montserrat', sans-serif;
    font-size: 13px; font-weight: 600;
    cursor: pointer; transition: all 0.15s ease;
    border-radius: var(--radius-pill);
    display: inline-flex; align-items: center; gap: 8px;
    text-decoration: none;
  }
  .btn:hover { background: var(--bg-soft); border-color: var(--text); }
  .btn svg { width: 14px; height: 14px; }

  .btn-primary {
    background: var(--accent);
    color: #fff;
    border-color: var(--accent);
  }
  .btn-primary:hover { background: var(--accent-hover); border-color: var(--accent-hover); }

  /* ── Stats strip ─────────────────────────────────────── */
  .stats { display: flex; gap: 44px; padding: 0 0 24px; margin-bottom: 24px; border-bottom: 1px solid var(--border-soft); flex-wrap: wrap; }
  .stat-item { display: flex; flex-direction: column; }
  .stat-num { font-size: 32px; font-weight: 700; color: var(--text); letter-spacing: -0.03em; line-height: 1; }
  .stat-num.accent { color: var(--accent); }
  .stat-num.amber { color: var(--amber); }
  .stat-label { font-size: 11px; color: var(--text-muted); font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 6px; }

  /* ── Section headings ────────────────────────────────── */
  .section-header {
    display: flex; align-items: baseline; justify-content: space-between;
    padding-bottom: 16px; margin: 48px 0 0;
    border-bottom: 1px solid var(--border);
  }
  .section-header:first-of-type { margin-top: 0; }
  .section-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 13px; font-weight: 700;
    letter-spacing: 0.04em; text-transform: uppercase;
    color: var(--text);
    display: flex; align-items: center; gap: 10px; margin: 0;
  }
  .section-title .marker { display: inline-block; width: 8px; height: 8px; background: var(--accent); border-radius: 50%; }
  .section-title.muted { color: var(--text-muted); }
  .section-title.muted .marker { background: var(--text-dim); }
  .section-count { font-size: 12px; color: var(--text-muted); font-weight: 500; }

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
    content: ""; position: absolute; left: 0; top: 12px; bottom: 12px;
    width: 3px; background: var(--accent); border-radius: 0 3px 3px 0;
    transform: scaleY(0); transform-origin: center;
    transition: transform 0.25s ease;
  }
  .event:hover::before { transform: scaleY(1); }

  .event-date { font-size: 12px; font-weight: 500; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; padding-top: 8px; }
  .event-date .day { display: block; font-size: 30px; color: var(--text); margin-bottom: 2px; font-weight: 700; letter-spacing: -0.02em; line-height: 1; }

  .event-main { min-width: 0; }

  .event-badges { display: flex; gap: 6px; margin-bottom: 10px; flex-wrap: wrap; align-items: center; }
  .badge {
    font-size: 10px; font-weight: 600;
    padding: 3px 10px;
    border-radius: var(--radius-pill);
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }
  .badge-format { background: var(--text); color: #fff; }
  .badge-topic { background: var(--accent-soft); color: var(--accent-hover); }
  .badge-new {
    background: var(--amber);
    color: #fff;
    padding: 3px 10px;
    animation: pulse 2s ease-in-out infinite;
  }
  @keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4); }
    50% { box-shadow: 0 0 0 6px rgba(245, 158, 11, 0); }
  }

  .event-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 22px; font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--text);
    text-decoration: none;
    line-height: 1.25;
    display: inline-block;
    margin-bottom: 10px;
    transition: color 0.15s ease;
  }
  .event-title:hover { color: var(--accent); }
  .event-title .arrow { display: inline-block; margin-left: 4px; font-size: 16px; color: var(--text-muted); transition: color 0.15s ease, transform 0.15s ease; }
  .event-title:hover .arrow { color: var(--accent); transform: translate(2px, -2px); }

  .event-meta { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; font-size: 13px; color: var(--text-muted); font-weight: 500; margin-bottom: 12px; }
  .event-meta .sep { color: var(--text-dim); }
  .event-meta .free { color: var(--accent-hover); background: var(--accent-soft); padding: 3px 10px; border-radius: var(--radius-pill); font-weight: 600; font-size: 12px; }
  .event-meta .organizer-link { color: var(--text-muted); cursor: pointer; text-decoration: underline; text-decoration-color: var(--border); }
  .event-meta .organizer-link:hover { color: var(--accent-hover); text-decoration-color: var(--accent); }

  .event-description { color: var(--text-muted); font-size: 14px; line-height: 1.55; margin-bottom: 14px; max-width: 760px; }

  .event-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
  .tag { font-size: 11px; font-weight: 500; padding: 4px 10px; background: var(--bg-soft); border: 1px solid var(--border-soft); color: var(--text-muted); border-radius: var(--radius-pill); }

  .event-actions {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
  }
  .action-btn {
    font-size: 12px;
    font-weight: 500;
    padding: 6px 12px;
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text-muted);
    border-radius: var(--radius-pill);
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s ease;
    font-family: 'Montserrat', sans-serif;
  }
  .action-btn:hover { border-color: var(--accent); color: var(--accent-hover); background: var(--accent-soft); }
  .action-btn.saved { background: var(--accent-soft); color: var(--accent-hover); border-color: var(--accent); font-weight: 600; }
  .action-btn .star { font-size: 13px; }
  .action-btn.has-note { border-color: var(--amber); background: var(--amber-soft); color: #B45309; }

  /* ── Score badge ─────────────────────────────────────── */
  .score { display: flex; flex-direction: column; align-items: flex-end; padding-top: 6px; min-width: 80px; }
  .score-num { font-family: 'Montserrat', sans-serif; font-size: 44px; font-weight: 700; line-height: 1; letter-spacing: -0.04em; color: var(--score-mid); }
  .score-label { font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-dim); margin-top: 6px; font-weight: 600; }
  .score.tier-high .score-num { color: var(--score-high); }
  .score.tier-high .score-label { color: var(--accent); }
  .score.tier-low .score-num { color: var(--score-low); }

  /* ── Note preview under event ────────────────────────── */
  .note-preview {
    margin-top: 10px;
    padding: 10px 14px;
    background: var(--amber-soft);
    border-left: 3px solid var(--amber);
    border-radius: 6px;
    font-size: 13px;
    color: #78350F;
    line-height: 1.5;
  }
  .note-preview strong { color: var(--amber); font-weight: 700; margin-right: 6px; }

  /* ── Modal ───────────────────────────────────────────── */
  .modal-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    z-index: 1000;
    align-items: center;
    justify-content: center;
    padding: 24px;
  }
  .modal-overlay.active { display: flex; }
  .modal {
    background: var(--bg);
    border-radius: var(--radius-card);
    padding: 32px;
    max-width: 560px;
    width: 100%;
    max-height: 90vh;
    overflow: auto;
    box-shadow: 0 30px 80px rgba(0, 0, 0, 0.2);
  }
  .modal h3 {
    font-size: 18px;
    font-weight: 700;
    margin: 0 0 4px;
    color: var(--text);
    letter-spacing: -0.015em;
  }
  .modal .modal-subtitle {
    font-size: 13px;
    color: var(--text-muted);
    margin-bottom: 20px;
  }
  .modal textarea {
    width: 100%;
    min-height: 140px;
    padding: 14px;
    border: 1px solid var(--border);
    border-radius: 10px;
    font-family: 'Montserrat', sans-serif;
    font-size: 14px;
    resize: vertical;
    outline: none;
    color: var(--text);
  }
  .modal textarea:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
  .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
  .modal-actions .btn-danger { color: #DC2626; border-color: #FCA5A5; }
  .modal-actions .btn-danger:hover { background: #FEE2E2; border-color: #DC2626; }

  /* ── Empty state ─────────────────────────────────────── */
  .empty { text-align: center; padding: 80px 24px; color: var(--text-muted); font-size: 14px; background: var(--bg-soft); border-radius: var(--radius-card); margin-top: 32px; }
  .empty h4 { font-size: 18px; color: var(--text); margin: 0 0 10px; font-weight: 700; }

  /* ── Toast ───────────────────────────────────────────── */
  .toast {
    position: fixed;
    bottom: 32px;
    left: 50%;
    transform: translateX(-50%) translateY(100px);
    background: var(--text);
    color: #fff;
    padding: 12px 20px;
    border-radius: var(--radius-pill);
    font-size: 13px;
    font-weight: 500;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    transition: transform 0.25s ease, opacity 0.25s ease;
    opacity: 0;
    z-index: 2000;
    pointer-events: none;
  }
  .toast.active {
    transform: translateX(-50%) translateY(0);
    opacity: 1;
  }

  /* ── Footer ──────────────────────────────────────────── */
  footer { margin-top: 96px; padding-top: 32px; border-top: 1px solid var(--border-soft); display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: var(--text-muted); font-weight: 500; flex-wrap: wrap; gap: 16px; }

  /* ── Responsive ──────────────────────────────────────── */
  @media (max-width: 720px) {
    .container { padding: 28px 20px 80px; }
    .topbar { flex-direction: column; align-items: flex-start; }
    h1 { font-size: 42px; }
    .subtitle { font-size: 15px; }
    .controls { flex-direction: column; align-items: stretch; gap: 14px; }
    .controls-right { margin-left: 0; justify-content: stretch; flex-wrap: wrap; }
    .controls-right .btn { flex: 1; justify-content: center; }
    .stats { gap: 20px; }
    .stat-num { font-size: 24px; }
    .event { grid-template-columns: 1fr auto; gap: 16px; padding: 22px 0; }
    .event:hover { padding-left: 12px; padding-right: 12px; }
    .event-date { grid-column: 1 / -1; display: flex; gap: 8px; align-items: baseline; padding-top: 0; }
    .event-date .day { display: inline; font-size: 16px; }
    .score-num { font-size: 32px; }
    .event-title { font-size: 18px; }
    .tabs { overflow-x: auto; white-space: nowrap; }
  }

  /* ── Print view ──────────────────────────────────────── */
  @media print {
    .topbar-right, .tabs, .controls, .stats, .event-actions, footer, .icon-btn, .toast { display: none !important; }
    body { background: #fff; }
    .container { max-width: 100%; padding: 20px; }
    h1 { font-size: 32px; }
    .subtitle { font-size: 13px; }
    .event { break-inside: avoid; padding: 14px 0; border-bottom: 1px solid #ddd; }
    .event:hover { background: none; padding: 14px 0; }
    .event::before { display: none; }
    .event-description { font-size: 11px; }
    .event-title { font-size: 15px; }
    .section-header { margin-top: 20px; }
    .score-num { font-size: 24px; }
    .event-date .day { font-size: 20px; }
    .badge-new, .badge-format, .badge-topic { border: 1px solid #999; color: #333 !important; background: #fff !important; }
    .footer-print { display: block !important; text-align: center; margin-top: 24px; font-size: 10px; color: #999; }
  }
  .footer-print { display: none; }
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
        <span id="new-count-tag" class="tag" style="display:none; background: var(--amber-soft); color: #92400E;">
          <strong id="new-count-num">0</strong> new
        </span>
        <button class="icon-btn" id="open-settings" title="Settings / Export / Import">⚙</button>
      </div>
    </div>

    <header>
      <h1>Events<br><span class="black">worth showing up.</span></h1>
      <p class="subtitle">
        Automated watch on tech &amp; business events across Denmark — filtered by ICPs,
        scored by relevance, with your shortlist and sales notes.
      </p>
    </header>

    <div class="tabs">
      <button class="tab active" data-tab="all">
        All events <span class="count" id="count-all">0</span>
      </button>
      <button class="tab" data-tab="shortlist">
        ★ My shortlist <span class="count" id="count-shortlist">0</span>
      </button>
      <button class="tab" data-tab="past">
        Past events <span class="count" id="count-past">0</span>
      </button>
    </div>

    <div class="controls">
      <div class="filter-group">
        <span class="filter-label">Topic</span>
        <div class="select-wrap"><select id="filter-topic"><option value="all">All topics</option>__TOPIC_OPTIONS__</select></div>
      </div>
      <div class="filter-group">
        <span class="filter-label">Format</span>
        <div class="select-wrap"><select id="filter-format"><option value="all">All formats</option>__FORMAT_OPTIONS__</select></div>
      </div>
      <div class="filter-group">
        <span class="filter-label">City</span>
        <div class="select-wrap"><select id="filter-city"><option value="all">All cities</option>__CITY_OPTIONS__</select></div>
      </div>
      <div class="filter-group">
        <span class="filter-label">Organizer</span>
        <div class="select-wrap"><select id="filter-organizer"><option value="all">All organizers</option>__ORGANIZER_OPTIONS__</select></div>
      </div>
      <div class="filter-group">
        <span class="filter-label">When</span>
        <div class="select-wrap">
          <select id="filter-date">
            <option value="all">Any date</option>
            <option value="7">Next 7 days</option>
            <option value="14">Next 14 days</option>
            <option value="30">Next 30 days</option>
            <option value="90">Next 90 days</option>
          </select>
        </div>
      </div>
      <div class="filter-group">
        <button class="pill active" data-filter="cost" data-value="all">All</button>
        <button class="pill" data-filter="cost" data-value="free">Free only</button>
      </div>
      <div class="score-slider-wrap">
        <span class="filter-label">Min. score</span>
        <input type="range" id="score-range" min="0" max="100" step="5" value="0" />
        <span class="score-value" id="score-value">0</span>
      </div>
      <div class="controls-right">
        <button class="btn" id="btn-print" title="Print or save as PDF">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9V2h12v7M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2M6 14h12v8H6z"/></svg>
          Print
        </button>
        <a class="btn btn-primary" href="events.csv" download>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 3v12m0 0l-4-4m4 4l4-4M5 21h14"/></svg>
          Download CSV
        </a>
      </div>
    </div>

    <div class="stats" id="stats-bar">
      <div class="stat-item"><span class="stat-num accent" id="stat-top">0</span><span class="stat-label">Don't miss</span></div>
      <div class="stat-item"><span class="stat-num" id="stat-mid">0</span><span class="stat-label">Worth considering</span></div>
      <div class="stat-item"><span class="stat-num amber" id="stat-new">0</span><span class="stat-label">New this week</span></div>
      <div class="stat-item"><span class="stat-num" id="stat-free">0</span><span class="stat-label">Free events</span></div>
      <div class="stat-item"><span class="stat-num" id="stat-showing">0</span><span class="stat-label">Showing</span></div>
    </div>

    <main id="events-container"></main>

    <footer>
      <span>Flow Event Recon — v0.3</span>
      <span>Sources: Copenhagen Fintech · Luma · Eventbrite · Your saves are local to this browser</span>
    </footer>
    <div class="footer-print">Flow Event Recon — printed on <span id="print-date"></span></div>
  </div>

  <!-- Note modal -->
  <div class="modal-overlay" id="modal-note">
    <div class="modal">
      <h3 id="modal-note-title">Add a note</h3>
      <p class="modal-subtitle" id="modal-note-event"></p>
      <textarea id="modal-note-text" placeholder="E.g. 'met Jakub from Danske here', 'lead opportunity', 'bring printed one-pagers'..."></textarea>
      <div class="modal-actions">
        <button class="btn btn-danger" id="btn-note-delete">Delete</button>
        <button class="btn" id="btn-note-cancel">Cancel</button>
        <button class="btn btn-primary" id="btn-note-save">Save note</button>
      </div>
    </div>
  </div>

  <!-- Settings modal -->
  <div class="modal-overlay" id="modal-settings">
    <div class="modal">
      <h3>Settings &amp; backup</h3>
      <p class="modal-subtitle">
        Your saves and notes are stored in this browser. Export them as a backup or to share with a colleague.
      </p>
      <div style="display: flex; flex-direction: column; gap: 10px;">
        <button class="btn" id="btn-export">📤 Export my saves &amp; notes (JSON)</button>
        <button class="btn" id="btn-import">📥 Import from JSON file</button>
        <input type="file" id="import-file" accept=".json" style="display: none;" />
        <button class="btn btn-danger" id="btn-clear">🗑 Clear all my data</button>
      </div>
      <div class="modal-actions">
        <button class="btn" id="btn-settings-close">Close</button>
      </div>
    </div>
  </div>

  <div class="toast" id="toast"></div>

<script>
  const EVENTS = __EVENTS_JSON__;
  const PAST_EVENTS = __PAST_EVENTS_JSON__;
  const SCORE_HIGH = __SCORE_HIGH__;
  const SCORE_MEDIUM = __SCORE_MEDIUM__;

  // ── State (persisted in localStorage) ───────────────
  const STORAGE_KEY = 'flowEventRecon_v1';

  function loadUserData() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    } catch (e) { return {}; }
  }
  function saveUserData(data) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(data)); } catch (e) {}
  }
  function getSaves() { return loadUserData().saves || {}; }
  function getNotes() { return loadUserData().notes || {}; }
  function toggleSave(url) {
    const data = loadUserData();
    data.saves = data.saves || {};
    if (data.saves[url]) delete data.saves[url];
    else data.saves[url] = Date.now();
    saveUserData(data);
  }
  function setNote(url, text) {
    const data = loadUserData();
    data.notes = data.notes || {};
    if (text) data.notes[url] = text;
    else delete data.notes[url];
    saveUserData(data);
  }

  // ── Runtime state ───────────────────────────────────
  const state = {
    tab: 'all',
    topic: 'all',
    format: 'all',
    city: 'all',
    organizer: 'all',
    date: 'all',
    cost: 'all',
    minScore: 0,
  };

  // ── Utilities ───────────────────────────────────────
  function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function parseDateParts(d) {
    const parts = (d || "").split(" ");
    return { day: parts[0] || "—", month: (parts[1] || "").toUpperCase(), year: parts[2] || "" };
  }
  function tierClass(score) {
    if (score >= SCORE_HIGH) return "tier-high";
    if (score >= SCORE_MEDIUM) return "";
    return "tier-low";
  }
  function toast(msg) {
    const el = document.getElementById('toast');
    el.textContent = msg;
    el.classList.add('active');
    setTimeout(() => el.classList.remove('active'), 2200);
  }

  // ── .ics generation ─────────────────────────────────
  function formatICSDate(isoStr) {
    // 2026-05-06T09:00:00+00:00 → 20260506T090000Z
    const dt = new Date(isoStr);
    const pad = n => String(n).padStart(2, '0');
    return dt.getUTCFullYear() +
      pad(dt.getUTCMonth() + 1) +
      pad(dt.getUTCDate()) + 'T' +
      pad(dt.getUTCHours()) +
      pad(dt.getUTCMinutes()) +
      pad(dt.getUTCSeconds()) + 'Z';
  }
  function downloadICS(event) {
    const start = event.date_iso;
    const startDate = new Date(start);
    const endDate = new Date(startDate.getTime() + 2 * 60 * 60 * 1000); // +2h default

    const uid = btoa(event.url).replace(/=/g, '') + '@flow-event-recon';
    const lines = [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//Flow Event Recon//EN',
      'BEGIN:VEVENT',
      'UID:' + uid,
      'DTSTAMP:' + formatICSDate(new Date().toISOString()),
      'DTSTART:' + formatICSDate(startDate.toISOString()),
      'DTEND:' + formatICSDate(endDate.toISOString()),
      'SUMMARY:' + (event.title || '').replace(/[,;\n]/g, ' '),
      'DESCRIPTION:' + (event.description_short || '').replace(/[,;\n]/g, ' ').substring(0, 300) + '\\n\\n' + event.url,
      'LOCATION:' + (event.city || ''),
      'URL:' + event.url,
      'END:VEVENT',
      'END:VCALENDAR'
    ].join('\r\n');

    const blob = new Blob([lines], { type: 'text/calendar;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = (event.title || 'event').replace(/[^a-z0-9]/gi, '_').substring(0, 50) + '.ics';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast('📅 Calendar file downloaded');
  }

  // ── Render event ────────────────────────────────────
  function renderEvent(e, opts = {}) {
    const isPast = opts.isPast || false;
    const saves = getSaves();
    const notes = getNotes();
    const isSaved = !!saves[e.url];
    const note = notes[e.url];

    const tier = tierClass(parseInt(e.score, 10) || 0);
    const parts = parseDateParts(e.date);
    const tags = (e.keywords_match || "").split(",").map(t => t.trim()).filter(Boolean);
    const tagHtml = tags.slice(0, 5).map(t => `<span class="tag">${escapeHtml(t)}</span>`).join("");
    const moreTags = tags.length > 5 ? `<span class="tag">+${tags.length - 5}</span>` : "";

    const isFree = (e.price || "").toLowerCase() === "free";
    const priceHtml = isFree
      ? `<span class="free">Free</span>`
      : `<span>${escapeHtml(e.price)}</span>`;

    const formatBadge = e.format && e.format !== "Other"
      ? `<span class="badge badge-format">${escapeHtml(e.format)}</span>` : "";
    const topicBadge = e.topic && e.topic !== "Other"
      ? `<span class="badge badge-topic">${escapeHtml(e.topic)}</span>` : "";
    const newBadge = (!isPast && (e.is_new === "True" || e.is_new === true))
      ? `<span class="badge badge-new">NEW</span>` : "";

    const organizerHtml = e.organizer
      ? `<span class="organizer-link" data-filter-organizer="${escapeHtml(e.organizer)}">${escapeHtml(e.organizer)}</span><span class="sep">·</span>`
      : "";

    return `
      <article class="event" data-url="${escapeHtml(e.url)}">
        <div class="event-date">
          <span class="day">${escapeHtml(parts.day)}</span>
          ${escapeHtml(parts.month)} ${escapeHtml(parts.year)}
        </div>
        <div class="event-main">
          ${formatBadge || topicBadge || newBadge ? `<div class="event-badges">${newBadge}${formatBadge}${topicBadge}</div>` : ""}
          <a class="event-title" href="${escapeHtml(e.url)}" target="_blank" rel="noopener">${escapeHtml(e.title)}<span class="arrow">↗</span></a>
          <div class="event-meta">
            ${organizerHtml}
            <span>${escapeHtml(e.city || "—")}</span>
            <span class="sep">·</span>
            <span>${escapeHtml(e.mode || "")}</span>
            <span class="sep">·</span>
            ${priceHtml}
          </div>
          ${e.description_short ? `<p class="event-description">${escapeHtml(e.description_short)}</p>` : ""}
          ${tags.length ? `<div class="event-tags">${tagHtml}${moreTags}</div>` : ""}
          ${!isPast ? `
          <div class="event-actions">
            <button class="action-btn ${isSaved ? 'saved' : ''}" data-action="save">
              <span class="star">${isSaved ? '★' : '☆'}</span>
              ${isSaved ? 'Saved' : 'Save'}
            </button>
            <button class="action-btn ${note ? 'has-note' : ''}" data-action="note">
              📝 ${note ? 'Edit note' : 'Add note'}
            </button>
            <button class="action-btn" data-action="calendar">
              📅 Add to calendar
            </button>
          </div>
          ` : ""}
          ${note ? `<div class="note-preview"><strong>NOTE</strong>${escapeHtml(note)}</div>` : ""}
        </div>
        <div class="score ${tier}">
          <span class="score-num">${e.score}</span>
          <span class="score-label">Score</span>
        </div>
      </article>
    `;
  }

  // ── Filter logic ────────────────────────────────────
  function matchesFilters(e) {
    if (state.topic !== 'all' && e.topic !== state.topic) return false;
    if (state.format !== 'all' && e.format !== state.format) return false;
    if (state.city !== 'all' && (e.city || "").toLowerCase() !== state.city.toLowerCase()) return false;
    if (state.organizer !== 'all' && (e.organizer || "") !== state.organizer) return false;
    if (state.cost === 'free' && (e.price || "").toLowerCase() !== 'free') return false;
    if ((parseInt(e.score, 10) || 0) < state.minScore) return false;
    if (state.date !== 'all') {
      const days = parseInt(state.date, 10);
      try {
        const dt = new Date(e.date_iso);
        const now = new Date();
        const diff = (dt - now) / (1000 * 60 * 60 * 24);
        if (diff > days) return false;
        if (diff < -1) return false; // don't show already-past when filtered by "next X days"
      } catch (err) {}
    }
    return true;
  }

  function updateStats(filtered) {
    const top = filtered.filter(e => (parseInt(e.score, 10) || 0) >= SCORE_HIGH).length;
    const mid = filtered.filter(e => { const s = parseInt(e.score, 10) || 0; return s >= SCORE_MEDIUM && s < SCORE_HIGH; }).length;
    const newCount = filtered.filter(e => e.is_new === "True" || e.is_new === true).length;
    const free = filtered.filter(e => (e.price || "").toLowerCase() === 'free').length;
    document.getElementById('stat-top').textContent = top;
    document.getElementById('stat-mid').textContent = mid;
    document.getElementById('stat-new').textContent = newCount;
    document.getElementById('stat-free').textContent = free;
    document.getElementById('stat-showing').textContent = filtered.length;

    const globalNew = EVENTS.filter(e => e.is_new === "True" || e.is_new === true).length;
    const tag = document.getElementById('new-count-tag');
    if (globalNew > 0) {
      tag.style.display = '';
      document.getElementById('new-count-num').textContent = globalNew;
    } else {
      tag.style.display = 'none';
    }
  }

  function updateTabCounts() {
    const saves = getSaves();
    const shortlistCount = EVENTS.filter(e => saves[e.url]).length;
    document.getElementById('count-all').textContent = EVENTS.length;
    document.getElementById('count-shortlist').textContent = shortlistCount;
    document.getElementById('count-past').textContent = PAST_EVENTS.length;
  }

  // ── Render ──────────────────────────────────────────
  function render() {
    const container = document.getElementById('events-container');
    let source;
    let isPast = false;

    if (state.tab === 'shortlist') {
      const saves = getSaves();
      source = EVENTS.filter(e => saves[e.url]);
    } else if (state.tab === 'past') {
      source = PAST_EVENTS;
      isPast = true;
    } else {
      source = EVENTS;
    }

    const filtered = source.filter(matchesFilters);
    updateStats(filtered);
    updateTabCounts();

    if (!filtered.length) {
      let msg;
      if (state.tab === 'shortlist') msg = `<h4>Your shortlist is empty</h4>Browse events and tap ★ Save to add them here.`;
      else if (state.tab === 'past') msg = `<h4>No past events yet</h4>As events happen, they'll move here for the next 90 days.`;
      else msg = `<h4>No events match these filters</h4>Try widening the filters or lowering the min. score.`;
      container.innerHTML = `<div class="empty">${msg}</div>`;
      return;
    }

    if (isPast) {
      // Flat list, newest first (already sorted by CSV)
      container.innerHTML = filtered.map(e => renderEvent(e, { isPast: true })).join("");
      return;
    }

    const topEvents = filtered.filter(e => (parseInt(e.score, 10) || 0) >= SCORE_HIGH);
    const midEvents = filtered.filter(e => { const s = parseInt(e.score, 10) || 0; return s >= SCORE_MEDIUM && s < SCORE_HIGH; });
    const lowEvents = filtered.filter(e => (parseInt(e.score, 10) || 0) < SCORE_MEDIUM);

    const sections = [];
    if (topEvents.length) sections.push(`
      <div class="section-header">
        <h2 class="section-title"><span class="marker"></span>Don't miss</h2>
        <span class="section-count">${topEvents.length} event${topEvents.length === 1 ? '' : 's'} · score ≥ ${SCORE_HIGH}</span>
      </div>${topEvents.map(e => renderEvent(e)).join("")}`);
    if (midEvents.length) sections.push(`
      <div class="section-header">
        <h2 class="section-title"><span class="marker"></span>Worth considering</h2>
        <span class="section-count">${midEvents.length} event${midEvents.length === 1 ? '' : 's'} · score ${SCORE_MEDIUM}–${SCORE_HIGH - 1}</span>
      </div>${midEvents.map(e => renderEvent(e)).join("")}`);
    if (lowEvents.length) sections.push(`
      <div class="section-header">
        <h2 class="section-title muted"><span class="marker"></span>Low relevance</h2>
        <span class="section-count">${lowEvents.length} event${lowEvents.length === 1 ? '' : 's'} · score &lt; ${SCORE_MEDIUM}</span>
      </div>${lowEvents.map(e => renderEvent(e)).join("")}`);
    container.innerHTML = sections.join("");
  }

  // ── Event delegation for action buttons ─────────────
  document.getElementById('events-container').addEventListener('click', (ev) => {
    const actionBtn = ev.target.closest('.action-btn');
    const orgLink = ev.target.closest('.organizer-link');

    if (orgLink) {
      const org = orgLink.dataset.filterOrganizer;
      const select = document.getElementById('filter-organizer');
      select.value = org;
      select.dispatchEvent(new Event('change'));
      ev.preventDefault();
      return;
    }

    if (!actionBtn) return;
    const article = actionBtn.closest('.event');
    const url = article.dataset.url;
    const evt = [...EVENTS, ...PAST_EVENTS].find(e => e.url === url);
    if (!evt) return;
    const action = actionBtn.dataset.action;

    if (action === 'save') {
      toggleSave(url);
      render();
      toast(getSaves()[url] ? '★ Saved to shortlist' : 'Removed from shortlist');
    } else if (action === 'calendar') {
      downloadICS(evt);
    } else if (action === 'note') {
      openNoteModal(evt);
    }
  });

  // ── Note modal ──────────────────────────────────────
  let currentNoteUrl = null;
  function openNoteModal(event) {
    currentNoteUrl = event.url;
    document.getElementById('modal-note-event').textContent = event.title;
    document.getElementById('modal-note-text').value = getNotes()[event.url] || '';
    document.getElementById('btn-note-delete').style.display = getNotes()[event.url] ? '' : 'none';
    document.getElementById('modal-note').classList.add('active');
    setTimeout(() => document.getElementById('modal-note-text').focus(), 50);
  }
  function closeNoteModal() {
    document.getElementById('modal-note').classList.remove('active');
    currentNoteUrl = null;
  }
  document.getElementById('btn-note-cancel').addEventListener('click', closeNoteModal);
  document.getElementById('btn-note-save').addEventListener('click', () => {
    const text = document.getElementById('modal-note-text').value.trim();
    if (currentNoteUrl) {
      setNote(currentNoteUrl, text);
      render();
      toast(text ? '📝 Note saved' : '📝 Note removed');
    }
    closeNoteModal();
  });
  document.getElementById('btn-note-delete').addEventListener('click', () => {
    if (currentNoteUrl) {
      setNote(currentNoteUrl, '');
      render();
      toast('📝 Note deleted');
    }
    closeNoteModal();
  });

  // ── Settings modal ──────────────────────────────────
  document.getElementById('open-settings').addEventListener('click', () => {
    document.getElementById('modal-settings').classList.add('active');
  });
  document.getElementById('btn-settings-close').addEventListener('click', () => {
    document.getElementById('modal-settings').classList.remove('active');
  });
  document.getElementById('btn-export').addEventListener('click', () => {
    const data = loadUserData();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'flow-event-recon-saves-' + new Date().toISOString().slice(0, 10) + '.json';
    a.click();
    toast('📤 Exported');
  });
  document.getElementById('btn-import').addEventListener('click', () => {
    document.getElementById('import-file').click();
  });
  document.getElementById('import-file').addEventListener('change', (ev) => {
    const file = ev.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result);
        if (!data.saves && !data.notes) throw new Error('Invalid file');
        saveUserData(data);
        render();
        toast('📥 Imported');
        document.getElementById('modal-settings').classList.remove('active');
      } catch (err) {
        toast('⚠ Invalid file');
      }
    };
    reader.readAsText(file);
  });
  document.getElementById('btn-clear').addEventListener('click', () => {
    if (confirm('Remove all your saved events and notes? This cannot be undone.')) {
      localStorage.removeItem(STORAGE_KEY);
      render();
      toast('🗑 Cleared');
      document.getElementById('modal-settings').classList.remove('active');
    }
  });

  // Click outside modal to close
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (ev) => {
      if (ev.target === overlay) overlay.classList.remove('active');
    });
  });

  // ── Tabs ────────────────────────────────────────────
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      state.tab = tab.dataset.tab;
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      render();
    });
  });

  // ── Filters ─────────────────────────────────────────
  ['topic', 'format', 'city', 'organizer', 'date'].forEach(key => {
    const el = document.getElementById(`filter-${key}`);
    el.addEventListener('change', () => {
      state[key] = el.value;
      el.classList.toggle('active', el.value !== 'all');
      render();
    });
  });

  document.querySelectorAll(".pill[data-filter='cost']").forEach(pill => {
    pill.addEventListener('click', () => {
      state.cost = pill.dataset.value;
      document.querySelectorAll(".pill[data-filter='cost']").forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      render();
    });
  });

  const range = document.getElementById('score-range');
  const rangeValue = document.getElementById('score-value');
  range.addEventListener('input', () => {
    state.minScore = Number(range.value);
    rangeValue.textContent = range.value;
    render();
  });

  // ── Print ───────────────────────────────────────────
  document.getElementById('btn-print').addEventListener('click', () => {
    document.getElementById('print-date').textContent = new Date().toLocaleDateString();
    window.print();
  });

  // ── Initial render ──────────────────────────────────
  render();
</script>
</body>
</html>
"""


def _load_csv(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    with open(p, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _options(values: list[str]) -> str:
    return "\n".join(
        f'          <option value="{html.escape(v)}">{html.escape(v)}</option>'
        for v in values
    )


def build_dashboard() -> None:
    events = _load_csv(CSV_OUTPUT)
    events.sort(key=lambda e: (-int(e.get("score", 0) or 0), e.get("date_iso", "")))
    past_events = _load_csv(PAST_EVENTS_CSV)
    past_events.sort(key=lambda e: e.get("date_iso", ""), reverse=True)

    cities = sorted({e.get("city", "").strip() for e in events if e.get("city", "").strip()})
    topics = sorted({e.get("topic", "").strip() for e in events
                     if e.get("topic", "").strip() and e.get("topic") != "Other"})
    formats = sorted({e.get("format", "").strip() for e in events
                      if e.get("format", "").strip() and e.get("format") != "Other"})
    organizers = sorted({e.get("organizer", "").strip() for e in events
                         if e.get("organizer", "").strip()})

    html_str = HTML_TEMPLATE
    html_str = html_str.replace("__EVENTS_JSON__", json.dumps(events, ensure_ascii=False))
    html_str = html_str.replace("__PAST_EVENTS_JSON__", json.dumps(past_events, ensure_ascii=False))
    html_str = html_str.replace("__TOTAL__", str(len(events)))
    html_str = html_str.replace("__UPDATED__", datetime.now().strftime("%d %b %Y"))
    html_str = html_str.replace("__SCORE_HIGH__", str(SCORE_TIER_HIGH))
    html_str = html_str.replace("__SCORE_MEDIUM__", str(SCORE_TIER_MEDIUM))
    html_str = html_str.replace("__CITY_OPTIONS__", _options(cities))
    html_str = html_str.replace("__TOPIC_OPTIONS__", _options(topics))
    html_str = html_str.replace("__FORMAT_OPTIONS__", _options(formats))
    html_str = html_str.replace("__ORGANIZER_OPTIONS__", _options(organizers))

    with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_str)

    print(f"✓ Generated {HTML_OUTPUT}")


if __name__ == "__main__":
    build_dashboard()
