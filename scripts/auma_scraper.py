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

    print("Klicke Ergebnisse anzeigen...")

    page.locator("button").nth(25).click(force=True)

    page.wait_for_timeout(5000)

    print("\nURL:")
    print(page.url)

    print("\nERSTE 3000 ZEICHEN:\n")

    body = page.locator("body").inner_text()

    print(body[:3000])

    browser.close()
