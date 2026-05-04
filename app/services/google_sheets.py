import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from app.config import settings


def get_sheet():
    if not os.path.exists(settings.google_creds_json):
        return None

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        settings.google_creds_json,
        scope
    )
    client = gspread.authorize(creds)
    sh = client.open(settings.google_sheet_name)

    try:
        ws = sh.worksheet("Data")
    except Exception:
        ws = sh.add_worksheet(title="Data", rows=2000, cols=30)
        ws.append_row([
            "Сана",
            "Вақт",
            "Адрес",
            "Ориентир",
            "Код клиента",
            "Последняя прибытья аналитика",
            "Код стенда",
            "Комментарии от клиента",
            "Заключение",
            "Фото стенда",
            "Фото махсулот",
            "Фото ташкари",
            "Аналитик номи",
            "Аналитик номери",
        ])

    return ws


def append_visit_rows(data, agent, photo_links):
    ws = get_sheet()
    if ws is None:
        return False, "Google credentials topilmadi"

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
        f'=HYPERLINK("{photo_links[1]}";"Фото махсулот")' if len(photo_links) > 1 and photo_links[1] else "",
        f'=HYPERLINK("{photo_links[2]}";"Фото ташкари")' if len(photo_links) > 2 and photo_links[2] else "",
        agent.full_name,
        agent.phone,
    ]

    ws.append_row(row, value_input_option="USER_ENTERED")
    return True, "ok"