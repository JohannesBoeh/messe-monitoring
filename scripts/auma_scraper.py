import requests

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

for city in A_CITIES:

    print("\n" + "=" * 50)
    print(city)
    print("=" * 50)

    fairs = [
        fair
        for fair in data
        if fair.get("strStadt") == city
    ]

    for fair in fairs[:10]:
        print(fair["strTitel"])
