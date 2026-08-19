from cities import CITIES
import csv

print("Starte AUMA-Scraper...\n")

all_messen = []

for item in CITIES:
    messe = {
        "stadt": item["city"],
        "standortklasse": item["class"]
    }

    all_messen.append(messe)

with open("output/raw_auma.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["stadt", "standortklasse"]
    )

    writer.writeheader()
    writer.writerows(all_messen)

print("CSV erfolgreich erstellt.")
