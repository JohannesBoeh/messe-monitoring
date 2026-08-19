import requests
from bs4 import BeautifulSoup

url = "https://www.auma.de/messen-finden/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

print(f"Status Code: {response.status_code}")

soup = BeautifulSoup(response.text, "html.parser")

print("\nSeitentitel:")
print(soup.title.text)

print("\nErste 20 Formularelemente:")

for tag in soup.find_all(["input", "select"])[0:20]:
    print(tag)
