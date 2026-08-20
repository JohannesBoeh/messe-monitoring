import requests
from bs4 import BeautifulSoup

detail_url = (
    "https://www.auma.de/messen-finden/details/"
    "?tfd=dusseldorf_psi_229475"
)

response = requests.get(
    detail_url,
    headers={"User-Agent": "Mozilla/5.0"}
)

soup = BeautifulSoup(response.text, "html.parser")

text = soup.get_text("\n", strip=True)

lines = []

for line in text.split("\n"):

    line = line.strip()

    if line:
        lines.append(line)

for i, line in enumerate(lines):

    if line in [
        "Turnus:",
        "Gründungsjahr:",
        "Veranstalter",
        "Zutritt",
        "Aussteller",
        "Besucher",
        "Bruttofläche",
        "Nettofläche"
    ]:

        print("\n" + "=" * 80)
        print(line)
        print("=" * 80)

        for x in lines[i:i+20]:
            print(x)
