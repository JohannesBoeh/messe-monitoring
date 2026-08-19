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

    print("Überschriften:")

    headings = page.locator("h1, h2, h3")

    for i in range(headings.count()):
        try:
            print(headings.nth(i).inner_text())
        except:
            pass

    browser.close()
`
