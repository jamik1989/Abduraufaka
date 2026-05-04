import io
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from app.config import settings


SCOPES = ["https://www.googleapis.com/auth/drive"]


def get_drive_service():
    creds = Credentials.from_service_account_file(
        settings.google_creds_json,
        scopes=SCOPES,
    )
    return build("drive", "v3", credentials=creds)


async def upload_telegram_photo_to_drive(bot, telegram_file_id: str, filename: str):
    file = await bot.get_file(telegram_file_id)

    bio = io.BytesIO()
    await bot.download_file(file.file_path, destination=bio)
    bio.seek(0)

    service = get_drive_service()

    media = MediaIoBaseUpload(bio, mimetype="image/jpeg", resumable=False)
    metadata = {"name": filename}

    created = service.files().create(
        body=metadata,
        media_body=media,
        fields="id,name",
    ).execute()

    file_id = created["id"]

    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()

    direct_url = f"https://drive.google.com/uc?id={file_id}"
    view_url = f"https://drive.google.com/file/d/{file_id}/view"

    return {
        "file_id": file_id,
        "direct_url": direct_url,
        "view_url": view_url,
    }
