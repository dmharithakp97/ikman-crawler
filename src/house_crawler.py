from google.oauth2.service_account import Credentials
from bs4 import BeautifulSoup
import math
from utils import URL_PREFIX
from utils import get_spreadsheet, google_translate_ads_list, extract_json_data, backup_sheet, clear_data

MAX_PAGES_THRESHOLD = 10

URL_ARR = [
    ['Nugegoda', 'https://ikman.lk/en/ads/nugegoda/houses-for-sale?enum.bathrooms=2,3,4,5,6,7,8,9,10,10+&enum.bedrooms=3,4,5,6,7,8,9,10,10+&money.price.minimum=15000000&money.price.maximum=50000000'],
    ['Kotte', 'https://ikman.lk/en/ads/kotte/houses-for-sale?enum.bathrooms=2,3,4,5,6,7,8,9,10,10+&enum.bedrooms=3,4,5,6,7,8,9,10,10+&money.price.minimum=15000000&money.price.maximum=50000000'],
    ['Colombo 5', 'https://ikman.lk/en/ads/colombo-5/houses-for-sale?enum.bathrooms=2,3,4,5,6,7,8,9,10,10+&enum.bedrooms=3,4,5,6,7,8,9,10,10+&money.price.minimum=15000000&money.price.maximum=50000000'],
    ['Nawala', 'https://ikman.lk/en/ads/nawala/houses-for-sale?enum.bathrooms=2,3,4,5,6,7,8,9,10,10+&enum.bedrooms=3,4,5,6,7,8,9,10,10+&money.price.minimum=15000000&money.price.maximum=50000000']
]


def get_last_house_data(sheet):
    old_values = sheet.get_all_values()
    old_data_obj = {}
    headers = old_values[0]
    url_index = headers.index('URL')
    status_index = headers.index('Status')
    notes_index = headers.index('Notes')
    for i in range(1, len(old_values)):
        data_row = old_values[i]
        url = data_row[url_index]
        if url not in old_data_obj:
            old_data_obj[url] = [data_row[status_index], data_row[notes_index]]
    print("Last house data processed successfully")
    return old_data_obj


def save_house_data(sheet, data):
    sheet.update('A2:G' + str(len(data) + 1), data)
    print(f"Saved data to : {sheet.title}, count: {len(data)}")


def handler(event, context):
    spreadsheet = get_spreadsheet()
    house_data_sheet = spreadsheet.worksheet("New")
    backup_sheet(spreadsheet, house_data_sheet)
    last_house_data = get_last_house_data(house_data_sheet)    
    clear_data(house_data_sheet)    

    return_data = []
    for url_index in range(len(URL_ARR)):
        city = URL_ARR[url_index][0]
        url = google_translate_ads_list(URL_ARR[url_index][1])
        max_page_number = -1
        for page_no in range(1, MAX_PAGES_THRESHOLD + 1):
            final_url = f"{url}&page={page_no}"
            data = extract_json_data(final_url)
            ads = data['serp']['ads']['data']['ads']            
            
            if max_page_number < 0:
                pagination = data['serp']['ads']['data']['paginationData']
                max_page_number = math.ceil(pagination['total'] / pagination['pageSize'])
                print(f"max_page_number: {max_page_number}")

            for ad in ads:
                price = ad['price'].split('Rs ')[1]
                size = ad['details']
                ad_url = f"{URL_PREFIX}{ad['slug']}"
                consider, note, description = "", "", ""
                if ad_url in last_house_data:
                    consider = last_house_data[ad_url][0]
                    note = last_house_data[ad_url][1]

                return_data.append([
                    ad['title'],
                    city,
                    size,
                    price,
                    f"{URL_PREFIX}{ad['slug']}",
                    consider,
                    note
                ])                 

            if page_no == max_page_number:
                break

    save_house_data(house_data_sheet, return_data)
    
    
# handler({}, {})