import requests
from bs4 import BeautifulSoup

url = "https://www.auma.de/messen-finden/details/?tfd=dusseldorf_psi_229475"

response = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
)

soup = BeautifulSoup(response.text, "html.parser")

text = soup.get_text("\n", strip=True)

print("Zeichen im Text:", len(text))
print()
print(text[:5000])
