import os
import time

import undetected_chromedriver
from bs4 import BeautifulSoup
from fake_useragent.fake import UserAgent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def init_driver(user_agent: str = None) -> webdriver:
    current_directory = os.getcwd()
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    if user_agent:
        chrome_options.add_argument("--user-agent={}".format(user_agent))
    chrome_options.add_argument('--profile-directory=Default')
    chrome_options.add_argument(f'--user-data-dir={current_directory}\\Chrome Profile\\')
    try:
        return undetected_chromedriver.Chrome(service=Service(ChromeDriverManager().install()),
                                              options=chrome_options)
    except WebDriverException as ex:
        print('Chrome already running!')
        print('Please close the previous chrome window and restart!')
        print(f"{ex.msg}")
        exit(1)


def get_user_agent(chrome_version: str) -> str:
    base_chrome_ua = UserAgent(browsers=['chrome'], os='windows').chrome
    parts = base_chrome_ua.split(' ')
    new_parts = [f'Chrome/{chrome_version}' if 'Chrome' in part else part for part in parts]
    return ' '.join(new_parts)


def get_whatsapp_txt_box(my_contact: str, driver: webdriver):
    driver.get('https://web.whatsapp.com/')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))
    time.sleep(5)
    body = BeautifulSoup(driver.find_element(By.CSS_SELECTOR, 'body').get_attribute('innerHTML'), 'html.parser')
    qr_code = body.find('div', {'data-testid': 'qrcode'})
    if qr_code is not None:
        input("Please login and press 'Enter' to continue")
    pane = None
    sleep_time = 5
    while pane is None:
        try:
            pane = driver.find_element(By.CSS_SELECTOR, '#pane-side')
        except NoSuchElementException:
            print('Error : Cant Load Whatsapp left pane (utilities.py : line 191)')
            time.sleep(sleep_time)
            sleep_time = 10
    contacts = None
    sleep_time = 5
    while contacts is None:
        try:
            contacts = driver.find_elements(By.CSS_SELECTOR, 'div.lhggkp7q.ln8gz9je.rx9719la')
        except NoSuchElementException:
            print('Error : Cant Load Whatsapp contacts (utilities.py : line 201)')
            time.sleep(sleep_time)
            sleep_time = 10
    for contact in contacts:
        contact_name = contact.text
        if my_contact in contact_name:
            contact.click()
            footer = None
            sleep_time = 5
            while footer is None:
                try:
                    footer = driver.find_element(By.TAG_NAME, 'footer')
                except NoSuchElementException:
                    print('Error : Cant Load Whatsapp contact footer (utilities.py : line 214)')
                    time.sleep(sleep_time)
                    sleep_time = 10
            text_box = None
            while text_box is None:
                try:
                    text_box = footer.find_element(By.XPATH, '//footer//div[@role="textbox"]')
                except NoSuchElementException:
                    print('Error : Cant Load Whatsapp text box (utilities.py : line 222)')
                    time.sleep(sleep_time)
                    sleep_time = 10
            text_box.click()
            return text_box
    return None


def send_msg_to_txt_box(message: str, text_box, category: str):
    for m in message.splitlines():
        try:
            text_box.send_keys(m)
        except WebDriverException:
            continue
        text_box.send_keys(Keys.SHIFT + Keys.ENTER)
    text_box.send_keys('FROM : ' + category + '\n')


def send_job_details_to_whatsapp(driver, contact_name, valid_clients) -> bool:
    if len(valid_clients) == 0:
        return True
    text_box = get_whatsapp_txt_box(contact_name, driver)
    if text_box is None:
        print('Error : Contact not found!')
        print('Please enter correct contact name in settings.py and restart!')
        return False
    for client in valid_clients:
        if client is not None:
            send_msg_to_txt_box(client.get_message(), text_box, client.category)
            time.sleep(5)
    return True
