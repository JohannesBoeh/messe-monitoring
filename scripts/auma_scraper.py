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

print("Anzahl Datensätze:", len(data))

print("\nERSTE 10 MESSEN\n")

for fair in data[:10]:

    print("Titel:", fair.get("strTitel"))
    print("Termin:", fair.get("strTermin"))
    print("Stadt:", fair.get("strStadt"))
    print("-" * 40)
