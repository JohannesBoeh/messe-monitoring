import requests
import csv
from bs4 import BeautifulSoup

API_URL = (
    "https://www.auma.de/api/TradeFairData/"
    "getWebOverviewTradeFairData"
    "?intFilterYearFrom=2026"
    "&intFilterYearTo=2032"
    "&intFilterMonthFrom=1"
    "&intFilterMonthTo=12"
    "&strLanguage=de"
)

data = requests.get(
    API_URL,
    headers={"User-Agent": "Mozilla/5.0"}
).json()

rows = []

for fair in data:

    if not fair.get("blnFKM"):
        continue

    detail_url = (
        "https://www.auma.de/messen-finden/details/?tfd="
        + fair["strUrlParameter"]
    )

    try:

        response = requests.get(
            detail_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        text = soup.get_text("\n", strip=True)

        rows.append({
            "MesseName": fair.get("strTitel"),
            "Stadt": fair.get("strStadt"),
            "Termin": fair.get("strTermin"),
            "FKM": fair.get("blnFKM"),
            "DetailURL": detail_url,
            "TextLaenge": len(text)
        })

        print(
            f"{len(rows)} | "
            f"{fair.get('strTitel')}"
        )

        if len(rows) >= 10:
            break

    except Exception as e:

        print("FEHLER:", e)

with open(
    "fkm_detail_test.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "MesseName",
            "Stadt",
            "Termin",
            "FKM",
            "DetailURL",
            "TextLaenge"
        ]
    )

    writer.writeheader()
    writer.writerows(rows)

print()
print("Exportiert:", len(rows))
``
