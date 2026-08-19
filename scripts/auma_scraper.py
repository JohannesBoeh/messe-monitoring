from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(
        "https://www.auma.de/messen-finden/",
        wait_until="networkidle"
    )

    page.fill("#location-input", "München")

    page.keyboard.press("Enter")

    page.wait_for_timeout(5000)

    print("Aktuelle URL:")
    print(page.url)

    print("\nSeitentitel:")
    print(page.title())

    browser.close()
