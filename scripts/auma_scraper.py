import requests
import csv
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

        turnus = ""

        for i, line in enumerate(lines):
            if line == "Turnus:":
                if i + 1 < len(lines):
                    turnus = lines[i + 1]
                break

        besucher = ""

        for i, line in enumerate(lines):
            if line == "Besucher (Zahl der Eintritte)":
                if i + 1 < len(lines):
                    besucher = lines[i + 1]
                break

        aussteller = ""

        for i in range(len(lines) - 3):

  
