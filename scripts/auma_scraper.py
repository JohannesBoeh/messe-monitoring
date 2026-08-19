import requests

base_url = "https://www.auma.de/api/TradeFairData/"

endpoints = [
    "getWebOverviewTradeFairData",
    "getWebOverviewTradeFairDataList",
    "getTradeFairData",
    "getTradeFairDetails",
    "getTradeFair",
]

for endpoint in endpoints:
    url = (
        base_url
        + endpoint
        + "?intFilterYearFrom=2026"
        + "&intFilterYearTo=2032"
        + "&intFilterMonthFrom=1"
        + "&intFilterMonthTo=12"
        + "&strLanguage=de"
    )

    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30
        )

        print("\n====
