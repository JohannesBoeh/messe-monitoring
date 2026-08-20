#!/usr/bin/env python3
"""
AUMA Scraper v4 - fixed

Usage:
  python scripts/auma_scraper.py [--year-from 2026] [--year-to 2032] [--all-cities]
                                [--include-non-fkm] [--no-browser] [--debug]
                                [--output AUMA_FKM_Messen.csv]
"""
import argparse
import csv
import json
import logging
import re
import time
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Labels (lowercased for matching)
# ---------------------------------------------------------------------------
LABEL_BESUCHER = "besucher (zahl der eintritte)"
LABEL_AUSSTELLER = "aussteller"
LABEL_ANGEBOTSSCHWERPUNKT = "angebotsschwerpunkte"
LABEL_BRANCHENSCHWERPUNKT = "branchenschwerpunkte"
LABEL_ZUTRITT = "zutritt"
LABEL_VERANSTALTER = "veranstalter"
LABEL_TURNUS = "turnus"  # normalized without ':'

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
AUMA_BASE = "https://www.auma.de"
HEADERS = {"User-Agent": "Mozilla/5.0 (AUMA-Scraper/4.0)"}

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")


# ---------------------------------------------------------------------------
# Requests session with retries
# ---------------------------------------------------------------------------
def get_session_with_retries(total=3, backoff_factor=0.8):
    session = requests.Session()
    retry_strategy = Retry(
        total=total,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
        backoff_factor=backoff_factor,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


SESSION = get_session_with_retries()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def fetch_overview(year_from, year_to):
    url = OVERVIEW_API.format(yf=year_from, yt=year_to)
    r = SESSION.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    payload = r.json()
    # Some API responses wrap list in top-level dict keys (data, Data, d, items, ...)
    if isinstance(payload, dict):
        for k in ("data", "Data", "d", "items", "Items"):
            if k in payload and isinstance(payload[k], list):
                return payload[k]
        # fallback: return first list value found
        for v in payload.values():
            if isinstance(v, list):
                return v
        return []
    return payload


def extract_year(termin):
    m = re.search(r"(20\d{2})", termin or "")
    return m.group(1) if m else ""


def extract_month(termin):
    if not termin:
        return ""
    # pattern like 12.03.2026 or 12.03.-15.03.2026
    m = re.search(r"\b\d{1,2}\.?(?P<mon>\d{2})\.\d{4}", termin)
    if m:
        return m.group("mon")
    # fallback: German month names detection
    m = re.search(r"(jan|feb|mär|mar|apr|mai|jun|jul|aug|sep|okt|nov|dez)", termin, flags=re.I)
    if m:
        names = {"jan": "01", "feb": "02", "mär": "03", "mar": "03", "apr": "04", "mai": "05", "jun": "06",
                 "jul": "07", "aug": "08", "sep": "09", "okt": "10", "nov": "11", "dez": "12"}
        return names.get(m.group(1).lower(), "")
    return ""


def standort_typ(city):
    if city in A_STANDORTE:
        return "A"
    if city in B_STANDORTE:
        return "B"
    return ""


def clean_number(val):
    if val is None:
        return ""
    s = str(val).strip().replace(".", "").replace(",", "").replace(" ", "")
    return s if s.isdigit() else str(val).strip()


def get_detail_url(fair):
    for key in ("strUrl", "strLink", "strDetailUrl", "strHref", "strPath", "strSlug", "strUrlParameter"):
        val = fair.get(key, "")
        if val:
            if val.startswith("http"):
                return val
            if not val.startswith("/"):
                val = "/" + val
            return AUMA_BASE + val
    fair_id = fair.get("intId") or fair.get("intFairId") or fair.get("id") or fair.get("strMesseTerminKey")
    if fair_id:
        return f"{AUMA_BASE}/de/messesuche/{fair_id}"
    return ""


# ---------------------------------------------------------------------------
# Strategy 1: detail API
# ---------------------------------------------------------------------------
def try_detail_api(fair_id):
    if not fair_id:
        return {}
    try:
        r = SESSION.get(DETAIL_API.format(id=fair_id), headers=HEADERS, timeout=15)
        r.raise_for_status()
        d = r.json()
        if isinstance(d, list) and d:
            d = d[0]
        if isinstance(d, dict):
            besucher = clean_number(d.get("intBesucher") or d.get("strBesucher") or d.get("Besucher"))
            aussteller = clean_number(d.get("intAussteller") or d.get("strAussteller") or d.get("Aussteller"))
            if besucher or aussteller:
                return {
                    "Besucherzahlen": besucher,
                    "Ausstellerzahlen": aussteller,
                    "Reichweite": d.get("strReichweite", ""),
                    "Angebotsschwerpunkt": d.get("strAngebotsschwerpunkt", ""),
                    "Branchenschwerpunkt": d.get("strBranchenschwerpunkt", "") or d.get("strBranchenSchwerpunkt", ""),
                }
    except Exception as e:
        logger.debug("Detail API error for %s: %s", fair_id, e)
    return {}


# ---------------------------------------------------------------------------
# Strategy 2: Playwright + BeautifulSoup
# ---------------------------------------------------------------------------
def parse_statistics_from_html(html: str, debug: bool = False) -> dict:
    soup = BeautifulSoup(html or "", "html.parser")
    result = {}

    selectors = [
        ".trade-fair-statistics-table__row--lvl-2",
        ".trade-fair-statistics-table__row",
        ".trade-fair-statistics-row",
        ".statistics__row",
        ".row-statistics",
    ]
    all_rows = []
    for sel in selectors:
        found = soup.select(sel)
        if found:
            all_rows = found
            break

    if not all_rows:
        parents = []
        for key_el in soup.select(".trade-fair-statistics-table__key, .statistics__key, .key"):
            if key_el.parent is not None:
                parents.append(key_el.parent)
        all_rows = parents

    if debug:
        labels_found = []
        for row in all_rows:
            k = row.select_one('.trade-fair-statistics-table__key, .statistics__key, .key, th')
            if k:
                labels_found.append(k.get_text(strip=True))
        print("  [DEBUG] Labels found in HTML:", labels_found)

    for row in all_rows:
        if not row:
            continue
        key_cell = row.select_one('.trade-fair-statistics-table__key, .statistics__key, .key, th')
        val_cells = row.select('.trade-fair-statistics-table__item, .statistics__item, .item, td')
        if not key_cell or not val_cells:
            continue
        label = key_cell.get_text(strip=True).lower().rstrip(":").strip()
        value = val_cells[-1].get_text(strip=True)

        if LABEL_BESUCHER in label and "Besucherzahlen" not in result:
            result["Besucherzahlen"] = clean_number(value)
        elif LABEL_AUSSTELLER in label and "Ausstellerzahlen" not in result:
            result["Ausstellerzahlen"] = clean_number(value)
        elif LABEL_ANGEBOTSSCHWERPUNKT in label and "Angebotsschwerpunkt" not in result:
            result["Angebotsschwerpunkt"] = value
        elif LABEL_BRANCHENSCHWERPUNKT in label and "Branchenschwerpunkt" not in result:
            result["Branchenschwerpunkt"] = value
        elif LABEL_ZUTRITT in label and "Zutritt" not in result:
            result["Zutritt"] = value
        elif LABEL_VERANSTALTER in label and "Veranstalter" not in result:
            result["Veranstalter"] = value
        elif LABEL_TURNUS in label and "Turnus" not in result:
            result["Turnus"] = value

    return result


def scrape_with_playwright(url: str, debug: bool = False) -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [WARN] playwright not installed")
        return {}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(user_agent=HEADERS.get("User-Agent"))
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.evaluate(
                "document.querySelectorAll('.accordion__collapse, .collapse, [data-bs-toggle]').forEach(el=>el.classList.add('show'))"
            )
            time.sleep(1.3)
            html = page.content()
            if debug:
                Path("debug_first_page.html").write_text(html, encoding="utf-8")
                print("  [DEBUG] Saved debug_first_page.html")
            browser.close()
        return parse_statistics_from_html(html, debug=debug)
    except Exception as exc:
        print("  [WARN] Playwright error:", exc)
        return {}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AUMA FKM Messen Scraper v4")
    parser.add_argument("--year-from", type=int, default=2026)
    parser.add_argument("--year-to", type=int, default=2032)
    parser.add_argument("--all-cities", action="store_true")
    parser.add_argument("--include-non-fkm", action="store_true")
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--output", default="AUMA_FKM_Messen.csv")
    parser.add_argument("--delay", type=float, default=1.5)
    parser.add_argument("--debug", action="store_true", help="Dump API fields + save first detail page HTML")
    args = parser.parse_args()

    print(f"Fetching AUMA overview {args.year_from}–{args.year_to} …")
    raw = fetch_overview(args.year_from, args.year_to)
    print(f"Total API records: {len(raw)}")

    if args.debug and raw:
        first = raw[0]
        print("\n[DEBUG] API field names in first record:")
        for k, v in first.items():
            print(f"  {k!r:40s} = {str(v)[:200]}")
        Path("debug_api_first_record.json").write_text(json.dumps(first, indent=2, ensure_ascii=False), encoding="utf-8")
        print("[DEBUG] Saved to debug_api_first_record.json\n")

    rows = []
    debug_saved = False

    for i, fair in enumerate(raw):
        city = fair.get("strStadt", "")
        if not args.all_cities and city not in ALL_TARGET_CITIES:
            continue
        if not args.include_non_fkm and not fair.get("blnFKM"):
            continue

        termin = fair.get("strTermin", "")
        detail_url = get_detail_url(fair)
        fair_id = fair.get("intId") or fair.get("intFairId") or fair.get("id") or fair.get("strMesseTerminKey")

        row = {
            "Messe": fair.get("strTitel", ""),
            "Jahr": extract_year(termin),
            "Monat": extract_month(termin),
            "Termin": termin,
            "Stadt": city,
            "Standort_Typ": standort_typ(city),
            "Besucherzahlen": "",
            "Ausstellerzahlen": "",
            "Angebotsschwerpunkt": "",
            "Branchenschwerpunkt": "",
            "Zutritt": "",
            "Turnus": "",
            "Veranstalter": "",
            "FKM_Zertifiziert": "Ja" if fair.get("blnFKM") else "Nein",
            "Detail_URL": detail_url,
        }

        print(f"  [{i+1}] {row['Messe'][:50]} …", end=" ", flush=True)

        # Strategy 1: detail API
        stats = try_detail_api(fair_id)

        # Strategy 2: Playwright
        if not stats and not args.no_browser and detail_url:
            time.sleep(args.delay)
            dbg = args.debug and not debug_saved
            stats = scrape_with_playwright(detail_url, debug=dbg)
            if dbg:
                debug_saved = True

        if stats:
            row.update(stats)
            print(f"✓  Besucher={row.get('Besucherzahlen','')}  Aussteller={row.get('Ausstellerzahlen','')}")
        else:
            print("– no stats found")

        rows.append(row)

    rows.sort(key=lambda r: (r["Jahr"], (r["Monat"] or "00").zfill(2), r["Stadt"]))

    out_path = Path(args.output)
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    filled = sum(1 for r in rows if r.get("Besucherzahlen"))
    print(f"\nExportiert: {len(rows)} Messen  |  Besucherzahlen gefunden: {filled}/{len(rows)}")
    print(f"Gespeichert: {out_path.resolve()}")


if __name__ == '__main__':
    main()
