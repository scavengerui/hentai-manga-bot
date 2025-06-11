import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials

from dotenv import load_dotenv
load_dotenv()

CREDENTIALS_PATH = "./service_account.json"
PARENT_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

def get_drive_service():
    creds = Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=creds)

def get_or_create_subfolder(service, title):
    query = f"'{PARENT_FOLDER_ID}' in parents and name='{title}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get("files", [])
    
    if folders:
        return folders[0]["id"]
    
    # Create new folder
    file_metadata = {
        "name": title,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [PARENT_FOLDER_ID]
    }
    folder = service.files().create(body=file_metadata, fields="id").execute()
    return folder["id"]

def upload_pdf_to_drive(pdf_path, title):
    service = get_drive_service()
    folder_id = get_or_create_subfolder(service, title)

    file_metadata = {
        "name": os.path.basename(pdf_path),
        "parents": [folder_id]
    }
    media = MediaFileUpload(pdf_path, mimetype="application/pdf")
    uploaded = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

    file_id = uploaded["id"]

    # Make file viewable (not mandatory for private bot but good for drive links)
    permission = {
        "role": "reader",
        "type": "anyone"
    }
    try:
        service.permissions().create(fileId=file_id, body=permission).execute()
    except:
        pass

    view_link = f"https://drive.google.com/file/d/{file_id}/view"
    return view_link
