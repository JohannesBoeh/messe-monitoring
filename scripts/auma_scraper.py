import requests

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

for fair in data[:20]:

    print("=" * 80)

    print("TITEL:")
    print(fair.get("strTitel"))

    print("\nURL PARAMETER:")
    print(fair.get("strUrlParameter"))

    print("\nKOMPLETTER DATENSATZ:")
    print(fair)
