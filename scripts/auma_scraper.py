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

data = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
).json()

filtered = [
    fair
    for fair in data
    if fair.get("strStadt") in A_CITIES
]

with open(
    "a_standorte.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "strMesseTerminKey",
            "strTitel",
            "strStadt",
            "strTermin",
            "strKategorie",
            "blnFKM",
            "strUrlParameter"
        ]
    )

    writer.writeheader()
    writer.writerows(filtered)

print("Datensätze:", len(filtered))
