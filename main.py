import time

from Models.BotSettingsModel import BotSettings
from Models.JobValidationModel import JobValidation
from Utilities.FileReader import read_prev_seen_jobs, read_category_feed_data, read_settings_data
from Utilities.FileWriter import write_seen_data
from Utilities.RSS import read_data_from_feeds, read_items_by_category, get_valid_clients
from Utilities.WebDriver import init_driver, send_job_details_to_whatsapp, get_user_agent

rss_links = read_category_feed_data()
prev_data = read_prev_seen_jobs()
settings_json = read_settings_data()
settings = BotSettings(**settings_json)
validation_settings = JobValidation(**settings.ValidationSettings)
driver = init_driver()
driver.get("https://www.upwork.com/ab/account-security/login")
while True:
    print('Bot is now running!')
    soup_objects = read_data_from_feeds(rss_links)
    items_by_category = read_items_by_category(soup_objects)
    valid_clients = get_valid_clients(items_by_category, prev_data, driver, validation_settings)
    if not send_job_details_to_whatsapp(driver, settings.contact_name, valid_clients):
        break
    write_seen_data(prev_data)
    print('BOT IS SLEEPING FOR ' + str(settings.refresh_time) + 'sec.(You can now close the window)')
    time.sleep(settings.refresh_time)
input('Press Enter to Exit!')
