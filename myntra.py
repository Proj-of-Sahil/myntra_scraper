from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.proxy import Proxy, ProxyType
import re
import concurrent.futures
import random
import time


BASE_URL = "https://www.myntra.com/"
log_path = "./geckodriver.log"

# Your list of proxies
# proxies = [
#     "184.168.124.233:5402",
#     "35.185.196.38:3128",
#     "154.236.177.102:1976",
#     "34.143.221.240:8103",
#     "189.240.60.163:9090",
#     "189.240.60.169:9090",
# ]

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
]


def setup_driver_with_proxy():
    # proxy_ip_port = random.choice(proxies)  # Randomly select a proxy
    firefox_options = FirefoxOptions()
    user_agent = random.choice(user_agents)
    firefox_options.set_preference("general.useragent.override", user_agent)
    firefox_options.add_argument("--headless")
    # firefox_options.proxy = Proxy(
    #     {
    #         "proxyType": ProxyType.MANUAL,
    #         "httpProxy": proxy_ip_port,
    #         "sslProxy": proxy_ip_port,
    #     }
    # )

    # Specify the path to your GeckoDriver
    driver_path = "/opt/geckodriver/geckodriver"
    service = Service(
        executable_path=driver_path, log_output=log_path, log_level="INFO"
    )

    # Initialize the Firefox driver with the proxy settings
    driver = webdriver.Firefox(service=service, options=firefox_options)
    return driver


def total_pages_for_item(driver, url):
    try:
        # Assuming there's an element that shows the total number of pages as "Page 1 of X"
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "pagination-paginationMeta"))
        )
        pagination_meta = driver.find_element(
            By.CLASS_NAME, "pagination-paginationMeta"
        ).text

        # Use a regular expression to find the total number of pages
        total_pages_match = re.search(r"Page \d+ of (\d+)", pagination_meta)
        if total_pages_match:
            total_pages = int(total_pages_match.group(1))
            print(f"Total Pages: {total_pages}")
            return total_pages
        else:
            print("Could not find the total number of pages.")
    except Exception as e:
        print(f"An error occurred while trying to find the total number of pages: {e}")


def worker(task):
    driver = task["driver"]
    url = BASE_URL + task["item"]
    item_name = task["item"]
    total_pages = total_pages_for_item(driver, url)
    page_number = 1
    while True:
        try:
            # Wait for the initial elements to load
            driver.get(url)
            WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.CLASS_NAME, "results-base"))
            )

            # Scroll down to the bottom of the page to ensure all data is loaded
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.randint(5, 10))
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Save the page HTML to a file
            element = driver.find_element(By.CLASS_NAME, "results-base")
            inner_html = element.get_attribute("innerHTML")

            # Append the inner HTML to a file
            with open(f"./outputs/{item_name}.html", "a") as file:
                file.write(inner_html)
            # with open(f"page_{page_number}.html", "w") as file:
            # file.write(driver.page_source)
            print(page_number, "/", total_pages, ":-", item_name, end=" ")
            progression_percentage = (page_number / total_pages) * 100
            print(f"Progression Percentage: {progression_percentage:.2f}%")

            # Check if the "Next" button is present and not disabled
            next_button = driver.find_element(
                By.CSS_SELECTOR, "li.pagination-next:not(.pagination-disabled)"
            )

            if next_button:
                next_button.click()
                page_number += 1
                time.sleep(random.randint(5, 8))  # Wait for the next page to load
            else:
                # If the "Next" button is disabled, we are on the last page
                break
        except Exception as e:
            print(f"An error occurred: {e}")
            break
        finally:
            pass
    driver.quit()
    return f"Sucess: {item_name}"


tasks = [
    {"item": "saree", "driver": setup_driver_with_proxy()},
    {"item": "cargo", "driver": setup_driver_with_proxy()},
    {"item": "kurta", "driver": setup_driver_with_proxy()},
    {"item": "shirts", "driver": setup_driver_with_proxy()},
    {"item": "jeans", "driver": setup_driver_with_proxy()},
]

# Run scraping tasks in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    future_to_url = {executor.submit(worker, task): task for task in tasks}
    for future in concurrent.futures.as_completed(future_to_url):
        task = future_to_url[future]
        try:
            data = future.result()
            print(f"Task completed: {task}, Result: {data}")
        except Exception as exc:
            print(f"Task generated an exception: {task}, Exception: {exc}")
