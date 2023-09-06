from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import csv
import time


class Craig:
    def __init__(self):

        # creating selenium driver
        # self.url = input("Enter the Craigslist link you want: ")
        self.url = 'https://orangecounty.craigslist.org/search/orange-ca/cta?lat=33.799&lon=-117.765&min_price=0&purveyor=owner&search_distance=7.5#search=1~gallery~0~0'
        options = ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--headless')
        options.add_argument('--log-level=3')
        self.driver = Chrome(service=Service(
            ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 60)
        self.parsed_links = []

    def parse_item(self, link):  # removed
        if self.driver.find_elements(By.CLASS_NAME, 'removed'):
            return None
        self.driver.get(link)
        car_info = self.wait.until(
            EC.visibility_of_all_elements_located((By.CLASS_NAME, 'attrgroup')))
        title = car_info[0].text.split(maxsplit=1)
        year = title[0]
        name = title[1]
        print(f'Gathering info for {name}')
        price = self.wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'price'))).text
        description_str = car_info[1].text.strip().split('\n')
        description = ' '.join(description_str)
        odometer_tag = [item for item in description_str if 'odometer' in item]
        try:
            odometer = odometer_tag[0].split(': ')[1]
        except IndexError:
            odometer = None

        time_posted = self.driver.find_element(
            By.CLASS_NAME, 'date.timeago').get_attribute('title')
        return {'Name': name, 'Year': year, 'Price': price, 'Mileage': odometer, 'Date Posted': time_posted,
                'Description': description, 'Link': link}

    # Move to the next page
    def pagination(self):
        self.driver.get(self.url)
        next_page_button = self.driver.find_element(
            By.CLASS_NAME, 'bd-button.cl-next-page')
        next_page_button.click()
        self.url = self.driver.current_url

    def collecting_urls(self):
        self.driver.get(self.url)
        anchor_elements = self.driver.find_elements(
            By.CSS_SELECTOR, '#search-results-page-1 a')
        links = set([link.get_attribute(
            'href') for link in anchor_elements if link.get_attribute('href')])
        return links

    def run(self):
        self.driver.get(self.url)

        running = True
        while running:
            # collect urls from current page
            links = self.collecting_urls()
            print(f"Parsing {len(links)} items found in \n{self.url}")

            fieldnames = ['Name', 'Year', 'Price', 'Mileage',
                          'Date Posted', 'Description', 'Link']
            # loop over all the links collected and Write to csv
            with open('car_data.csv', 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if csvfile.tell() == 0:
                    writer.writeheader()
                for link in links:
                    if link not in self.parsed_links:
                        parsed_link = self.parse_item(link)
                        if not parsed_link:
                            pass
                        writer.writerow(parsed_link)
                        self.parsed_links.append(parsed_link)
                        time.sleep(1)

            # go to next page
            self.pagination()

            # quit loop if it's last page
            if len(links) < 120:
                running = False

        self.driver.quit()


while True:
    craig = Craig()
    craig.run()

    print("The Script will resume after 10 min or press 'Ctrl+C' to quit")
    time.sleep(600)  # 600 seconds = 10 minutes
