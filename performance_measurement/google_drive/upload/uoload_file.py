import json
import os
import time
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the scope for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']


def get_access_token():
    # Load OAuth2 credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
        return creds.token
    flow = InstalledAppFlow.from_client_secrets_file(
    # Replace with your client secret file path
        '../sececret_path',
        scopes=SCOPES
    )
    creds = flow.run_local_server(port=0)

    # Save the credentials (you may want to save these to a file for later use)
    # For example:
    with open('token.json', 'w') as token_file:
        token_file.write(creds.to_json())

    return creds.token


def upload_file_to_google_drive(file_path):
    # Google Drive API endpoint for uploading files
    url = 'https://www.googleapis.com/upload/drive/v3/files?uploadType=media'
    print(f"Uploading file: {file_path}")
    # Open the file to be uploaded
    with open(file_path, 'rb') as f:
        file_content = f.read()

    # Start measuring the upload time
    start_time = time.time()
    # Define the file metadata, including its name
    metadata = {
        'name': file_path.split('/')[-1],
    }
    # Make the request to upload the file
    response = requests.post(
        'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart',
        headers={'Authorization': f'Bearer {get_access_token()}'},
        files={
            'data': ('metadata', json.dumps(metadata), 'application/json; charset=UTF-8'),
            'file': file_content,
        }
    )
    # # Make the request to upload the file
    # response = requests.post(
    #     url,
    #     headers={'Authorization': f'Bearer {get_access_token()}'},
    #     data=file_content,
    #     params={'name': file_path.split('/')[-1]}  # Using the file name as the title in Google Drive
    # )

    # End measuring the upload time
    end_time = time.time()

    if response.status_code == 200:
        print("File uploaded successfully")
        print(f"Upload time: {end_time - start_time} seconds")
        return end_time - start_time
    else:
        print("Failed to upload file")
        print(response.text)


if __name__ == '__main__':
    # get_access_token()
    # exit(0)
    # Replace 'file_path' with the path to the file you want to upload
    # file_path = 'test.txt'
    all_upload_time = {}
    for root, _, files in os.walk("upload_files"):
        for file in files:
            file_path = os.path.join(root, file)
            upload_time = upload_file_to_google_drive(file_path)
            print(f"File: {file}, Upload Time: {upload_time}")
            all_upload_time[file] = upload_time
    print(all_upload_time)
    with open("upload_time.json", "w") as f:
        json.dump(all_upload_time, f)
