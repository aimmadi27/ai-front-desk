from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_cloud_project: str = ""
    google_application_credentials: str = ""
    gemini_api_key: str = ""

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    sendgrid_api_key: str = ""

    airtable_api_key: str = ""

    scheduler_secret: str = "change-me-in-production"

    app_env: str = "development"
    base_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"


settings = Settings()
