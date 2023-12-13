import html
import re
import xml.sax.saxutils as saxutils
from datetime import datetime

import bs4
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Models.ClientModel import Client
from Models.JobValidationModel import JobValidation


def read_data_from_feeds(rss_feed: dict) -> dict:
    soup_objects = {}
    for category_name, sub_categories in rss_feed.items():
        soup_obj_list = []
        for sub_category in sub_categories.values():
            response = requests.get(sub_category)
            xml_content = response.content.decode('utf-8')
            xml_content_unescaped = saxutils.unescape(xml_content)
            soup_object = BeautifulSoup(xml_content_unescaped, features="xml")
            soup_obj_list.append(soup_object)
        if not (len(soup_obj_list) == 0):
            soup_objects[category_name] = soup_obj_list
    return soup_objects


def read_items_by_category(soup_objects: dict):
    items_by_category = {}
    for category_name, soup_obj in soup_objects.items():
        items = []
        for obj in soup_obj:
            item = obj.findAll('item')
            items = items + item
        if not (len(items) == 0):
            items_by_category[category_name] = items
    return items_by_category


def get_client_from_item(item: bs4.element.Tag, category: str, valid_budget: float) -> Client:
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
    return Client(title=title, link=link, description=html.unescape(description), category=category, budget=budget,
                  posted_on=posted_on, country=country, valid_budget=valid_budget)


def validate_client(client: Client, driver: webdriver, job_validation: JobValidation) -> bool:
    if client is None:
        return False
    elapsed_minutes = abs((datetime.now() - client.job_post_time).total_seconds() / 60)
    if client.country.upper() in job_validation.unsupported_country:
        return False
    if elapsed_minutes > job_validation.valid_elapsed_job_time:
        return False
    if client.budget < job_validation.valid_client_budget:
        return False
    description_words = client.description.lower().split(' ')
    title_words = client.title.lower().split(' ')
    for inv_word in job_validation.invalid_keywords:
        if inv_word.lower() in description_words or inv_word.lower() in title_words:
            return False
    driver.get(client.link)
    try:
        driver.maximize_window()
    except WebDriverException:
        pass
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))
    body = BeautifulSoup(driver.find_element(By.CSS_SELECTOR, 'body').get_attribute('innerHTML'), 'html.parser')
    try:
        client_activity_items = body.find('ul', {
            'class': 'client-activity-items'}).find_all('li', {'class': 'ca-item'})
        for item in client_activity_items:
            title: str = item.find('span', {'class': 'title'}).text
            try:
                value: str = item.find('span', {'class': 'value'}).text
            except AttributeError:
                value: str = item.find('div', {'class': 'value'}).text
            integers = re.findall(r'\d+', value)
            int_values = [int(num) for num in integers]
            data_value: int = max(int_values)
            if 'Proposals' in title:
                if data_value > job_validation.valid_proposal_count:
                    return False
            elif 'Interviewing' in title:
                if data_value > job_validation.valid_interviewing_count:
                    return False
            elif 'Invites sent' in title:
                if data_value > job_validation.valid_invites_sent_count:
                    return False
        about_client_container = body.find('li', {'data-qa': 'client-job-posting-stats'})
        if '1 job posted' in about_client_container.text:
            return True
        hire_rate = about_client_container.find('div', {
            'class': 'text-muted mt-5'}).text.strip().split(' ')[0].replace("%", '')
        hire_rate = float(hire_rate)
        if hire_rate < job_validation.valid_hire_rate:
            return False

    except AttributeError:
        return True
    return True


def get_valid_clients(items_by_category: dict, prev_data: list, driver: webdriver,
                      job_validation: JobValidation) -> list:
    valid_clients = []
    for category, values in items_by_category.items():
        for value in values:
            client = get_client_from_item(value, category, job_validation.valid_client_budget)
            if client.link in prev_data:
                continue
            else:
                prev_data.append(client.link)
            if validate_client(client, driver, job_validation):
                valid_clients.append(client)
    return valid_clients
