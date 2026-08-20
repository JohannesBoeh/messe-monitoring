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

for fair in data:

    if fair.get("strMesseTerminKey") == "229475":

        print("PSI gefunden:\n")

        for key, value in fair.items():
            print(f"{key}: {value}")

        break
