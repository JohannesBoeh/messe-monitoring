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

    if any(target in city for target in TARGET_CITIES):

        rows.append({
            "MesseID": fair.get("strMesseTerminKey"),
            "MesseName": fair.get("strTitel"),
            "Termin": fair.get("strTermin"),
            "Stadt": fair.get("strStadt"),
            "Land": fair.get("strLand"),
            "Kategorie": fair.get("strKategorie"),
            "Foerderung": fair.get("strFoerderung"),
            "FKM": fair.get("blnFKM"),
            "DE": fair.get("blnDE"),
            "HE": fair.get("blnHE"),
            "WAN": fair.get("blnWAN"),
            "GTQ": fair.get("blnGTQ"),
            "UrlParameter": fair.get("strUrlParameter")
        })

with open(
    "a_standorte.csv",
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
            "DE",
            "HE",
            "WAN",
            "GTQ",
            "UrlParameter"
        ]
    )

    writer.writeheader()
    writer.writerows(rows)

print("Exportierte Datensätze:", len(rows))
