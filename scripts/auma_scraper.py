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

        print("=" * 80)
        print(fair["strTitel"])
        print("Status:", response.status_code)

        count += 1

        if count >= 20:
            break
