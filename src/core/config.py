from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Resend
    resend_api_key: str
    from_email: str
    from_name: str = "Newsletter"

    # MongoDB
    mongodb_uri: str
    mongodb_db: str = "newsletter"

    # AWS S3
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "us-east-1"
    s3_bucket: str
    s3_public_base_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Singleton — fails fast at startup if any required variable is missing
settings = Settings()
