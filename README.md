# Flow Event Recon

Interní nástroj Etnetera Flow pro automatizovaný přehled tech/business eventů v Dánsku.

Sleduje eventy ze 4 zdrojů (Copenhagen Fintech, Luma, Eventbrite), skóruje podle
relevance pro ICPs (Retail, BFSI, E-commerce), kategorizuje podle topicu a formátu,
a nabízí sales-focused dashboard s shortlisty, poznámkami a calendar exportem.

**Live URL:** https://markoveruovic-cmyk.github.io/flow-event-recon/

---

## Co to umí (v0.3)

### Dashboard features
- 📊 Stats strip — Don't miss / Worth considering / New / Free / Showing
- 🏷️ 5 filtrů — Topic, Format, City, Organizer, When (date range)
- 🟡 NEW badge — u eventů, které minulý týden ještě nebyly
- ⭐ ★ Save — osobní shortlist (localStorage)
- 📝 Sales notes — per-event poznámky (localStorage)
- 📅 Add to Calendar — stáhne .ics soubor
- 🗂️ 3 záložky — All events / My shortlist / Past events
- 🖨️ Print / Save as PDF — čistý printable výpis
- ⚙️ Export/Import — backup & sharing shortlistu s kolegou

### Pod kapotou
- Scraping: Copenhagen Fintech, Luma (CPH + Aarhus), Eventbrite (Business + Tech)
- History tracking: seen_urls.txt pamatuje dřívější eventy pro detekci nových
- Past events archive: past_events.csv, 90denní retence
- Každé pondělí 8:00 automatický run přes GitHub Actions

---

## Struktura projektu

```
flow-event-recon/
├── .github/workflows/weekly.yml   ← GitHub Actions scheduler
├── config.py                       ← keywords, kategorie, zdroje (HLAVNÍ edit point)
├── scoring.py                      ← výpočet skóre (0-100)
├── scraper.py                      ← multi-source scraping
├── history.py                      ← NEW tracking + past events archive
├── generate_html.py                ← dashboard generator
├── requirements.txt                ← Python dependencies
├── events.csv                      ← [auto] upcoming events
├── past_events.csv                 ← [auto] archive (90 dní)
├── seen_urls.txt                   ← [auto] history store
└── index.html                      ← [auto] finální dashboard
```

[auto] = generuje se a commituje automaticky při každém běhu workflow.

---

## Editace bez kódu

**Přidat / upravit klíčová slova:**
Otevři config.py na GitHubu (klikni tužku) a uprav seznamy ICP_KEYWORDS, TECH_KEYWORDS.
Commit changes → workflow se spustí → za 2 min je změna live.

**Změnit váhy skórování:**
config.py, sekce SCORE_* konstanty + TOPIC_SCORE_BONUS + FORMAT_SCORE_BONUS.

**Vypnout zdroj:**
config.py → SOURCES → nastav "enabled": False u daného zdroje.

---

## Lokální spuštění (volitelné)

```bash
pip install -r requirements.txt
python scraper.py       # stáhne, napočítá, vytvoří CSV + HTML
open index.html         # otevři v prohlížeči
```

Python 3.10+ required.

---

## Roadmapa

- [ ] AI vrstva přes Claude API (lepší shrnutí + inteligentnější kategorizace)
- [ ] Use Case 2 — Key accounts tracking
- [ ] Slack webhook notifikace
- [ ] Email digest
- [ ] Další zdroje (TechBBQ partneři, DI events, Meetup.com)
