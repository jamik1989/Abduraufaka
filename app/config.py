from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = Field(..., alias="BOT_TOKEN")
    admin_ids: str = Field("", alias="ADMIN_IDS")
    group_chat_id: str = Field("", alias="GROUP_CHAT_ID")
    google_sheet_name: str = Field("PolevoyAgent", alias="GOOGLE_SHEET_NAME")
    google_creds_json: str = Field("credentials/service_account.json", alias="GOOGLE_CREDS_JSON")
    timezone: str = Field("Asia/Tashkent", alias="TIMEZONE")
    db_path: str = Field("data/app.db", alias="DB_PATH")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8-sig",
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def admin_id_list(self) -> list[int]:
        result = []
        for x in self.admin_ids.split(","):
            x = x.strip()
            if x.isdigit():
                result.append(int(x))
        return result


settings = Settings()