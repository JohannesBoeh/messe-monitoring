import requests
import json

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

print("Suche erste FKM-Messe...\n")

found = False

for fair in data:

    if fair.get("blnFKM"):

        print(json.dumps(
            fair,
            indent=2,
            ensure_ascii=False
        ))

        found = True
        break

if not found:
    print("Keine FKM-Messe gefunden.")
