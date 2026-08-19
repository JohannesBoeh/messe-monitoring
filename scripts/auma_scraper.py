from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(
        "https://www.auma.de/messen-finden/",
        wait_until="networkidle"
    )

    page.fill("#location-input", "München")

    page.wait_for_timeout(3000)

    content = page.locator("body").inner_text()

    print(content[:5000])

    browser.close()
