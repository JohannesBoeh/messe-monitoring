import requests
import csv

TARGET_CITIES = [
    "Berlin",
    "Düsseldorf",
    "Frankfurt",
    "Hamburg",
    "Köln",
    "Leipzig",
    "München",
    "Stuttgart"
]

url = (
    "https://www.auma.de/api/TradeFairData/"
    "getWebOverviewTradeFairData"
    "?intFilterYearFrom=2026"
    "&intFilterYearTo=2032"
    "&intFilterMonthFrom=1"
    "&intFilterMonthTo=12"
    "&strLanguage=de"
)

response = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
)

data = response.json()

rows = []

for fair in data:

    city = fair.get("strStadt", "")

    if (
        fair.get("blnFKM")
        and any(target in city for target in TARGET_CITIES)
    ):

        rows.append({
            "MesseID": fair.get("strMesseTerminKey"),
            "MesseName": fair.get("strTitel"),
            "Termin": fair.get("strTermin"),
            "Stadt": fair.get("strStadt"),
            "Land": fair.get("strLand"),
            "Kategorie": fair.get("strKategorie"),
            "Foerderung": fair.get("strFoerderung"),
            "FKM": fair.get("blnFKM"),
            "UrlParameter": fair.get("strUrlParameter")
        })

with open(
    "fkm_messen.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "MesseID",
            "MesseName",
            "Termin",
            "Stadt",
            "Land",
            "Kategorie",
            "Foerderung",
            "FKM",
            "UrlParameter"
        ]
    )

    writer.writeheader()
    writer.writerows(rows)

print("FKM-Messen exportiert:", len(rows))
