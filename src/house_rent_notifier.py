from difflib import SequenceMatcher
from datetime import date
from src.utils import get_parameter, get_spreadsheet, send_email
# from utils import get_parameter, get_spreadsheet, send_email

def handle(event, context):
    spreadsheet = get_spreadsheet()
    new_sheet = spreadsheet.worksheet("Rent")

    new_data = new_sheet.get_all_values()

    new_headers = new_data[0]

    status_index_new = new_headers.index('Status')

    new_ads_today = sum(1 for row in new_data if row[status_index_new] == '')

    # Rearrange rows before saving
    new_data = [new_data[0]] + sorted(new_data[1:], key=lambda row: ('' if row[status_index_new] == '' else ('1' if row[status_index_new] == 'Consider' else '2')))

    new_sheet.update('A1', new_data)

    send_notification(new_ads_today)
    

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def send_notification(new_ads_today):
    if(new_ads_today > 0):        
        from_email = get_parameter('ikman_crawler_from_email')
        to_email = get_parameter('ikman_crawler_to_emails').split(',')
        google_sheet_url = get_parameter('ikman_crawler_google_sheet_rent')
        formatted_date = date.today().strftime("%Y-%m-%d")
        subject = f"{new_ads_today} new houses found for rent on {formatted_date}"
        body_text = f'Click on the <a href="{google_sheet_url}">Google Sheet</a>'
        send_email(subject, body_text, to_email, from_email)
        
# handle({}, {})
