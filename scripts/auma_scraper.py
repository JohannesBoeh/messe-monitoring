from playwright.sync_api import sync_playwright

seen = set()

def log_response(response):

    url = response.url

    if "/api/" in url and url not in seen:
        seen.add(url)

        print("\n" + "=" * 100)
        print(url)

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.on("response", log_response)

    page.goto(
        "https://www.auma.de/messen-finden/",
        wait_until="networkidle"
    )

    page.wait_for_timeout(3000)

    body = page.locator("body").inner_text()

    print(body[:5000])

    browser.close()
