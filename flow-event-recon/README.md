# Flow Event Recon

Interní nástroj Etnetera Flow pro automatizovaný přehled tech/business eventů v Dánsku.

Malý Python nástroj, co každé pondělí (nebo kdy ho spustíš) stáhne nadcházející
tech/business eventy v Dánsku, skóruje je podle tvých klíčových slov a vyhodí ti:

1. `events.csv` — tabulka, co otevřeš v Excelu / Google Sheets
2. `index.html` — přehledová webová stránka v brandu Flow, kterou si otevřeš v prohlížeči

**Žádné AI API, žádný cloud, žádné účty** — jen Python a čtyři soubory kódu.

---

## Co je v projektu

```
flow-event-recon/
├── config.py          ← KLÍČOVÁ SLOVA a nastavení (TADY budeš upravovat)
├── scraper.py         ← stahuje z Lumy
├── scoring.py         ← počítá skóre 0–100
├── generate_html.py   ← vygeneruje webovou stránku
├── events.csv         ← výstup (při prvním spuštění přepíšeš ukázková data)
├── index.html         ← výstup (otevři v prohlížeči)
├── requirements.txt   ← seznam knihoven (pro tech tým / pip install)
└── README.md          ← tenhle soubor
```

---

## Rychlý start (poprvé)

### 1. Zkontroluj, že máš Python 3.10+

Otevři terminál a spusť:

```bash
python3 --version
```

Pokud to ukáže `3.10` a vyšší, jsi OK. Pokud ne, nainstaluj si
[Python z python.org](https://www.python.org/downloads/).

### 2. Nainstaluj knihovny

V terminálu, v této složce:

```bash
pip3 install -r requirements.txt
```

Stáhne tři drobné knihovny (requests, beautifulsoup4, python-dateutil).

### 3. Otevři preview BEZ stahování nových eventů

Kdyžužsi chceš nejdřív jen prohlédnout, jak to vypadá — otevři `index.html`
v prohlížeči (nebo spusť):

```bash
python3 generate_html.py
```

Uvidíš dashboard s ukázkovými eventy ze Sample CSV.

### 4. Stáhni reálné eventy z Lumy

```bash
python3 scraper.py
```

Skript:
- stáhne eventy z `lu.ma/copenhagen` a `lu.ma/aarhus`
- přepočítá skóre
- přepíše `events.csv` a `index.html`

Pak znovu otevři `index.html` — vidíš aktuální data.

---

## Úpravy, co zvládneš sama

### Přidat / ubrat klíčová slova

Otevři `config.py` v libovolném editoru (VS Code, Notepad, cokoliv).
Seznamy `ICP_KEYWORDS` a `TECH_KEYWORDS` uprav podle potřeby.

### Změnit barvy nebo vzhled

`generate_html.py` — hned nahoře v `HTML_TEMPLATE` jsou CSS proměnné:

```css
--bg: #0B0B0B;
--accent: #D7FF3A;
--text: #F5F5F0;
```

Uprav hexy podle aktuálního brand guidu Flow a přegeneruj:

```bash
python3 generate_html.py
```

### Přidat další dánské město

V `config.py` přidej do `SOURCES`:

```python
"luma_odense": {
    "enabled": True,
    "url": "https://lu.ma/odense",
    "city_default": "Odense",
},
```

---

## Co přidáme příště (roadmapa)

- [ ] **Další zdroje:** Eventbrite, Meetup, TechBBQ, Copenhagen Fintech Week
- [ ] **Claude API:** lepší AI shrnutí (2–3 věty namísto zkrácení popisu) a
      chytřejší skórování, co rozumí kontextu
- [ ] **Automatický běh:** GitHub Actions cron každé pondělí v 7:00
- [ ] **Use case 2:** Sledování key accounts (Danske Bank, Nordea, …)
- [ ] **Export do Notionu / Slacku** (volitelné)

---

## Když něco nefunguje

**"No events collected"**  
Luma mohla změnit strukturu stránky. Pošli tech týmu výstup z terminálu
a soubor `scraper.py`.

**"ModuleNotFoundError"**  
Zapomněla jsi krok 2 — `pip3 install -r requirements.txt`.

**Stránka vypadá rozbitě**  
Pravděpodobně nejede internet při prvním načtení (kvůli Google Fonts).
Bez fontů bude fungovat, jen to nebude tak hezké.

---

## Pro tech tým

- Pure Python 3.10+, žádné exotické dependencies
- Jeden adaptér = jedna funkce `scrape_*(key, cfg)` v `scraper.py`, vrací `list[Event]`
- Přidání zdroje: nový záznam v `SOURCES` + funkce s odpovídajícím prefixem
- Scoring je rules-based (viz `scoring.py`), připravený na pozdější AI vrstvu
- HTML je jeden soubor bez buildu, žádný Node / bundler
- Pro deployment doporučuju GitHub Actions cron + commit výstupu do repa,
  případně GitHub Pages na hosting `index.html`
