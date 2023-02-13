from utilities import *

driver = init_driver()
rss_data = read_data()
prev_data = read_seen_data()
settings = read_settings_data()

while True:
    print('Bot is now running!')
    soup_objects = gather_data_from_feeds(rss_data)
    items_by_category = traverse_items(soup_objects)
    valid_clients = get_valid_clients(items_by_category, prev_data, driver)
    if not (len(valid_clients) == 0):
        text_box = get_whatssapp_txt_box(settings['contact name'], driver)
        if text_box is None:
            print('Error : Contact not found!')
            print('Please enter correct contact name in settings.py and restart!')
            break
        for client in valid_clients:
            if client is not None:
                send_msg_to_txt_box(client.get_message(), text_box, client.category)
                time.sleep(5)
    write_seen_data(prev_data)
    print('BOT IS SLEEPING FOR ' + str(settings['refresh time(sec)']) + 'sec.(You can now close the window)')
    time.sleep(settings['refresh time(sec)'])
input('Press Enter to Exit!')
