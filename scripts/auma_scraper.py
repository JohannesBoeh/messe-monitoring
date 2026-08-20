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

fkm_fairs = []

for fair in data:

    city = fair.get("strStadt", "")

    if (
        fair.get("blnFKM")
        and any(target in city for target in TARGET_CITIES)
    ):
        fkm_fairs.append(fair)

print("FKM-Messen gesamt:")
print(len(fkm_fairs))

print("\nFKM-Messen je Stadt:\n")

counter = Counter()

for fair in fkm_fairs:
    counter[fair["strStadt"]] += 1

for city, count in counter.most_common():
    print(f"{city}: {count}")

print("\nERSTE 20 FKM-MESSEN\n")

for fair in fkm_fairs[:20]:
    print(
        fair["strStadt"],
        "-",
        fair["strTitel"]
    )
