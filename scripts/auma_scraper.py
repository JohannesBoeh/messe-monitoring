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

data = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
).json()

count = 0

for fair in data:

    if fair.get("blnFKM"):

        detail_url = (
            "https://www.auma.de/messen-finden/details/?tfd="
            + fair["strUrlParameter"]
        )

        response = requests.get(
            detail_url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        print("\n================================================")
        print(fair["strTitel"])
        print(response.status_code)
        print(detail_url)

        count += 1

        if count == 10:
            break
``
