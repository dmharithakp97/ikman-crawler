import boto3
from google.oauth2.service_account import Credentials
import gspread
import json
import requests
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import os

URL_PREFIX = "https://ikman.lk/en/ad/"

def get_parameter(name):
    ssm = boto3.client('ssm', region_name='us-east-1')
    parameter = ssm.get_parameter(Name=name, WithDecryption=True)
    return parameter['Parameter']['Value']

def send_email(subject, body_text, to_addresses, from_address):
    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name="us-east-1")

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': to_addresses,
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': "UTF-8",
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': subject,
                },
            },
            Source=from_address,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

def get_spreadsheet():
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name="us-east-1"
    )

    # Retrieve the secret
    get_secret_value_response = client.get_secret_value(
        SecretId=os.environ['SECRET_ARN']
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
    spreadsheet = gc.open_by_url(get_parameter('ikman_crawler_google_sheet'))
    return spreadsheet

def extract_json_data(final_url):
    for attempt in range(3):
        response = requests.get(final_url)
        response.encoding = 'utf-8'  # Set encoding to utf-8
        print(f"HTTP Status: {response.status_code}, URL: {final_url}")
        if response.status_code == 200:
            data_str = response.text.split("window.initialData =")[1].split("</script>")[0]
            data = json.loads(data_str)
            return data
        else:
            print(f"Attempt {attempt+1} failed. Retrying...")
    raise Exception(f"Failed to fetch data from {final_url} after 3 attempts. HTTP Status: {response.status_code}")


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

def read_config(spreadsheet):
    config_sheet = spreadsheet.worksheet("Config")
    config_values = config_sheet.get_all_values()
    config_map = {}
    key_index = config_values[0].index('Key')
    value_index = config_values[0].index('Value')
    for i in range(1, len(config_values)):
        key = config_values[i][key_index]
        value = config_values[i][value_index]
        if key in config_map:
            config_map[key].append(value)
        else:
            config_map[key] = [value]
    print(f"Config read successfully: {len(config_map)} keys found")
    return config_map    