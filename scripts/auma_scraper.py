import requests
import csv
import re
from bs4 import BeautifulSoup

TARGET_CITIES = [
    "Berlin",
    "Düsseldorf",
    "Frankfurt am Main",
    "Hamburg",
    "Köln",
    "Leipzig",
    "München",
    "Stuttgart"
]

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

    city = fair.get("strStadt", "")

    if city not in TARGET_CITIES:
        continue

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

        soup = BeautifulSoup(
            page.text,
            "html.parser"
        )

        text = soup.get_text("\n", strip=True)

        lines = [
            x.strip()
            for x in text.split("\n")
            if x.strip()
        ]

        # Standardwerte
        turnus = ""
        besucher = ""
        aussteller = ""

        # Turnus suchen
        for i, line in enumerate(lines):
            if line == "Turnus:":
                if i + 1 < len(lines):
                    turnus = lines[i + 1]
                break

        # Besucher suchen
        for i, line in enumerate(lines):
            if line == "Besucher (Zahl der Eintritte)":
                if i + 1 < len(lines):
                    besucher = lines[i + 1]
                break

        # Aussteller suchen
        for i, line in enumerate(lines):
            if (
                line == "Aussteller"
                and i + 1 < len(lines)
                and re.match(r"^[0-9.]+$", lines[i + 1])
            ):
                aussteller = lines[i + 1]
                break

        termin = fair.get("strTermin", "")

        jahr = ""
        monat = ""

        match = re.search(r"(20\d{2})", termin)

        if match:
            jahr = match.group(1)

        match = re.match(r"(\d{2})\.", termin)

        if match:
            monat = match.group(1)

        rows.append({
            "Messe": fair.get("strTitel"),
            "Jahr": jahr,
            "Monat": monat,
            "Termin": termin,
            "Stadt": city,
            "Turnus": turnus,
            "Besucherzahl": besucher,
            "Ausstellerzahl": aussteller
        })

        print(
            len(rows),
            fair.get("strTitel")
        )

    except Exception as e:

        print(
            "FEHLER:",
            fair.get("strTitel"),
            e
        )

with open(
    "AUMA_FKM_Messen.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "Messe",
            "Jahr",
            "Monat",
            "Termin",
            "Stadt",
            "Turnus",
            "Besucherzahl",
            "Ausstellerzahl"
        ],
        delimiter=";"
    )

    writer.writeheader()
    writer.writerows(rows)

print()
print("Exportiert:", len(rows))
