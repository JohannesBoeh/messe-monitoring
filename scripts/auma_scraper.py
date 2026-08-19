from playwright.sync_api import sync_playwright

seen = set()

def log_response(response):
    url = response.url

    if "/api/TradeFairData/" in url and url not in seen:
        seen.add(url)

        print("\nAPI:")
        print(url)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.on("response", log_response)

    page.goto(
        "https://www.auma.de/messen-finden/",
        wait_until="networkidle"
    )

    page.click("#location-input")
    page.fill("#location-input", "Mün")

    page.wait_for_timeout(2000)

    page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")

    page.wait_for_timeout(10000)

    browser.close()
