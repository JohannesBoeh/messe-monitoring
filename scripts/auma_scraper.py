from playwright.sync_api import sync_playwright
import re

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(
        "https://www.auma.de/messen-finden/",
        wait_until="networkidle"
    )

    page.click("#location-input")
    page.fill("#location-input", "Mün")

    page.wait_for_timeout(2000)

    page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")

    page.wait_for_timeout(3000)

    body = page.locator("body").inner_text()

    matches = re.findall(r"(\\d+)\\s+Messen gefunden", body)

    if matches:
        print("Trefferzahl:", matches[0])
    else:
        print("Keine Trefferzahl gefunden")

    browser.close()
