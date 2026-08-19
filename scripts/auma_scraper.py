import requests
from bs4 import BeautifulSoup

url = "https://www.auma.de/messen-finden/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, "html.parser")

print("Inputs mit Name-Attribut:\n")

for inp in soup.find_all("input"):
    print("NAME :", inp.get("name"))
    print("ID   :", inp.get("id"))
    print("TYPE :", inp.get("type"))
    print("VALUE:", inp.get("value"))
    print("-" * 40)
