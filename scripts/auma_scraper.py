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

first_fair = data[0]

print("MESSE:")
print(first_fair["strTitel"])

print("\nURL PARAMETER:")
print(first_fair["strUrlParameter"])

print("\nMESSE KEY:")
print(first_fair["strMesseTerminKey"])
