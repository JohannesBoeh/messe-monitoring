import requests
import csv
from bs4 import BeautifulSoup

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

    rows.append({
        "Messe": fair.get("strTitel"),
        "Jahr": "2026",
        "Monat": fair.get("strTermin", "")[:2],
        "Termin": fair.get("strTermin"),
        "Stadt": city,
        "Turnus": "",
        "Besucherzahl": "",
        "Ausstellerzahl": ""
    })

    if len(rows) >= 10:
        break

with open(
    "AUMA_FKM_Messen.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "Messe",
            "Jahr",
            "Monat",
            "Termin",
            "Stadt",
            "
