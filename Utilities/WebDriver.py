import os
import time

import undetected_chromedriver
from bs4 import BeautifulSoup
from fake_useragent.fake import UserAgent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from undetected_chromedriver import WebElement
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
    tries = 5
    while tries > 0:
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))
            break
        except TimeoutException:
            tries -= 1
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
            contacts = driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"]')
        except NoSuchElementException:
            print('Error : Cant Load Whatsapp contacts (utilities.py : line 201)')
            time.sleep(sleep_time)
            sleep_time = 10
    for contact in contacts:
        contact_name = contact.text
        if my_contact in contact_name:
            click_element(driver=driver, element=contact)
            return True
    return False


def get_text_box(driver: WebDriver) -> WebElement:
    return driver.find_element(By.CSS_SELECTOR, 'div[id=main] footer div[role=textbox]')


def get_send_button(driver: WebDriver) -> WebElement:
    return driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Send"]')


def send_keys_to_element(driver: WebDriver, element: WebElement, keys: str):
    ActionChains(driver).send_keys_to_element(element, keys).perform()


def click_element(driver: WebDriver, element: WebElement):
    ActionChains(driver).move_to_element(element).click(element).perform()


def send_msg_to_txt_box(message: str, text_box: WebElement, category: str):
    message = convert_bmp(message)
    for m in message.splitlines():
        try:
            text_box.send_keys(m)
        except WebDriverException:
            continue
        text_box.send_keys(Keys.SHIFT, Keys.ENTER)
    text_box.send_keys(Keys.SHIFT, Keys.ENTER)
    text_box.send_keys(f'FROM : {category}\n')


def convert_bmp(text: str) -> str:
    return ''.join([char for char in text if ord(char) <= 0xFFFF])


def send_job_details_to_whatsapp(driver, contact_name, valid_clients) -> bool:
    if len(valid_clients) == 0:
        return True
    text_box = get_whatsapp_txt_box(contact_name, driver)
    if not text_box:
        print('Error : Contact not found!')
        print('Please enter correct contact name in settings.py and restart!')
        return False
    for client in valid_clients:
        if client is not None:
            text_box = get_text_box(driver)
            send_msg_to_txt_box(client.get_message(), text_box, client.category)
            time.sleep(5)
    return True
