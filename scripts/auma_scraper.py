import requests

url = "https://www.auma.de/messen-finden/details/?tfd=dusseldorf_psi_229475"

response = requests.get(
    url,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

text = response.text

suchbegriffe = [
    "Turnus:",
    "Gründungsjahr:",
    "RX Deutschland GmbH",
    "Fachbesucher",
    "Aussteller",
    "Besucher",
    "Bruttofläche",
    "Nettofläche"
]

print("GEFUNDENE TREFFER:\n")

for begriff in suchbegriffe:

    pos = text.find(begriff)

    if pos != -1:

        start = max(0, pos - 200)
        end = min(len(text), pos + 1000)

        print("\n" + "=" * 80)
        print(begriff)
        print("=" * 80)

        print(text[start:end])
