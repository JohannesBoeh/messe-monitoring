import requests
import csv

A_CITIES = [
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

filtered = [
    fair
    for fair in data
    if fair.get("strStadt") in A_CITIES
]

rows = []

for fair in filtered:
    rows.append({
        "MesseID": fair.get("strMesseTerminKey"),
        "MesseName": fair.get("strTitel"),
        "Stadt": fair.get("strStadt"),
        "Land": fair.get("strLand"),
        "Termin": fair.get("strTermin"),
        "Kategorie": fair.get("strKategorie"),
        "FKM": fair.get("blnFKM"),
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
            "Stadt",
            "Land",
            "Termin",
            "Kategorie",
            "FKM",
            "UrlParameter"
        ]
    )

    writer.writeheader()
    writer.writerows(rows)

print("Datensätze exportiert:", len(rows))

for row in rows[:10]:
    print(
        row["Stadt"],
        "-",
        row["MesseName"]
    )
