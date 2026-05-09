import os
import requests


def send_report_to_panel(report_data, agent, photo_links):
    panel_api_url = os.getenv("PANEL_API_URL", "").strip()
    if not panel_api_url:
        return False, "PANEL_API_URL kiritilmagan"

    payload = {
        "agent_name": agent.full_name,
        "agent_phone": agent.phone,
        "address": report_data["address"],
        "landmark": report_data["landmark"],
        "client_code": report_data["client_code"],
        "last_trade_agent_visit": report_data["last_visit_date"],
        "stand_code": report_data["stand_code"],
        "client_comment": report_data["client_comment"],
        "conclusion": report_data["conclusion"],
        "created_at": None,
        "photos": [
            {
                "photo_type": "stand",
                "photo_link": photo_links[0] if len(photo_links) > 0 else "",
            },
            {
                "photo_type": "product",
                "photo_link": photo_links[1] if len(photo_links) > 1 else "",
            },
            {
                "photo_type": "outside",
                "photo_link": photo_links[2] if len(photo_links) > 2 else "",
            },
        ],
    }

    try:
        resp = requests.post(panel_api_url, json=payload, timeout=30)
        if resp.status_code == 200:
            return True, "OK"
        return False, f"HTTP {resp.status_code}: {resp.text}"
    except Exception as e:
        return False, str(e)