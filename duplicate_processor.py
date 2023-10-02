from difflib import SequenceMatcher
from utils import get_spreadsheet
from utils import send_email
from datetime import date
from utils import get_parameter

def handle(event, context):
    spreadsheet = get_spreadsheet()
    new_sheet = spreadsheet.worksheet("New")
    desc_sheet = spreadsheet.worksheet("Description")

    new_data = new_sheet.get_all_values()
    desc_data = desc_sheet.get_all_values()

    new_headers = new_data[0]
    desc_headers = desc_data[0]

    url_index_new = new_headers.index('URL')
    status_index_new = new_headers.index('Status')
    total_index_new = new_headers.index('Total')
    notes_index_new = new_headers.index('Notes')

    url_index_desc = desc_headers.index('URL')
    desc_index_desc = desc_headers.index('Description')

    new_ads_today = sum(1 for row in new_data if row[status_index_new] == '')
    print(f"New ads today: {new_ads_today}")
    
    for i in range(1, len(new_data)):
        if new_data[i][status_index_new] == '':
            url_new = new_data[i][url_index_new]
            desc_new = next((desc_data[j][desc_index_desc] for j in range(1, len(desc_data)) if desc_data[j][url_index_desc] == url_new), None)            
            if desc_new:
                matched_rows = [desc_data[j] for j in range(1, len(desc_data)) if similar(desc_new, desc_data[j][desc_index_desc]) >= 0.9 and desc_data[j][url_index_desc] != url_new]
                matched_urls = [row[url_index_desc] for row in matched_rows]
                matched_new_rows = [new_data[k] for k in range(1, len(new_data)) if new_data[k][url_index_new] in matched_urls]
                
                if new_data[i][status_index_new] != '':
                    print(f"Status is not empty: {url_new}")
                    continue
                
                if len(matched_new_rows) == 0:
                    print(f"No matching rows: {url_new}")
                    continue;
                else:
                    print(f"{len(matched_new_rows)} matching rows for {url_new}")
                
                if all(row[status_index_new] == '' for row in matched_new_rows):
                    min_total_row = min((row for row in matched_new_rows if row[status_index_new] == ''), key=lambda row: float(row[total_index_new].replace(',', '')))
                    if float(new_data[i][total_index_new].replace(',', '')) < float(min_total_row[total_index_new].replace(',', '')):
                        new_data[i][status_index_new] = "Ignore"
                        new_data[i][notes_index_new] = min_total_row[url_index_new]
                        print(f"Ignore: {url_new}")
                    else:
                        for row in matched_new_rows:
                            row[status_index_new] = "Ignore"
                            row[notes_index_new] = new_data[i][url_index_new]
                            print(f"Ignore: {row[url_index_new]}")
                elif any(row[status_index_new] == "Consider" for row in matched_new_rows):
                    min_total_row = min((row for row in matched_new_rows if row[status_index_new] == "Consider"), key=lambda row: float(row[total_index_new].replace(',', '')))
                    if float(new_data[i][total_index_new].replace(',', '')) < float(min_total_row[total_index_new].replace(',', '')):
                        new_data[i][status_index_new] = "Consider"
                        print(f"Consider: {url_new}")
                    else:
                        new_data[i][status_index_new] = "Ignore"
                        new_data[i][notes_index_new] = min_total_row[url_index_new]
                        print(f"Ignore: {url_new}")
                elif any(row[status_index_new] == "Ignore" for row in matched_new_rows):
                    min_total_row = min((row for row in matched_new_rows if row[status_index_new] == "Ignore"), key=lambda row: float(row[total_index_new].replace(',', '')))
                    if float(new_data[i][total_index_new].replace(',', '')) >= float(min_total_row[total_index_new].replace(',', '')):
                        new_data[i][status_index_new] = "Ignore"
                        new_data[i][notes_index_new] = min_total_row[url_index_new]
                        print(f"Ignore: {url_new}")
               

    new_sheet.update('A1', new_data)

    new_ads_after_duplciate_removal = sum(1 for row in new_data if row[status_index_new] == '')
    print(f"New ads after removing duplicates: {new_ads_after_duplciate_removal}")        
    send_notification(new_ads_after_duplciate_removal)
    

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def send_notification(new_ads_after_duplciate_removal):
    if(new_ads_after_duplciate_removal > 0):        
        from_email = get_parameter('ikman_crawler_from_email')
        to_email = get_parameter('ikman_crawler_to_emails').split(',')
        google_sheet_url = get_parameter('ikman_crawler_google_sheet')
        formatted_date = date.today().strftime("%Y-%m-%d")
        subject = f"{new_ads_after_duplciate_removal} new houses found for sale on {formatted_date}"
        body_text = f'Click on the <a href="{google_sheet_url}">Google Sheet</a>'
        send_email(subject, body_text, to_email, from_email)
        
# handle({}, {})
