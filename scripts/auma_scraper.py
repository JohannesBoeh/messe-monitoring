import requests
import csv

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

    if fair.get("blnFKM"):

        rows.append({
            "MesseName": fair.get("strTitel"),
            "Stadt": fair.get("strStadt"),
            "Termin": fair.get("strTermin"),
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
            "MesseName",
            "Stadt",
            "Termin",
            "UrlParameter"
        ]
    )

    writer.writeheader()
    writer.writerows(rows)

print("Exportiert:", len(rows))
