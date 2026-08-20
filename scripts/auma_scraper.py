import requests
import csv

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
        "Termin": fair.get("strTermin"),
        "Stadt": city
    })

print("Gefundene Messen:", len(rows))

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
            "Termin",
            "Stadt"
        ],
        delimiter=";"
    )

    writer.writeheader()
    writer.writerows(rows)

print("CSV geschrieben")
