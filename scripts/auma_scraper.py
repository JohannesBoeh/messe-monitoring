"""
AUMA Scraper  v2
================
Step 1 – Fetch fair list from AUMA overview API.
Step 2 – For each fair, try a detail API endpoint first; if that returns no
         stats, fall back to rendering the fair's HTML page with Playwright
         and scraping  .trade-fair-statistics-table__item  elements.

Install:
    pip install requests beautifulsoup4 playwright
    playwright install chromium

Run:
    python auma_scraper.py [--year-from 2026] [--year-to 2032]
                          [--all-cities] [--include-non-fkm]
                          [--no-browser]        # skip Playwright fallback
                          [--output AUMA_FKM_Messen.csv]
"""

import argparse
import csv
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

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

OUTPUT_FIELDS = [
    "Messe", "Jahr", "Monat", "Termin", "Stadt", "Standort_Typ",
    "Besucherzahlen", "Ausstellerzahlen",
    "Reichweite", "Angebotsschwerpunkt",
    "FKM_Zertifiziert", "Turnus", "Veranstalter",
    "Detail_URL",
]

OVERVIEW_API = (
    "https://www.auma.de/api/TradeFairData/getWebOverviewTradeFairData"
    "?intFilterYearFrom={yf}&intFilterYearTo={yt}"
    "&intFilterMonthFrom=1&intFilterMonthTo=12&strLanguage=de"
)

# Candidate detail-API endpoint (may or may not exist — tried first)
DETAIL_API = "https://www.auma.de/api/TradeFairData/getWebDetailTradeFairData?intId={id}&strLanguage=de"

AUMA_BASE = "https://www.auma.de"

HEADERS = {"User-Agent": "Mozilla/5.0 (AUMA-Scraper/2.0)"}


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
    if city in A_STANDORTE:
        return "A"
    if city in B_STANDORTE:
        return "B"
    return ""


def clean_number(val):
    """Turn '4.292' or '4,292' or 4292 into '4292'."""
    if val is None:
        return ""
    s = str(val).strip()
    # German thousands separator is "." — remove it
    s = s.replace(".", "").replace(",", "").replace(" ", "")
    return s if s.isdigit() else str(val).strip()


# ---------------------------------------------------------------------------
# Strategy 1: detail API
# ---------------------------------------------------------------------------

def try_detail_api(fair_id):
    """Return dict with Besucherzahlen/Ausstellerzahlen or empty dict."""
    if not fair_id:
        return {}
    try:
        r = requests.get(DETAIL_API.format(id=fair_id), headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return {}
        d = r.json()
        if isinstance(d, list) and d:
            d = d[0]
        besucher    = clean_number(d.get("intBesucher") or d.get("strBesucher") or d.get("Besucher"))
        aussteller  = clean_number(d.get("intAussteller") or d.get("strAussteller") or d.get("Aussteller"))
        reichweite  = d.get("strReichweite", "")
        schwerpunkt = d.get("strAngebotsschwerpunkt", "")
        if besucher or aussteller:
            return {
                "Besucherzahlen":   besucher,
                "Ausstellerzahlen": aussteller,
                "Reichweite":       reichweite,
                "Angebotsschwerpunkt": schwerpunkt,
            }
    except Exception:
        pass
    return {}


# ---------------------------------------------------------------------------
# Strategy 2: Playwright HTML scraping
# ---------------------------------------------------------------------------

def parse_statistics_from_html(html: str) -> dict:
    """
    Parse the AUMA fair-detail HTML page.

    The page contains accordion sections, e.g.:
        <div id="collapseVisitors">
          <div class="trade-fair-statistics-table__row trade-fair-statistics-table__row--lvl-2">
            <div class="trade-fair-statistics-table__key ...">Besucher gesamt</div>
            <div class="trade-fair-statistics-table__item">4.292</div>
          </div>
          ...
        </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    result = {}

    # ---- Visitors ----
    visitors_div = soup.find(id="collapseVisitors")
    if visitors_div:
        rows = visitors_div.select(
            ".trade-fair-statistics-table__row--lvl-2"
        )
        for row in rows:
            cells = row.select(".trade-fair-statistics-table__item")
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True).lower()
                value = cells[-1].get_text(strip=True)
                if "gesamt" in label or "total" in label or "besucher" in label:
                    result["Besucherzahlen"] = clean_number(value)
                    break
        # Fallback: first value in the section
        if "Besucherzahlen" not in result:
            first_val = visitors_div.select_one(".trade-fair-statistics-table__item:last-child")
            if first_val:
                result["Besucherzahlen"] = clean_number(first_val.get_text(strip=True))

    # ---- Exhibitors ----
    exhibitors_div = soup.find(id="collapseExhibitors") or soup.find(id="collapseAussteller")
    if exhibitors_div:
        rows = exhibitors_div.select(".trade-fair-statistics-table__row--lvl-2")
        for row in rows:
            cells = row.select(".trade-fair-statistics-table__item")
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True).lower()
                value = cells[-1].get_text(strip=True)
                if "gesamt" in label or "total" in label or "aussteller" in label:
                    result["Ausstellerzahlen"] = clean_number(value)
                    break
        if "Ausstellerzahlen" not in result:
            first_val = exhibitors_div.select_one(".trade-fair-statistics-table__item:last-child")
            if first_val:
                result["Ausstellerzahlen"] = clean_number(first_val.get_text(strip=True))

    # ---- Reichweite / Schwerpunkt (look in any lvl-2 row) ----
    for row in soup.select(".trade-fair-statistics-table__row--lvl-2"):
        cells = row.select(".trade-fair-statistics-table__item")
        if len(cells) >= 2:
            label = cells[0].get_text(strip=True).lower()
            value = cells[-1].get_text(strip=True)
            if "reichweite" in label and "Reichweite" not in result:
                result["Reichweite"] = value
            if ("schwerpunkt" in label or "angebot" in label) and "Angebotsschwerpunkt" not in result:
                result["Angebotsschwerpunkt"] = value

    return result


def scrape_with_playwright(url: str) -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [WARN] playwright not installed — run: pip install playwright && playwright install chromium")
        return {}

    result = {}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(user_agent="Mozilla/5.0 (AUMA-Scraper/2.0)")
            page.goto(url, wait_until="networkidle", timeout=30000)

            # Expand all accordion sections so the stats are in the DOM
            page.evaluate("""
                document.querySelectorAll('.accordion__collapse, .collapse').forEach(el => {
                    el.classList.add('show');
                });
            """)
            time.sleep(1)

            html = page.content()
            browser.close()
            result = parse_statistics_from_html(html)
    except Exception as exc:
        print(f"  [WARN] Playwright failed for {url}: {exc}")
    return result


# ---------------------------------------------------------------------------
# Build detail URL from API fields
# ---------------------------------------------------------------------------

def get_detail_url(fair: dict) -> str:
    """Construct the fair's detail page URL from API data."""
    # Try common URL fields the API might return
    for key in ("strUrl", "strLink", "strDetailUrl", "strHref", "strPath"):
        val = fair.get(key, "")
        if val:
            return val if val.startswith("http") else AUMA_BASE + val

    # Fall back: build from fair ID
    fair_id = fair.get("intId") or fair.get("intFairId") or fair.get("id")
    if fair_id:
        return f"{AUMA_BASE}/de/messesuche/{fair_id}"

    return ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="AUMA FKM Messen Scraper v2")
    parser.add_argument("--year-from",       type=int, default=2026)
    parser.add_argument("--year-to",         type=int, default=2032)
    parser.add_argument("--all-cities",      action="store_true")
    parser.add_argument("--include-non-fkm", action="store_true")
    parser.add_argument("--no-browser",      action="store_true",
                        help="Skip Playwright; only use the detail API")
    parser.add_argument("--output",          default="AUMA_FKM_Messen.csv")
    parser.add_argument("--delay",           type=float, default=1.0,
                        help="Seconds to wait between detail page requests")
    args = parser.parse_args()

    print(f"Fetching AUMA overview {args.year_from}–{args.year_to} …")
    raw = fetch_overview(args.year_from, args.year_to)
    print(f"Total API records: {len(raw)}")

    rows = []
    for i, fair in enumerate(raw):
        city = fair.get("strStadt", "")

        if not args.all_cities and city not in ALL_TARGET_CITIES:
            continue
        if not args.include_non_fkm and not fair.get("blnFKM"):
            continue

        termin = fair.get("strTermin", "")
        detail_url = get_detail_url(fair)

        row = {
            "Messe":            fair.get("strTitel", ""),
            "Jahr":             extract_year(termin),
            "Monat":            extract_month(termin),
            "Termin":           termin,
            "Stadt":            city,
            "Standort_Typ":     standort_typ(city),
            "Besucherzahlen":   "",
            "Ausstellerzahlen": "",
            "Reichweite":       fair.get("strReichweite", ""),
            "Angebotsschwerpunkt": fair.get("strAngebotsschwerpunkt", ""),
            "FKM_Zertifiziert": "Ja" if fair.get("blnFKM") else "Nein",
            "Turnus":           fair.get("strTurnus", ""),
            "Veranstalter":     fair.get("strVeranstalter", ""),
            "Detail_URL":       detail_url,
        }

        fair_id = fair.get("intId") or fair.get("intFairId") or fair.get("id")
        messe   = row["Messe"]
        print(f"  [{i+1}] {messe[:50]} …", end=" ", flush=True)

        # Strategy 1: detail API
        stats = try_detail_api(fair_id)

        # Strategy 2: Playwright HTML scrape
        if not stats and not args.no_browser and detail_url:
            time.sleep(args.delay)
            stats = scrape_with_playwright(detail_url)

        if stats:
            row.update(stats)
            print(f"✓ Besucher={row['Besucherzahlen']}  Aussteller={row['Ausstellerzahlen']}")
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

