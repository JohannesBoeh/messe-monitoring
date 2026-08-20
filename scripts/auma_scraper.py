import requests
from bs4 import BeautifulSoup

url = "https://www.auma.de/messen-finden/details/?tfd=dusseldorf_psi_229475"

response = requests.get(
    url,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

print("STATUS:")
print(response.status_code)

print("\nFINAL URL:")
print(response.url)

soup = BeautifulSoup(
    response.text,
    "html.parser"
)

print("\nSEITENTITEL:")
print(soup.title.text)

print("\nERSTE 10000 ZEICHEN:\n")

text = soup.get_text("\n", strip=True)

print(text[:10000])
