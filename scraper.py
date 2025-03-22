from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import pandas as pd
from datetime import datetime
import time

options = Options()
options.add_argument("--window-size=1920,1080")
options.add_argument("--headless")
ua = UserAgent()
options.add_argument(f"user-agent={ua.random}")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

URL = "https://www.ebay.com/globaldeals/tech"
CSV_FILE = "ebay_tech_deals.csv"


def setup_page():
    driver.get(URL)
    time.sleep(5)
    scroll_to_bottom()


def scroll_to_bottom():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def extract_product_data(item, timestamp):
    try:
        title = item.find_element(By.XPATH, ".//h3[contains(@class, 'dne-itemtile-title')]//span[@itemprop='name']").text.strip()
    except Exception:
        title = "N/A"
    try:
        price = item.find_element(By.CSS_SELECTOR, ".dne-itemtile-price").text.strip()
    except Exception:
        price = "N/A"
    try:
        original_price = item.find_element(By.XPATH, ".//div[@class='dne-itemtile-original-price']//span[@class='itemtile-price-strikethrough']").text.strip()
    except Exception:
        original_price = "N/A"
    try:
        shipping = item.find_element(By.XPATH, ".//span[@class='dne-itemtile-delivery']").text.strip()
    except Exception:
        shipping = "N/A"
    try:
        item_url = item.find_element(By.XPATH, ".//div[@class='dne-itemtile-detail']/a").get_attribute("href")
    except Exception:
        item_url = "N/A"

    try:
        return {
            "timestamp": timestamp,
            "title": title,
            "price": price,
            "original_price": original_price,
            "shipping": shipping,
            "item_url": item_url
        }
    except Exception as e:
        print(f"Error processing product item: {e}")
        return None


def scrape_products():
    setup_page()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    products = []

    try:
        product_items = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".dne-itemtile"))
        )
    except Exception:
        product_items = []

    for item in product_items:
        product = extract_product_data(item, timestamp)
        if product:
            products.append(product)

    return products


def append_to_csv(data):
    try:
        df_existing = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        df_existing = pd.DataFrame(columns=["timestamp", "title", "price", "original_price", "shipping", "item_url"])

    new_data = pd.DataFrame(data)
    df_combined = pd.concat([df_existing, new_data], ignore_index=True)
    df_combined.to_csv(CSV_FILE, index=False)


def main():
    print("Scraping eBay Tech Deals...")
    data = scrape_products()
    if data:
        append_to_csv(data)
        print(f"Data for {len(data)} products saved to {CSV_FILE}")
    else:
        print("No products found or error occurred")
    driver.quit()


if __name__ == "__main__":
    main()
