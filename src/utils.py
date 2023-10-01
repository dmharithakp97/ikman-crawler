import boto3
from google.oauth2.service_account import Credentials
import gspread
import json
import requests

URL_PREFIX = "https://ikman.lk/en/ad/"


def get_spreadsheet():
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name="us-east-1"
    )

    # Retrieve the secret
    get_secret_value_response = client.get_secret_value(
        SecretId='arn:aws:secretsmanager:us-east-1:310340543340:secret:gsheet_client_secret-eq2CuG'
    )

    # Decode the secret
     # Decode the secret
    keyfile_dict = json.loads(get_secret_value_response['SecretString'])
    
    # Define the scopes
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive']
    
    # Create the credentials object with the scopes
    creds = Credentials.from_service_account_info(keyfile_dict, scopes=SCOPES)
    # ...

    # Access the Google Sheet
    gc = gspread.authorize(creds)
    spreadsheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1FegF2xLs9dXpwhZxhd80Zz_rKIgoyygC2RpWODEZiHE/edit#gid=921283701')
    return spreadsheet

def google_translate_ads_list(url):
    return url.replace('https://ikman.lk/', 'https://ikman-lk.translate.goog/') + '&_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=wapp'

def google_translate_ad(url):
    return 'https://translate.google.com/translate?sl=auto&tl=en&hl=en&u='+url+'&client=webapp'

def extract_json_data(final_url):
    print(f"Fetching: {final_url}")
    response = requests.get(final_url)
    response.encoding = 'utf-8'  # Set encoding to utf-8
    print(f"HTTP Status: {response.status_code}")
    data_str = response.text.split("window.initialData =")[1].split("</script>")[0]
    data = json.loads(data_str)
    return data


def backup_sheet(spreadsheet, sheet):
    backup_sheet_name = sheet.title + ' - Backup'
    backup_sheet = spreadsheet.worksheet(backup_sheet_name)
    backup_sheet.clear()

    # Copy all data from "New" sheet to "Old" sheet
    backup_sheet.append_rows(sheet.get_all_values())
    print(f"Backup complete: {backup_sheet_name}")


def clear_data(sheet):
    # Clear all the content from "New" sheet starting from row 2 onwards
    if sheet.row_count > 1:
        cell_range = sheet.range('A2:{}{}'.format(gspread.utils.rowcol_to_a1(sheet.row_count, sheet.col_count)[0], sheet.row_count))
        for cell in cell_range:
            cell.value = ''
        sheet.update_cells(cell_range)
    print(f"Data clear complete: {sheet.title}")