from playwright.sync_api import sync_playwright

print("Starte Browser...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto("https://www.auma.de/messen-finden/")

    print("Seitentitel:")
    print(page.title())

    browser.close()
