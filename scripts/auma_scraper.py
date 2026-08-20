"""
AUMA Scraper
============
Fetches trade fair data from the AUMA API and exports a CSV with:
  Messe, Jahr, Monat, Termin, Stadt,
  Besucherzahlen, Ausstellerzahlen, Reichweite, Angebotsschwerpunkt

Only FKM-certified fairs (blnFKM = true) at A-/B-Standorte are included.
Run:  python auma_scraper.py [--year-from 2026] [--year-to 2032] [--all-cities]
"""

import argparse
import csv
import re
import sys
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

A_STANDORTE = [
    "Berlin",
    "Düsseldorf",
    "Frankfurt am Main",
    "Hamburg",
    "Köln",
    "Leipzig",
    "München",
    "Stuttgart",
]

# Add known B-Standorte here if needed
B_STANDORTE = [
    "Hannover",
    "Nürnberg",
    "Essen",
    "Dortmund",
    "Friedrichshafen",
    "Freiburg",
    "Bremen",
    "Dresden",
    "Erfurt",
    "Karlsruhe",
]

ALL_TARGET_CITIES = A_STANDORTE + B_STANDORTE

OUTPUT_FIELDS = [
    "Messe",
    "Jahr",
    "Monat",
    "Termin",
    "Stadt",
    "Standort_Typ",        # A or B
    "Besucherzahlen",
    "Ausstellerzahlen",
    "Reichweite",          # national / international
    "Angebotsschwerpunkt",
    "FKM_Zertifiziert",
    "Turnus",              # annual / biennial etc.
    "Veranstalter",
]

API_BASE = "https://www.auma.de/api/TradeFairData/getWebOverviewTradeFairData"

HEADERS = {"User-Agent": "Mozilla/5.0 (AUMA-Scraper/1.0)"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fetch_data(year_from: int, year_to: int, language: str = "de") -> list:
    url = (
        f"{API_BASE}"
        f"?intFilterYearFrom={year_from}"
        f"&intFilterYearTo={year_to}"
        f"&intFilterMonthFrom=1"
        f"&intFilterMonthTo=12"
        f"&strLanguage={language}"
    )
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as exc:
        print(f"[ERROR] API request failed: {exc}", file=sys.stderr)
        sys.exit(1)


def extract_year(termin: str) -> str:
    m = re.search(r"(20\d{2})", termin)
    return m.group(1) if m else ""


def extract_month(termin: str) -> str:
    # Typical format: "15.03. – 19.03.2026" → month = "03"
    m = re.match(r"\d{2}\.(\d{2})\.", termin)
    return m.group(1) if m else ""


def standort_typ(city: str) -> str:
    if city in A_STANDORTE:
        return "A"
    if city in B_STANDORTE:
        return "B"
    return ""


def parse_fair(fair: dict) -> dict:
    termin = fair.get("strTermin", "")
    city   = fair.get("strStadt", "")

    # Visitor / exhibitor counts — AUMA API field names observed in the wild.
    # The API may return integers or formatted strings; normalise to plain int string.
    def _int(val):
        if val is None:
            return ""
        s = str(val).replace(".", "").replace(",", "").strip()
        return s if s.isdigit() else str(val)

    return {
        "Messe":            fair.get("strTitel", ""),
        "Jahr":             extract_year(termin),
        "Monat":            extract_month(termin),
        "Termin":           termin,
        "Stadt":            city,
        "Standort_Typ":     standort_typ(city),
        "Besucherzahlen":   _int(fair.get("intBesucher") or fair.get("strBesucher")),
        "Ausstellerzahlen": _int(fair.get("intAussteller") or fair.get("strAussteller")),
        "Reichweite":       fair.get("strReichweite", ""),
        "Angebotsschwerpunkt": fair.get("strAngebotsschwerpunkt", ""),
        "FKM_Zertifiziert": "Ja" if fair.get("blnFKM") else "Nein",
        "Turnus":           fair.get("strTurnus", ""),
        "Veranstalter":     fair.get("strVeranstalter", ""),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="AUMA FKM Messen Scraper")
    parser.add_argument("--year-from", type=int, default=2026)
    parser.add_argument("--year-to",   type=int, default=2032)
    parser.add_argument("--all-cities", action="store_true",
                        help="Include all cities, not just A/B Standorte")
    parser.add_argument("--include-non-fkm", action="store_true",
                        help="Include fairs without FKM certification")
    parser.add_argument("--output", default="AUMA_FKM_Messen.csv",
                        help="Output CSV file path")
    parser.add_argument("--language", default="de", choices=["de", "en"])
    args = parser.parse_args()

    print(f"Fetching AUMA data {args.year_from}–{args.year_to} …")
    raw = fetch_data(args.year_from, args.year_to, args.language)
    print(f"Total records from API: {len(raw)}")

    rows = []
    skipped_city = 0
    skipped_fkm  = 0

    for fair in raw:
        city = fair.get("strStadt", "")

        # City filter
        if not args.all_cities and city not in ALL_TARGET_CITIES:
            skipped_city += 1
            continue

        # FKM filter
        if not args.include_non_fkm and not fair.get("blnFKM"):
            skipped_fkm += 1
            continue

        rows.append(parse_fair(fair))

    # Sort by Jahr → Monat → Stadt
    rows.sort(key=lambda r: (r["Jahr"], r["Monat"].zfill(2), r["Stadt"]))

    out_path = Path(args.output)
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS, delimiter=";",
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nExportiert:         {len(rows)} Messen")
    print(f"Übersprungen (Stadt): {skipped_city}")
    print(f"Übersprungen (FKM):   {skipped_fkm}")
    print(f"Gespeichert unter:  {out_path.resolve()}")


if __name__ == "__main__":
    main()
