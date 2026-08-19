from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(
        "https://www.auma.de/messen-finden/",
        wait_until="networkidle"
    )

    # München auswählen
    page.click("#location-input")
    page.fill("#location-input", "Mün")

    page.wait_for_timeout(2000)

    page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")

    page.wait_for_timeout(2000)

    # Ergebnisse anzeigen anklicken
    page.locator("button").nth(26).click(force=True)

    page.wait_for_timeout(5000)

    print("URL:")
    print(page.url)

    print("\nErste 1000 Zeichen:")

    text = page.locator("body").inner_text()

    print(text[:1000])

    browser.close()
