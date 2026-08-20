import argparse
import csv
import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Exact label strings as shown on AUMA website (lowercased for matching)
# ---------------------------------------------------------------------------
LABEL_BESUCHER            = "besucher (zahl der eintritte)"
LABEL_AUSSTELLER          = "aussteller"
LABEL_ANGEBOTSSCHWERPUNKT = "angebotsschwerpunkte"
LABEL_BRANCHENSCHWERPUNKT = "branchenschwerpunkte"
LABEL_ZUTRITT             = "zutritt"
LABEL_VERANSTALTER        = "veranstalter"
LABEL_TURNUS              = "turnus:"

A_STANDORTE = [
    "Berlin", "Duesseldorf", "Dusseldorf", "Dusseldorf", "Duesseldorf",
    "Hamburg", "Koeln", "Koln", "Leipzig", "Munchen", "Munich", "Stuttgart",
    "Frankfurt am Main", "Frankfurt", "Dusseldorf",
    # With umlauts
    "Düsseldorf", "Köln", "München",
]
A_STANDORTE_CLEAN = [
    "Berlin", "Düsseldorf", "Frankfurt am Main",
    "Hamburg", "Köln", "Leipzig", "München", "Stuttgart",
]
B_STANDORTE = [
    "Hannover", "Nürnberg", "Essen", "Dortmund", "Friedrichshafen",
    "Freiburg", "Bremen", "Dresden", "Erfurt", "Karlsruhe",
]
ALL_TARGET_CITIES = A_STANDORTE_CLEAN + B_STANDORTE

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
DETAIL_API = (
    "https://www.auma.de/api/TradeFairData/getWebDetailTradeFairData"
    "?intId={id}&strLanguage=de"
)
AUMA_BASE = "https://www.auma.de"
HEADERS = {"User-Agent": "Mozilla/5.0 (AUMA-Scraper/4.0)"}


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
    if city in A_STANDORTE_CLEAN:
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
    for key in ("strUrl", "strLink", "strDetailUrl", "strHref", "strPath", "strSlug", "strDetailLink"):
        val = fair.get(key, "")
        if val:
            return val if val.startswith("http") else AUMA_BASE + val
    fair_id = fair.get("intId") or fair.get("intFairId") or fair.get("id")
    if fair_id:
        return "{}/de/messesuche/{}".format(AUMA_BASE, fair_id)
    return ""


def try_detail_api(fair_id):
    if not fair_id:
        return {}
    try:
        r = requests.get(DETAIL_API.format(id=fair_id), headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return {}
        d = r.json()
        if isinstance(d, list) and d:
            d = d[0]
        besucher   = clean_number(d.get("intBesucher") or d.get("strBesucher") or d.get("Besucher"))
        aussteller = clean_number(d.get("intAussteller") or d.get("strAussteller") or d.get("Aussteller"))
        if besucher or aussteller:
            return {
                "Besucherzahlen":      besucher,
                "Ausstellerzahlen":    aussteller,
                "Reichweite":          d.get("strReichweite", ""),
                "Angebotsschwerpunkt": d.get("strAngebotsschwerpunkt", ""),
            }
    except Exception:
        pass
    return {}


def parse_statistics_from_html(html, debug=False):
    soup = BeautifulSoup(html, "html.parser")
    result = {}

    all_rows = soup.select(".trade-fair-statistics-table__row--lvl-2")

    if debug:
        labels_found = []
        for row in all_rows:
            k = row.select_one(".trade-fair-statistics-table__key")
            if k:
                labels_found.append(k.get_text(strip=True))
        print("  [DEBUG] Labels found in HTML: {}".format(labels_found))

    for row in all_rows:
        key_cell = row.select_one(".trade-fair-statistics-table__key")
        val_cells = row.select(".trade-fair-statistics-table__item")
        if not key_cell or not val_cells:
            continue
        label = key_cell.get_text(strip=True).lower()
        value = val_cells[-1].get_text(strip=True)

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

    return result


def scrape_with_playwright(url, debug=False):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [WARN] playwright not installed")
        return {}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(user_agent="Mozilla/5.0 (AUMA-Scraper/4.0)")
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.evaluate(
                "document.querySelectorAll('.accordion__collapse,.collapse').forEach(el=>el.classList.add('show'));"
            )
            time.sleep(1.5)
            html = page.content()
            if debug:
                Path("debug_first_page.html").write_text(html, encoding="utf-8")
                print("  [DEBUG] Saved debug_first_page.html")
            browser.close()
        return parse_statistics_from_html(html, debug=debug)
    except Exception as exc:
        print("  [WARN] Playwright error: {}".format(exc))
        return {}


def main():
    parser = argparse.ArgumentParser(description="AUMA FKM Messen Scraper v4")
    parser.add_argument("--year-from",       type=int, default=2026)
    parser.add_argument("--year-to",         type=int, default=2032)
    parser.add_argument("--all-cities",      action="store_true")
    parser.add_argument("--include-non-fkm", action="store_true")
    parser.add_argument("--no-browser",      action="store_true")
    parser.add_argument("--output",          default="AUMA_FKM_Messen.csv")
    parser.add_argument("--delay",           type=float, default=1.5)
    parser.add_argument("--debug",           action="store_true",
                        help="Print API fields + save first detail page HTML")
    args = parser.parse_args()

    print("Fetching AUMA overview {} - {} ...".format(args.year_from, args.year_to))
    raw = fetch_overview(args.year_from, args.year_to)
    print("Total API records: {}".format(len(raw)))

    if args.debug and raw:
        first = raw[0]
        print("\n[DEBUG] All API field names in first record:")
        for k, v in first.items():
            print("  {!r:40s} = {}".format(k, str(v)[:100]))
        Path("debug_api_first_record.json").write_text(
            json.dumps(first, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    rows = []
    debug_done = False

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

        print("  [{}] {} ...".format(i + 1, row["Messe"][:50]), end=" ", flush=True)

        stats = try_detail_api(fair_id)

        if not stats and not args.no_browser and detail_url:
            time.sleep(args.delay)
            do_debug = args.debug and not debug_done
            stats = scrape_with_playwright(detail_url, debug=do_debug)
            if do_debug:
                debug_done = True

        if stats:
            row.update(stats)
            print("OK Besucher={} Aussteller={}".format(
                row["Besucherzahlen"], row["Ausstellerzahlen"]))
        else:
            print("- no stats (url={})".format(detail_url[:60] if detail_url else "EMPTY"))

        rows.append(row)

    rows.sort(key=lambda r: (r["Jahr"], r["Monat"].zfill(2), r["Stadt"]))

    out_path = Path(args.output)
    with open(str(out_path), "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS, delimiter=";",
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    filled = sum(1 for r in rows if r["Besucherzahlen"])
    print("\nExportiert: {} Messen | Besucherzahlen gefunden: {}/{}".format(
        len(rows), filled, len(rows)))
    print("Gespeichert: {}".format(out_path.resolve()))


if __name__ == "__main__":
    main()
