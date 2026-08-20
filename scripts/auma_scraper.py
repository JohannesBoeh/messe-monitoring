import requests
from collections import Counter

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

filtered = []

for fair in data:

    city = fair.get("strStadt", "")

    if any(target in city for target in TARGET_CITIES):
        filtered.append(fair)

print("Gesamtzahl A-Standorte:")
print(len(filtered))

print("\nMessen je Stadt:\n")

city_counter = Counter()

for fair in filtered:
    city_counter[fair["strStadt"]] += 1

for city, count in city_counter.most_common():
    print(f"{city}: {count}")

print("\nFKM-Messen:\n")

fkm_count = sum(
    1 for fair in filtered
    if fair.get("blnFKM")
)

print(fkm_count)
