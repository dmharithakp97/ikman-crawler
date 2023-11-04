
from google.oauth2.service_account import Credentials
from bs4 import BeautifulSoup
import time

from src.utils import get_spreadsheet, extract_json_data, backup_sheet, clear_data



def get_last_house_data(sheet):
    old_values = sheet.get_all_values()
    old_data_obj = []
    headers = old_values[0]
    url_index = headers.index('URL')
    for i in range(1, len(old_values)):
        data_row = old_values[i]
        url = data_row[url_index]
        if url not in old_data_obj:
            old_data_obj.append(url)
    print(f"Last house data processed successfully. Count: {len(old_data_obj)}")
    return old_data_obj
 

def get_last_desc_urls(sheet):
    old_values = sheet.get_all_values()
    headers = old_values[0]
    url_index = headers.index('URL')
    old_data_urls = []
    for i in range(1, len(old_values)):
        data_row = old_values[i]
        url = data_row[url_index]
        old_data_urls.append(url)
    print("Last description data processed successfully")
    return old_data_urls
 

def append_desc_data(sheet, data):
    last_row = len(sheet.get_all_values()) + 1
    range_str = 'A' + str(last_row) + ':B' + str(last_row + len(data))
    sheet.update(range_str, data)
    print(f"Appended data to : {sheet.title}, count: {len(data)}")

def handler(event, context):
    spreadsheet = get_spreadsheet()
    house_data_sheet = spreadsheet.worksheet("New")
    last_house_data = get_last_house_data(house_data_sheet)
    
    desc_data_sheet = spreadsheet.worksheet("Description")
    # backup_sheet(spreadsheet, desc_data_sheet)
    desc_data_urls = get_last_desc_urls(desc_data_sheet)     

    return_data = []
        
    start_time = time.time()
    for url in last_house_data:        
        if time.time() - start_time > 810:  # 13.5 minutes in seconds
            break
        try:
            if url not in desc_data_urls:
                data = extract_json_data(url)
                desc = data['adDetail']['data']['ad']['description']
                return_data.append([
                    f"{url}",
                    desc   
                ])                    
        except Exception as e:
            print(f"Error occurred: {e}. Skipping this iteration.")
            continue
        
     

    append_desc_data(desc_data_sheet, return_data)
    
    
# handler({}, {})


