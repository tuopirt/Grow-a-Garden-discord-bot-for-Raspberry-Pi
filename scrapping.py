from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from collections import defaultdict
import asyncio
import concurrent.futures
import time

def scrape_sync():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)
    driver.get("https://www.vulcanvalues.com/grow-a-garden/stock")

    #asyncio.sleep(3)  # won’t run in sync function, use time.sleep instead
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    categorized = defaultdict(list)

    for header in soup.find_all("h2", class_="text-xl font-bold mb-2 text-center"):
        category = header.text.strip()
        ul = header.find_next_sibling("ul")
        if not ul:
            continue

        items = ul.find_all("li", class_="bg-gray-900")
        for item in items:
            name = item.find("img")["alt"]
            quantity = item.find("span", class_="text-gray-400").text.strip()
            categorized[category].append((name, quantity))

    return categorized

# ✅ This is what your bot will call
async def scrape_garden_stock():
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, scrape_sync)
    return result