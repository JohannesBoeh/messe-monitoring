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

    print("Location Field:")
    print(page.input_value("#location-input"))

    print("\nAria Controls:")

    element = page.locator("#location-input")

    print("aria-controls =", element.get_attribute("aria-controls"))
    print("aria-expanded =", element.get_attribute("aria-expanded"))
    print("role =", element.get_attribute("role"))

    browser.close()
