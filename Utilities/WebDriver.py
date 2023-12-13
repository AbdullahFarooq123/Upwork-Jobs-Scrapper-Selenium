import os
import time

from bs4 import BeautifulSoup
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


def init_driver() -> webdriver:
    current_directory = os.getcwd()
    chrome_options = Options()
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_argument('--disable- notifications')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--profile-directory=Default')
    chrome_options.add_argument(f'--user-data-dir={current_directory}\\Chrome Profile\\')
    chrome_options.add_experimental_option("prefs", prefs)
    # chrome_options.add_argument("--headless")
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.maximize_window()
        return driver
    except WebDriverException:
        print('Chrome already running!')
        print('Please close the previous chrome window and restart!')
        exit(1)
    return None


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
                    # fd365im1 to2l77zo bbv8nyr4 gfz4du6o ag5g9lrv bze30y65 kao4egtt mwp4sxku
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
