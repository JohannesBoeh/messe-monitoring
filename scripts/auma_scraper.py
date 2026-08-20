import requests
from bs4 import BeautifulSoup

url = (
    "https://www.auma.de/messen-finden/details/"
    "?tfd=dusseldorf_psi_229475"
)

response = requests.get(
    url,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

soup = BeautifulSoup(
    response.text,
    "html.parser"
)

text = soup.get_text("\n", strip=True)

keywords = [
    "Turnus:",
    "Gründungsjahr:",
    "Veranstalter",
    "Zutritt",
    "Aussteller",
    "Besucher",
    "Bruttofläche",
    "Nettofläche"
]

for keyword in keywords:

    print("\n" + "=" * 80)
    print(keyword)
    print("=" * 80)

    pos = text.find(keyword)

    if pos != -1:

        start = max(0, pos - 200)
        end = min(len(text), pos + 1000)

        print(text[start:end])

    else:
        print("Nicht gefunden")
