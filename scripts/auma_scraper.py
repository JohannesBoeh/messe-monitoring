import requests

url_parameter = "dusseldorf_psi_229475"

detail_url = (
    f"https://www.auma.de/messen-finden/details/"
    f"{url_parameter}"
)

response = requests.get(
    detail_url,
    headers={"User-Agent": "Mozilla/5.0"}
)

print("URL:")
print(detail_url)

print("\nSTATUS:")
print(response.status_code)

print("\nERSTE 3000 ZEICHEN:\n")

print(response.text[:3000])
