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

fkm_fairs = []

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

        fkm_fairs.append({
            "Titel": fair["strTitel"],
            "Status": response.status_code,
            "URL": detail_url
        })

print("FKM-Seiten geprüft:", len(fkm_fairs))

ok = sum(
    1 for x in fkm_fairs
    if x["Status"] == 200
)

print("Status 200:", ok)

for row in fkm_fairs[:20]:
    print(row)
