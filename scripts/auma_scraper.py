import requests

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

print("Anzahl Datensätze:")
print(len(data))

print("\nErste 50 Städte:\n")

count = 0

for fair in data:

    print(fair.get("strStadt"))

    count += 1

    if count >= 50:
        break
