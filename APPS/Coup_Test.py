# How to use PIP without writing to the 
#C:/Users/swcarpe2/AppData/Local/Programs/Python/Python313/python.exe -m pip install [Python Lib]

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from random import random
import time, csv

def scrape_webpage(departments):
    # TODO: Need to switch to dynamic loading times
    LINK = 'https://www.kroger.com/savings/cl/coupons/'
    coupons = []
    
    # Scrape headlines from a news website
    options = Options()
    options.add_argument('--start-fullscreen')
    options.add_argument('--force-device-scale-factor=.8')

    # URL setup
    url = LINK + "?"
    for item in departments:
        if " " in item:
            print("WARNING: A blank space was dtected may break link")
        url += "&category=" + item

    url = url.replace("?&", "?", 1)
    print("Url:", url, "\n")

    # Webdriver setup
    driver = webdriver.Edge(options=options)
    driver.get(url)
    print("Waiting for page to load (first time)")
    time.sleep(3)

    # Get initial scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print("Waiting for page to load")
        time.sleep(3)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break   # No more content
        last_height = new_height

    buttons = driver.find_elements(By.CLASS_NAME, 'CouponCard-viewQualifyingProducts')
    print("Num of buttons:", len(buttons))

    # Loop through the different Coupons
    for idx, btn in enumerate(buttons):
        driver.execute_script(f"arguments[0].scrollIntoView(true);", btn)
        driver.execute_script(f"window.scrollBy(0, -250);")
        btn.click()


        # TODO: Run a try/catch in case the "Qualifying Products" loads
        coupon_data = BeautifulSoup(driver.page_source, 'html.parser')
        coupon_data = coupon_data.find(class_="CouponDetails-new-content").find(class_="ml-0")
        # TODO: Needs to be a clean-up function
        #             (Coupon Title, Coupon Information, Coupon Expiration)
        coupon_data = (coupon_data.contents[0].h2.text, coupon_data.contents[2].span.text, 
                       coupon_data.contents[3].span.text)
        coupons.append(coupon_data)

        print(f"\n------ Data found ------ ({idx+1}/{len(buttons)})")
        print(coupon_data) 


        # TODO: Can be improved if necessary
        # Press the "X"
        raw = driver.find_elements(By.CLASS_NAME, 'ReactModalPortal')[2]\
            .find_element(By.CLASS_NAME, 'ReactModal__Overlay--after-open')\
            .find_element(By.CLASS_NAME, 'ReactModal__Content')\
            .find_element(By.CSS_SELECTOR, '[data-testid="modal-header-section"]')

        raw_raw = raw.find_element(By.CSS_SELECTOR, '[data-testid="ModalCloseButton"]')
        WebDriverWait(driver, 1 + random()).until(EC.element_to_be_clickable(raw_raw))
        raw_raw.click()


    return coupons

if __name__ == '__main__':
    try:
        departments = [
        "Bakery", "Baking%20Goods", "Beverages", "Breakfast", "Candy",
        "Canned%20%26%20Packaged", "Cleaning%20Products",
        "Condiment%20%26%20Sauces", "Dairy", "Deli", "Frozen", "General",
        "Health", "International", "Meat%20%26%20Seafood",
        "Natural%20%26%20Organic", "Produce", "Snacks",
        "Pasta%20Sauces%20Grain"
    ]
        
        print("MAKE SURE TO SWITCH TO Selenium\n")
        print(len(departments), "department(s) selected")
        coupon_list = scrape_webpage(departments)

        file_name = "example.csv"
        with open(file_name, "w", newline='') as file:
            print(f"Writing to {file_name}:")
            writer = csv.writer(file)
            for item in coupon_list:
                writer.writerow(list(item))

    except Exception as e:
        print(f'An error occurred: {e}')