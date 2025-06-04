from playwright.async_api import async_playwright
from collections import defaultdict

async def scrape_garden_stock():
    categorized = defaultdict(list)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.vulcanvalues.com/grow-a-garden/stock")
        await page.wait_for_selector("h2.text-xl.font-bold")  # Wait for content

        content = await page.content()
        await browser.close()

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    for section in soup.find_all("section"):
        header = section.find("h2", class_="text-xl font-bold mb-2 text-center")
        ul = section.find("ul", class_="grid")
        if not header or not ul:
            continue

        category = header.text.strip()
        items = ul.find_all("li", class_="bg-gray-900")

        for item in items:
            name = item.find("img")["alt"]
            quantity = item.find("span", class_="text-gray-400").text.strip()
            categorized[category].append((name, quantity))

    return categorized
