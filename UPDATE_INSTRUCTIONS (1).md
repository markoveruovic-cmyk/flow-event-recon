# Flow Event Recon v0.4 — Upgrade Instructions

## 🆕 Co je v této verzi nového

### Sales features (15 + extras)

**Nová záložka "What changed"** — ukazuje jen nové eventy od minulého týdne

**Event of the week hero card** — vizuálně vyzdvihne top event týdne (skóre 80+)

**Weekly summary oneliner** — pod hlavičkou: "This week: 3 top events · 2 new · next top in 12 days"

**NEW badge** (už měla v0.3, vylepšeno)

**Smart relative dates** — u eventů vidíš TOMORROW, IN 3 DAYS, NEXT WEEK, THIS MONTH

**Keyword highlighting** — v popisu se žlutě zvýrazní tvoje ICP/tech klíčová slova

**Key company chips** (🏢) — zelené chip badges s firmami ze sledovaného seznamu (Danske Bank, Nordea, Matas, etc.). Klikneš → zfiltruje.

**Speaker chips** (🎤) — jména řečníků extrahovaných z popisů (opatrná heuristika)

**Company filter** — nový dropdown "Any key company"

**Full-text search bar** — vyhledá napříč title, description, organizer, speakers

**Conflict detector** — 2 ★ saved eventy ve stejný den → ⚠️ badge a červený levý pruh

**Similar to what you saved** — v záložce My shortlist dole doporučí 5 podobných eventů

**Email template** — tlačítko 📧 otevře mail klienta s předvyplněným textem pro kontaktování účastníka

**Copy link with UTM** — 🔗 tlačítko zkopíruje link s ?utm_source=flow-event-recon

**iCal feed** — tlačítko nahoře → stáhne celý shortlist jako .ics (drop do Google/Outlook/Apple kalendáře)

**Manual event seed** — ⊕ Add event tlačítko, modal formulář, uloží do localStorage, zobrazí s MANUAL badge

**Dark mode toggle** — 🌙/☀ v pravém horním rohu

**Countdown** — "Next top event: Nordic Fintech Week in 23 days"

**Stats strip** s 6 čísly včetně Conflicts

**Print view** — lepší formátování pro tisk/PDF

### Zdroje (4 → 10)

**Stále funguje:**
- Copenhagen Fintech
- Luma Copenhagen, Luma Aarhus
- Eventbrite Business + Tech

**Nově přidáno:**
- Eventbrite Retail Copenhagen
- Eventbrite Fintech Copenhagen
- Innovation District Copenhagen
- IT-Branchen
- FDIH (Dansk E-handel)

Plus **generic_html adaptér** — jakýkoliv web s event listing HTML můžeme přidat jednou konfigurační položkou v `config.py`.

### Key Companies seznam

Scraper teď zná **63 sledovaných firem** — banky, pojišťovny, retailery, automotive, telco, food delivery, B2C s appkami. Když event zmiňuje Danske Bank, Nordea, Matas, Škoda, LEGO nebo jiné, automaticky se zobrazí jako chip a přidá +5 bodů do skóre.

---

## 📋 Soubory k nahrání

**Soubory k přepsání na GitHubu:**
1. `config.py` — nové zdroje + KEY_COMPANIES seznam
2. `scoring.py` — speaker + company extraction
3. `scraper.py` — generic_html adaptér + nové fields
4. `history.py` — update pro nové pole
5. `generate_html.py` — kompletně nový v0.4 dashboard
6. `.github/workflows/weekly.yml` — beze změny, ale můžeš přepsat (pro jistotu)

**Beze změny:**
- `requirements.txt`
- `README.md`

**Auto-generované (NEPŘEPISUJ, vytvoří se workflow):**
- `events.csv`
- `past_events.csv`
- `seen_urls.txt`
- `index.html`

---

## 🔧 Postup (10 min na GitHubu)

### Krok 1 — Smaž tyto soubory na GitHubu (jeden po druhém)

1. `config.py`
2. `scoring.py`
3. `scraper.py`
4. `history.py`
5. `generate_html.py`
6. `events.csv`
7. `past_events.csv`
8. `index.html`

⚠️ **NEMAŽ** `.github/workflows/` složku!

### Krok 2 — Nahraj nových 10 souborů

Na hlavní stránce repa:
1. **Add file** → **Upload files**
2. Z mého balíčku označ všech 10 souborů
3. Přetáhni do šedé zóny
4. Commit message: `upgrade to v0.4`
5. **Commit changes**

### Krok 3 — Sleduj Actions

Po commitu se workflow spustí sám. Za ~3 minuty:

- Zelené ✅✅ = hotovo, otevři svoji URL
- Červené ❌ = pošli screenshot logu

---

## 🎯 Realistické očekávání

### Nové zdroje

Z 5 nových zdrojů (4 Eventbrite search + 3 generic_html):
- **Eventbrite retail / fintech** — pravděpodobně ok, stejná struktura jako už funkční
- **Innovation District** — odhad 50/50, záleží na jejich HTML
- **IT-Branchen** — stejně
- **FDIH** — dánská stránka, malá, může mít jen 2-5 eventů

**Není to garance.** Generic_html je best-effort. Pokud zdroj vrátí 0 eventů při prvním běhu, není to bug — je to že jejich HTML neodpovídá našim selektorům. Tech tým pak doladí v `config.py` selektory pro konkrétní web.

### Speaker extraction

Funguje dobře na strukturované popisy typu "Speakers: Anna Jensen, Peter Olsen". Může občas minout u volně psaných popisů. Opět best-effort, vysokoprecizní.

### Key companies

**Funguje spolehlivě** — pattern matching na 63 firem ze seznamu. Pokud chybí firma, která tě zajímá, přidej ji do `config.py` → `KEY_COMPANIES`.

### Dark mode

Tlačítko 🌙 v pravém horním rohu. Uloží se per-prohlížeč.

---

## 💡 Pro salese — workflow tip

**Pondělí ráno:**
1. Otevři URL u kávy
2. Hero card ti ukáže event týdne
3. Weekly summary nahoře: "3 top · 2 new · next top in X days"
4. Klikni "What changed" tab → vidíš jen nové od minulého týdne
5. U zajímavých events klikni ★ Save + 📝 napiš note
6. Nakonec klikni 🔗 iCal feed → stáhni shortlist → drop do Outlooku

**Před eventem:**
- My shortlist tab → vidíš co máš naplánované
- Similar to what you saved ti ukáže, co dalšího by tě mohlo zajímat
- 📧 Email template u eventu ti napíše kontaktovací mail k prospektovi

**Po eventu:**
- Event přejde do Past events (90 dní)
- Klikneš na něj → vidíš svou starou notu → follow-up

---

## 📞 Když něco selže

**Actions vyhodí error?** → screenshot logu, společně ladíme.

**Nějaký zdroj vrátí 0 eventů?** → OK, prostě se nepoužije. Můžeš ho vypnout v `config.py`: `"enabled": False`.

**Dashboard vypadá rozbitě?** → CDN Google Fonts možná nenajela. Refresh. Funkce poběží i bez fontů.

**Speaker se chybně detekuje?** → Napiš mi která event a jaký speaker špatně, doladíme NAME_STOPWORDS.

---

🚀 Jdi na to!
