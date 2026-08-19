from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(
        "https://www.auma.de/messen-finden/",
        wait_until="networkidle"
    )

    page.click("#location-input")

    page.fill("#location-input", "Mün")

    page.wait_for_timeout(5000)

    print("aria-expanded:")
    print(
        page.locator("#location-input")
        .get_attribute("aria-expanded")
    )

    print("\nBody-Auszug:")

    body = page.locator("body").inner_text()

    if "München" in body:
        print("München gefunden!")
    else:
        print("München nicht gefunden!")

    browser.close()
