from google.oauth2.service_account import Credentials
from bs4 import BeautifulSoup
import math
from src.utils import URL_PREFIX
from src.utils import get_spreadsheet, extract_json_data, backup_sheet, clear_data, read_config

MAX_PAGES_THRESHOLD = 10
 
def get_last_house_urls(sheet):
    old_values = sheet.get_all_values()
    headers = old_values[0]
    url_index = headers.index('URL')
    old_data_urls = []
    for i in range(1, len(old_values)):
        data_row = old_values[i]
        url = data_row[url_index]
        old_data_urls.append(url)
    print("Last house data processed successfully")
    return old_data_urls
 

def append_house_data(sheet, data):
    last_row = len(sheet.get_all_values()) + 1
    range_str = 'A' + str(last_row) + ':G' + str(last_row + len(data))
    sheet.update(range_str, data)
    print(f"Appended data to : {sheet.title}, count: {len(data)}")

def extract_url_data(config):
    url_data = []
    for url in config['Source']:
        city = url.split('/')[5].replace('-', ' ').title()
        url_data.append([city, url])
    return url_data

def handler(event, context):
    spreadsheet = get_spreadsheet()

    config = read_config(spreadsheet)

    url_data = extract_url_data(config)
    
    house_data_sheet = spreadsheet.worksheet("New")
    # backup_sheet(spreadsheet, house_data_sheet)
    last_house_urls = get_last_house_urls(house_data_sheet)    
    # clear_data(house_data_sheet)    

    return_data = []
    for url_index in range(len(url_data)):
        city = url_data[url_index][0]
        print(f"Fetching data location: {city}")
        url = url_data[url_index][1]
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
                if ad_url not in last_house_urls:
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

    append_house_data(house_data_sheet, return_data)
    
    
# handler({}, {})
