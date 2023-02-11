import json
import time
from datetime import datetime
from telnetlib import EC

import bs4.element
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from client_class import Client


def init_driver() -> webdriver:
    chrome_options = Options()
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--profile-directory=Default')
    chrome_options.add_argument('--user-data-dir=C:\\Users\\hp\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1\\')
    chrome_options.add_experimental_option("prefs", prefs)
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.maximize_window()
    return driver


def read_data(filename: str = 'data.json') -> dict:
    try:
        with open(filename, 'r') as data_file:
            return json.load(data_file)
    except FileNotFoundError:
        return {}


def read_seen_data(filename: str = 'prev.json') -> list:
    try:
        with open(filename, 'r') as data_file:
            return json.load(data_file)
    except FileNotFoundError:
        return []


def read_settings_data(filename: str = 'settings.json') -> dict:
    try:
        with open(filename, 'r') as data_file:
            return json.load(data_file)
    except FileNotFoundError:
        return {}


def write_seen_data(prev_data: list, filename: str = 'prev.json'):
    try:
        with open(filename, 'w') as data_file:
            data_file.writelines(json.dumps(prev_data, indent=4))
    except FileNotFoundError:
        return


def gather_data_from_feeds(rss_feed: dict) -> dict:
    soup_objects = {}
    for category_name, sub_categories in rss_feed.items():
        soup_obj_list = []
        for sub_category in sub_categories.values():
            response = requests.get(sub_category)
            soup_object = BeautifulSoup(response.content, features="xml")
            soup_obj_list.append(soup_object)
        if not (len(soup_obj_list) == 0):
            soup_objects[category_name] = soup_obj_list
    return soup_objects


def traverse_items(soup_objects: dict):
    items_by_category = {}
    for category_name, soup_obj in soup_objects.items():
        items = []
        for obj in soup_obj:
            item = obj.findAll('item')
            items = items + item
        if not (len(items) == 0):
            items_by_category[category_name] = items
    return items_by_category


def parse_item(item: bs4.element.Tag, category: str) -> Client:
    title = item.find('title').getText()
    link = item.find('link').getText()
    description_data = item.find('description').getText()
    description_list = description_data.replace('<br />', '\n')
    description = ''
    budget = ''
    posted_on = ''
    country = ''
    for line in description_list.split('\n'):
        if not (len(line) == 0) and not line.startswith('<'):
            description += line
            description += '\n'
        elif 'BUDGET' in line.upper():
            line = line.replace('<b>', '').replace('</b>', '')
            description += line
            description += '\n'
            budget = line.split(':')[1].strip()
        elif 'POSTED ON' in line.upper():
            line = line.replace('<b>', '').replace('</b>', '')
            description += line
            description += '\n'
            posted_on = line.split('Posted On:')[1].strip()
        elif 'COUNTRY' in line.upper():
            line = line.replace('<b>', '').replace('</b>', '')
            description += line
            country = line.split(':')[1].strip()
        elif 'HOURLY RANGE' in line.upper():
            line = line.replace('<b>', '').replace('</b>', '')
            description += line
            description += '\n'
    return Client(title=title, link=link, description=description, category=category, budget=budget,
                  posted_on=posted_on, country=country)


def validate_client(client: Client, driver: webdriver) -> bool:
    if client is None:
        return False
    unsupported_country = ["INDIA", "PAKISTAN"]
    elapsed_minutes = abs((datetime.now() - client.job_post_time).total_seconds() / 60)
    if client.country.upper() in unsupported_country:
        return False
    if elapsed_minutes > 60:
        return False
    if client.budget < 50.0:
        return False
    driver.get(client.link)
    driver.maximize_window()
    WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))
    body = BeautifulSoup(driver.find_element(By.CSS_SELECTOR, 'body').get_attribute('innerHTML'), 'html.parser')
    try:
        about_client_container = body.find('li', {'data-qa': 'client-job-posting-stats'})
        if '1 job posted' in about_client_container.text:
            return True
        hire_rate = about_client_container.find('div', {
            'class': 'text-muted mt-5'}).text.strip().split(' ')[0].replace("%", '')
        hire_rate = float(hire_rate)
        if hire_rate < 40:
            return False
    except AttributeError:
        return True
    return True


def get_valid_clients(items_by_category: dict, prev_data: list, driver: webdriver) -> list:
    valid_clients = []
    for category, values in items_by_category.items():
        for value in values:
            client = parse_item(value, category)
            if client.link in prev_data:
                continue
            else:
                prev_data.append(client.link)
            if validate_client(client, driver):
                valid_clients.append(client)
    return valid_clients


def get_whatssapp_txt_box(my_contact: str, driver: webdriver):
    driver.get('https://web.whatsapp.com/')
    error_count = 0
    pane = None
    sleep_time = 5
    while error_count < 5:
        try:
            pane = driver.find_element(By.CSS_SELECTOR, '#pane-side')
            break
        except NoSuchElementException:
            if error_count <= 3:
                time.sleep(sleep_time)
                error_count += 1
                sleep_time += 3
                continue
            input("Please scan and press 'Enter' to continue")
            error_count += 1
    if pane is None:
        print('Error : Cannot send messages on whatsapp!')
        exit(1)
    time.sleep(3)
    contacts = driver.find_elements(By.CSS_SELECTOR, 'div.lhggkp7q.ln8gz9je.rx9719la')
    for contact in contacts:
        contact_name = contact.text
        if my_contact in contact_name:
            contact.click()
            footer = driver.find_element(By.TAG_NAME, 'footer')
            text_box = footer.find_element(By.CSS_SELECTOR,
                                           'div.fd365im1.to2l77zo.bbv8nyr4.gfz4du6o.ag5g9lrv.bze30y65.bdf91cm1.mwp4sxku')
            text_box.click()
            return text_box


def send_msg_to_txt_box(message: str, text_box, category: str):
    for m in message.splitlines():
        text_box.send_keys(m)
        text_box.send_keys(Keys.SHIFT + Keys.ENTER)
    text_box.send_keys('FROM : ' + category + '\n')
