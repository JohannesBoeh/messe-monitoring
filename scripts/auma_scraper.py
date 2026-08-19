import requests

BASE_URL = "https://www.auma.de/api/TradeFairData/"

endpoints = [
    "getTradeFairData?messeTerminKey=229475",
    "getTradeFairData?intMesseTerminKey=229475",
    "getTradeFairDetails?messeTerminKey=229475",
    "getTradeFairDetails?intMesseTerminKey=229475",
    "getWebTradeFairData?messeTerminKey=229475",
    "getWebTradeFairData?intMesseTerminKey=229475"
]

for endpoint in endpoints:

    url = BASE_URL + endpoint

    print("\n" + "=" * 80)
    print(url)

    try:

        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30
        )

        print("STATUS:", response.status_code)
        print(response.text[:1000])

    except Exception as e:

        print("ERROR:", e)
