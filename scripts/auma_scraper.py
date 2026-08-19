from playwright.sync_api import sync_playwright

def log_response(response):
    if "getWebOverviewTradeFairDataCount" in response.url:
        print("URL:")
        print(response.url)

        try:
            print("\nRESPONSE:")
            print(response.text())
        except Exception as e:
            print(e)

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

    page.wait_for_timeout(8000)

    browser.close()
