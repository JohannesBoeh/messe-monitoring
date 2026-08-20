"""
AUMA Scraper  v4
================
Step 1 – Fetch fair list from AUMA overview API.
Step 2 – For each fair, try a detail API endpoint first; if that returns no
         stats, fall back to rendering the fair's HTML page with Playwright
         and scraping trade-fair-statistics-table__item elements.

Exact AUMA label strings (confirmed from live site):
  Besucherzahl       → "Besucher (Zahl der Eintritte)"
  Ausstellerzahl     → "Aussteller"
  Angebotsschwerpunkt→ "Angebotsschwerpunkte"
  Branchenschwerpunkt→ "Branchenschwerpunkte"
  Zutritt            → "Zutritt"
  Veranstalter       → "Veranstalter"
  Turnus             → "Turnus:"

Install:
    pip install requests beautifulsoup4 playwright
    playwright install chromium

Run:
    python auma_scraper.py [--year-from 2026] [--year-to 2032]
                          [--all-cities] [--include-non-fkm]
                          [--no-browser]
                          [--debug]     # dumps API fields + saves first page HTML
                          [--output AUMA_FKM_Messen.csv]
"""

30| import argparse
31| import csv
32| import json
33| import logging
34| import re
35| import time
36| from pathlib import Path
37| 
37| import requests
38| from requests.adapters import HTTPAdapter
39| from urllib3.util.retry import Retry
40| from bs4 import BeautifulSoup
40| 
41| # Setup logging
42| logger = logging.getLogger(__name__)
43| logging.basicConfig(
44|     level=logging.INFO,
45|     format='%(asctime)s | %(levelname)-8s | %(message)s',
45|     datefmt='%Y-%m-%d %H:%M:%S'
46| )

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

A_STANDORTE = [
    "Berlin", "Düsseldorf", "Frankfurt am Main",
    "Hamburg", "Köln", "Leipzig", "München", "Stuttgart",
]
B_STANDORTE = [
    "Hannover", "Nürnberg", "Essen", "Dortmund", "Friedrichshafen",
    "Freiburg", "Bremen", "Dresden", "Erfurt", "Karlsruhe",
]
ALL_TARGET_CITIES = A_STANDORTE + B_STANDORTE

# Exact label strings as shown on AUMA website (lowercased for matching)
LABEL_BESUCHER            = "besucher (zahl der eintritte)"
LABEL_AUSSTELLER          = "aussteller"
LABEL_ANGEBOTSSCHWERPUNKT = "angebotsschwerpunkte"
LABEL_BRANCHENSCHWERPUNKT = "branchenschwerpunkte"
LABEL_ZUTRITT             = "zutritt"
LABEL_VERANSTALTER        = "veranstalter"
LABEL_TURNUS              = "turnus:"

OUTPUT_FIELDS = [
    "Messe", "Jahr", "Monat", "Termin", "Stadt", "Standort_Typ",
    "Besucherzahlen", "Ausstellerzahlen",
    "Angebotsschwerpunkt", "Branchenschwerpunkt",
    "Zutritt", "Turnus", "Veranstalter",
    "FKM_Zertifiziert", "Detail_URL",
]

OVERVIEW_API = (
    "https://www.auma.de/api/TradeFairData/getWebOverviewTradeFairData"
    "?intFilterYearFrom={yf}&intFilterYearTo={yt}"
    "&intFilterMonthFrom=1&intFilterMonthTo=12&strLanguage=de"
)
DETAIL_API = "https://www.auma.de/api/TradeFairData/getWebDetailTradeFairData?intId={id}&strLanguage=de"
AUMA_BASE  = "https://www.auma.de"

HEADERS = {"User-Agent": "Mozilla/5.0 (AUMA-Scraper/3.0)"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fetch_overview(year_from, year_to):
    url = OVERVIEW_API.format(yf=year_from, yt=year_to)
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def extract_year(termin):
    m = re.search(r"(20\d{2})", termin)
    return m.group(1) if m else ""


def extract_month(termin):
    m = re.match(r"\d{2}\.(\d{2})\.", termin)
    return m.group(1) if m else ""


def standort_typ(city):
    if city in A_STANDORTE: return "A"
    if city in B_STANDORTE: return "B"
    return ""


def clean_number(val):
    """'4.292' or '4,292' → '4292'"""
    if val is None:
        return ""
    s = str(val).strip().replace(".", "").replace(",", "").replace(" ", "")
    return s if s.isdigit() else str(val).strip()


def get_detail_url(fair):
    for key in ("strUrl", "strLink", "strDetailUrl", "strHref", "strPath", "strSlug"):
        val = fair.get(key, "")
        if val:
            return val if val.startswith("http") else AUMA_BASE + val
    fair_id = fair.get("intId") or fair.get("intFairId") or fair.get("id")
    if fair_id:
        return f"{AUMA_BASE}/de/messesuche/{fair_id}"
    return ""


# ---------------------------------------------------------------------------
# Strategy 1: detail API
# ---------------------------------------------------------------------------

def try_detail_api(fair_id):
    if not fair_id:
        return {}
135|     try:
136|         r = requests.get(DETAIL_API.format(id=fair_id), headers=HEADERS, timeout=15)
137|         r.raise_for_status()  # Fehler bei Status != 200 werfen
138|         d = r.json()
139|         if isinstance(d, list) and d:
140|             d = d[0]
141|         besucher   = clean_number(d.get("intBesucher") or d.get("strBesucher") or d.get("Besucher"))
142|         aussteller = clean_number(d.get("intAussteller") or d.get("strAussteller") or d.get("Aussteller"))
143|         if besucher or aussteller:
144|             return {
145|                 "Besucherzahlen":      besucher,
146|                 "Ausstellerzahlen":    aussteller,
147|                 "Reichweite":          d.get("strReichweite", ""),
148|                 "Angebotsschwerpunkt": d.get("strAngebotsschwerpunkt", ""),
149|             }
150|     except requests.Timeout:
151|         logger.warning(f"Detail API timeout for fair {fair_id}")
152|     except requests.HTTPError as e:
153|         logger.warning(f"Detail API HTTP error for fair {fair_id}: {e}")
154|     except ValueError:  # JSON-Parsing-Fehler
155|         logger.warning(f"Detail API returned invalid JSON for fair {fair_id}")
156|     except Exception as e:
157|         logger.error(f"Unexpected error in detail API for fair {fair_id}: {e}")
158|     return {}

# ---------------------------------------------------------------------------
# Strategy 2: Playwright + BeautifulSoup
# ---------------------------------------------------------------------------

def parse_statistics_from_html(html: str, debug_path: Path = None) -> dict:
    """
    Scan ALL trade-fair-statistics-table rows on the page.
    Match labels exactly against the known AUMA strings:
      - "Besucher (Zahl der Eintritte)"  → Besucherzahlen
      - "Aussteller"                      → Ausstellerzahlen
    Also picks up Reichweite and Angebotsschwerpunkt.
    """
    soup = BeautifulSoup(html, "html.parser")
    result = {}

    if debug_path:
        debug_path.write_text(html, encoding="utf-8")
        print(f"  [DEBUG] HTML saved to {debug_path}")

    # Collect all statistic rows anywhere on the page
    all_rows = soup.select(".trade-fair-statistics-table__row--lvl-2")

    for row in all_rows:
        # Key cell has BOTH classes; value cell has only trade-fair-statistics-table__item
        key_cell = row.select_one(".trade-fair-statistics-table__key")
        val_cells = row.select(".trade-fair-statistics-table__item")

        if not key_cell or not val_cells:
            continue

        label = key_cell.get_text(strip=True).lower()
        # Last item cell that is NOT also a key is the value
        value_cell = val_cells[-1] if val_cells else None
        if value_cell is None:
            continue
        value = value_cell.get_text(strip=True)

        if LABEL_BESUCHER in label and "Besucherzahlen" not in result:
            result["Besucherzahlen"] = clean_number(value)

        elif label == LABEL_AUSSTELLER and "Ausstellerzahlen" not in result:
            result["Ausstellerzahlen"] = clean_number(value)

        elif label == LABEL_ANGEBOTSSCHWERPUNKT and "Angebotsschwerpunkt" not in result:
            result["Angebotsschwerpunkt"] = value

        elif label == LABEL_BRANCHENSCHWERPUNKT and "Branchenschwerpunkt" not in result:
            result["Branchenschwerpunkt"] = value

        elif label == LABEL_ZUTRITT and "Zutritt" not in result:
            result["Zutritt"] = value

        elif label == LABEL_VERANSTALTER and "Veranstalter" not in result:
            result["Veranstalter"] = value

        elif label == LABEL_TURNUS and "Turnus" not in result:
            result["Turnus"] = value

    # Debug: print what we found
    if debug_path:
        print(f"  [DEBUG] Parsed stats: {result}")
        # Also print all unique labels found so we can verify
        labels_found = []
        for row in all_rows:
            k = row.select_one(".trade-fair-statistics-table__key")
            if k:
                labels_found.append(k.get_text(strip=True))
        print(f"  [DEBUG] All labels found: {labels_found}")

    return result


def scrape_with_playwright(url: str, debug_path: Path = None) -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [WARN] playwright not installed")
        return {}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(user_agent="Mozilla/5.0 (AUMA-Scraper/3.0)")
            page.goto(url, wait_until="networkidle", timeout=30000)
            # Expand every accordion/collapse so stats render in DOM
            page.evaluate("""
                document.querySelectorAll(
                  '.accordion__collapse, .collapse, [data-bs-toggle="collapse"]'
                ).forEach(el => el.classList.add('show'));
            """)
            time.sleep(1.5)
            html = page.content()
            browser.close()
        return parse_statistics_from_html(html, debug_path=debug_path)
    except Exception as exc:
        print(f"  [WARN] Playwright error: {exc}")
        return {}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="AUMA FKM Messen Scraper v3")
    parser.add_argument("--year-from",       type=int, default=2026)
    parser.add_argument("--year-to",         type=int, default=2032)
    parser.add_argument("--all-cities",      action="store_true")
    parser.add_argument("--include-non-fkm", action="store_true")
    parser.add_argument("--no-browser",      action="store_true")
    parser.add_argument("--output",          default="AUMA_FKM_Messen.csv")
    parser.add_argument("--delay",           type=float, default=1.5)
    parser.add_argument("--debug",           action="store_true",
                        help="Dump first API record fields + save first detail page HTML")
    args = parser.parse_args()

    print(f"Fetching AUMA overview {args.year_from}–{args.year_to} …")
    raw = fetch_overview(args.year_from, args.year_to)
    print(f"Total API records: {len(raw)}")

    # Debug: show all field names in the first record
    if args.debug and raw:
        first = raw[0]
        print("\n[DEBUG] API field names in first record:")
        for k, v in first.items():
            print(f"  {k!r:35s} = {str(v)[:80]}")
        Path("debug_api_first_record.json").write_text(
            json.dumps(first, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print("[DEBUG] Saved to debug_api_first_record.json\n")

    rows = []
    debug_saved = False

    for i, fair in enumerate(raw):
        city = fair.get("strStadt", "")
        if not args.all_cities and city not in ALL_TARGET_CITIES:
            continue
        if not args.include_non_fkm and not fair.get("blnFKM"):
            continue

        termin     = fair.get("strTermin", "")
        detail_url = get_detail_url(fair)
        fair_id    = fair.get("intId") or fair.get("intFairId") or fair.get("id")

        row = {
            "Messe":                fair.get("strTitel", ""),
            "Jahr":                 extract_year(termin),
            "Monat":                extract_month(termin),
            "Termin":               termin,
            "Stadt":                city,
            "Standort_Typ":         standort_typ(city),
            "Besucherzahlen":       "",
            "Ausstellerzahlen":     "",
            "Angebotsschwerpunkt":  "",
            "Branchenschwerpunkt":  "",
            "Zutritt":              "",
            "Turnus":               "",
            "Veranstalter":         "",
            "FKM_Zertifiziert":     "Ja" if fair.get("blnFKM") else "Nein",
            "Detail_URL":           detail_url,
        }

        print(f"  [{i+1}] {row['Messe'][:50]} …", end=" ", flush=True)

        # Strategy 1: detail API
        stats = try_detail_api(fair_id)

        # Strategy 2: Playwright
        if not stats and not args.no_browser and detail_url:
            time.sleep(args.delay)
            dbg_path = Path("debug_first_page.html") if (args.debug and not debug_saved) else None
            stats = scrape_with_playwright(detail_url, debug_path=dbg_path)
            if dbg_path:
                debug_saved = True

        if stats:
            row.update(stats)
            print(f"✓  Besucher={row['Besucherzahlen']}  Aussteller={row['Ausstellerzahlen']}")
        else:
            print("– no stats found")

        rows.append(row)

    rows.sort(key=lambda r: (r["Jahr"], r["Monat"].zfill(2), r["Stadt"]))

    out_path = Path(args.output)
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS, delimiter=";",
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    filled = sum(1 for r in rows if r["Besucherzahlen"])
    print(f"\nExportiert: {len(rows)} Messen  |  Besucherzahlen gefunden: {filled}/{len(rows)}")
    print(f"Gespeichert: {out_path.resolve()}")


if __name__ == "__main__":
    main()
