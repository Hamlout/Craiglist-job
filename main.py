from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
import csv
import time


class Craig:
    def __init__(self, url):
        self.url = url
        options = ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--headless')
        options.add_argument('--log-level=3')
        self.driver = Chrome(service=Service(
            ChromeDriverManager().install()), options=options)
        self.links_to_parse = []

    def parse_entries(self, writer, link):
        self.driver.get(link)
        price = self.driver.find_element(By.CLASS_NAME, 'price').text

        car_info = self.driver.find_elements(By.CLASS_NAME, 'attrgroup')
        title = car_info[0].text.split(maxsplit=1)
        year = title[0]
        name = title[1]

        print(f'Gathering info for {name}')

        description_str = car_info[1].text.strip().split('\n')
        description = ' '.join(description_str)
        odometer_tag = [item for item in description_str if 'odometer' in item]
        try:
            odometer = odometer_tag[0].split(': ')[1]
        except IndexError:
            odometer = None

        time_posted = self.driver.find_element(
            By.CLASS_NAME, 'date.timeago').get_attribute('title')
        writer.writerow(
            {'Name': name, 'Year': year, 'Price': price, 'Mileage': odometer, 'Date Posted': time_posted,
             'Description': description, 'Link': link}
        )

    def pagination(self):
        running = True
        while running:

            # Get links to parse
            anchor_elements = self.driver.find_elements(
                By.CSS_SELECTOR, '#search-results-page-1 a')
            links = [link.get_attribute(
                'href') for link in anchor_elements if link.get_attribute('href')]
            for link in links:
                if link not in self.links_to_parse:
                    self.links_to_parse.append(link)

            # If length of links is less than maximum entries per page
            if len(links) < 120:
                running = False

            # Move to the next page
            next_page_button = self.driver.find_element(
                By.CLASS_NAME, 'bd-button.cl-next-page')
            next_page_button.click()

    def run(self):
        self.driver.get(self.url)

        # loop over the pages to collect all links
        self.pagination()

        print(f"collected {len(self.links_to_parse)} to parse")

        fieldnames = ['Name', 'Year', 'Price', 'Mileage',
                      'Date Posted', 'Description', 'Link']
        # loop over all the links collected and Write to csv
        with open('car_data.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if csvfile.tell() == 0:
                writer.writeheader()
            for link in self.links_to_parse:
                self.parse_entries(writer, link)

        # quitting driver when leaving the while loop
        self.driver.quit()


while True:
    url = input("Enter the Craigslist link you want: ")
    # https://orangecounty.craigslist.org/search/orange-ca/cta?bundleDuplicates=1&lat=33.799&lon=-117.765&min_price=0&purveyor=owner&search_distance=7.5#search=1~gallery~0~0
    craig = Craig(url=url)
    craig.run()

    print("The Script will resume after 10 min or press 'Ctrl+C' to quit")
    time.sleep(600)  # 600 seconds = 10 minutes
