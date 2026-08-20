import requests
from bs4 import BeautifulSoup

url = "https://www.auma.de/messen-finden/details/?tfd=dusseldorf_psi_229475"

response = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
)

soup = BeautifulSoup(response.text, "html.parser")

text = soup.get_text("\n", strip=True)

lines = [
    line.strip()
    for line in text.split("\n")
    if line.strip()
]

for i, line in enumerate(lines):

    if line == "Turnus:":
        print("\nTURNUS")
        print(lines[i:i+5])

    if line == "Besucher (Zahl der Eintritte)":
        print("\nBESUCHER")
        print(lines[i:i+10])

    if line == "Aussteller":
        print("\nAUSSTELLER")
        print(lines[i:i+10])
