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

fkm_count = sum(
    1 for fair in data
    if fair.get("blnFKM")
)

print("FKM-Messen:")
print(fkm_count)

print("\nERSTE 10:\n")

counter = 0

for fair in data:

    if fair.get("blnFKM"):

        print(fair["strTitel"])
        print(fair["strUrlParameter"])
        print()

        counter += 1

        if counter >= 10:
            break
