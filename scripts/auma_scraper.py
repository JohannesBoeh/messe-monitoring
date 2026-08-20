import requests
import csv

API_URL = (
    "https://www.auma.de/api/TradeFairData/"
    "getWebOverviewTradeFairData"
    "?intFilterYearFrom=2026"
    "&intFilterYearTo=2032"
    "&intFilterMonthFrom=1"
    "&intFilterMonthTo=12"
    "&strLanguage=de"
)

response = requests.get(
    API_URL,
    headers={"User-Agent": "Mozilla/5.0"}
)

data = response.json()

rows = []

for fair in data:

    if not fair.get("blnFKM"):
        continue

    detail_url = (
        "https://www.auma.de/messen-finden/details/?tfd="
        + fair["strUrlParameter"]
    )

    try:

        page = requests.get(
            detail_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30
        )

        rows.append({
            "MesseName": fair.get("strTitel"),
            "Stadt": fair.get("strStadt"),
            "Termin": fair.get("strTermin"),
            "Status": page.status_code,
            "HTML_Laenge": len(page.text),
            "DetailURL": detail_url
        })

        print(
            f"{len(rows)} | "
            f"{fair.get('strTitel')} | "
            f"{page.status_code}"
        )

        if len(rows) >= 10:
            break

    except Exception as e:

        print("Fehler:", e)

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
            "Status",
            "HTML_Laenge",
            "DetailURL"
        ]
    )

    writer.writeheader()
    writer.writerows(rows)

print()
print("Exportiert:", len(rows))
