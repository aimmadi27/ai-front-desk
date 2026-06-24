from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = ""                 # postgresql+asyncpg://...

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Google Cloud
    google_cloud_project: str = ""
    google_application_credentials: str = ""

    # Gemini
    gemini_api_key: str = ""

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    # SendGrid
    sendgrid_api_key: str = ""

    # Airtable
    airtable_api_key: str = ""

    # Sentry
    sentry_dsn: str = ""

    # Internal
    scheduler_secret: str = "change-me-in-production"

    # App
    app_env: str = "development"
    base_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"


settings = Settings()
