import os
import json
import time
import tempfile
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from app.config import settings

logger = logging.getLogger(__name__)


def get_creds_file_path():
    json_content = os.getenv("GOOGLE_CREDS_JSON_CONTENT", "").strip()

    if json_content:
        try:
            json.loads(json_content)
            tmp = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".json",
                mode="w",
                encoding="utf-8"
            )
            tmp.write(json_content)
            tmp.close()
            logger.info("Google creds loaded from GOOGLE_CREDS_JSON_CONTENT")
            return tmp.name
        except Exception as e:
            logger.exception("Invalid GOOGLE_CREDS_JSON_CONTENT: %s", e)
            return None

    creds_path = settings.google_creds_json
    if creds_path and os.path.exists(creds_path):
        logger.info("Google creds loaded from file path: %s", creds_path)
        return creds_path

    logger.error("Google credentials not found")
    return None


def get_sheet():
    creds_path = get_creds_file_path()
    if not creds_path:
        return None

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    sh = client.open(settings.google_sheet_name)

    try:
        ws = sh.worksheet("Data")
    except Exception:
        ws = sh.add_worksheet(title="Data", rows=3000, cols=30)
        ws.append_row([
            "Сана",
            "Вақт",
            "Адрес",
            "Ориентир",
            "Код клиента",
            "Посл приб аналитика",
            "Код стенда",
            "Комментарии",
            "Заключение",
            "Фото стенда",
            "Фото маҳсулот",
            "Фото ташқари",
            "Аналитик исми",
            "Аналитик номери",
            "Рм маълумоти",
            "Дата решения",
        ])

    return ws


def append_visit_rows(data, agent, photo_links, retries=3, delay=2):
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            ws = get_sheet()
            if ws is None:
                return False, "Google Sheets ulanmadi"

            row = [
                data["date_str"],
                data["time_str"],
                data["address"],
                data["landmark"],
                data["client_code"],
                data["last_visit_date"],
                data["stand_code"],
                data["client_comment"],
                data["conclusion"],
                f'=HYPERLINK("{photo_links[0]}";"Фото стенда")' if len(photo_links) > 0 and photo_links[0] else "",
                f'=HYPERLINK("{photo_links[1]}";"Фото маҳсулот")' if len(photo_links) > 1 and photo_links[1] else "",
                f'=HYPERLINK("{photo_links[2]}";"Фото ташқари")' if len(photo_links) > 2 and photo_links[2] else "",
                agent.full_name,
                agent.phone,
                "",
                "",
            ]

            ws.append_row(row, value_input_option="USER_ENTERED")
            logger.info("Google Sheets row appended successfully on attempt %s", attempt)
            return True, "ok"

        except Exception as e:
            last_error = str(e)
            logger.exception("append_visit_rows failed on attempt %s: %s", attempt, e)
            if attempt < retries:
                time.sleep(delay)

    return False, last_error or "unknown error"