import requests
import csv
import re

TARGET_CITIES = [
    "Berlin",
    "Düsseldorf",
    "Frankfurt am Main",
    "Hamburg",
    "Köln",
    "Leipzig",
    "München",
    "Stuttgart"
]

API_URL = (
    "https://www.auma.de/api/TradeFairData/"
    "getWebOverviewTradeFairData"
    "?intFilterYearFrom=2026"
    "&intFilterYearTo=2032"
    "&intFilterMonthFrom=1"
    "&intFilterMonthTo=12"
    "&strLanguage=de"
)

response = requests.get(
    API_URL,
    headers={"User-Agent": "Mozilla/5.0"}
)

data = response.json()

rows = []

for fair in data:

    city = fair.get("strStadt", "")

    if city not in TARGET_CITIES:
        continue

    if not fair.get("blnFKM"):
        continue

    termin = fair.get("strTermin", "")

    jahr = ""
    monat = ""

    jahr_match = re.search(r"(20\d{2})", termin)

    if jahr_match:
        jahr = jahr_match.group(1)

    monat_match = re.match(r"(\d{2})\.", termin)

    if monat_match:
        monat = monat_match.group(1)

    rows.append({
        "Messe": fair.get("strTitel"),
        "Jahr": jahr,
        "Monat": monat,
        "Termin": termin,
        "Stadt": city
    })

with open(
    "AUMA_FKM_Messen.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
