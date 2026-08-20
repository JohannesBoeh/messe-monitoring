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

print("ANZAHL:")
print(len(data))

print("\nFKM MESSEN:\n")

count = 0

for fair in data:

    if fair.get("blnFKM"):

        print("=" * 80)

        print("TITEL:")
        print(fair.get("strTitel"))

        print("\nMESSE KEY:")
        print(fair.get("strMesseTerminKey"))

        print("\nURL PARAMETER:")
        print(fair.get("strUrlParameter"))

        print("\nSTADT:")
        print(fair.get("strStadt"))

        count += 1

        if count == 10:
            break
