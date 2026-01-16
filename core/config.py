from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    class Config:
        env_file = ".env"
        extra = "ignore"
    
    GOOGLE_CLIENT_ID: str = "715484256238-t9k2t4d6qoedf3bik945uk2depejkd8t.apps.googleusercontent.com"
        # Mapping for environment variables that might be lowercase in .env but uppercase here
        # Actually pydantic BaseSettings handles case-insensitivity by default usually, but let's be safe


class Database_Setting(AppSettings):
    DATABASE_URL: str


class MailSetting(AppSettings):
    SMTP_USER: str
    SMTP_PASS: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 20
    ALGORITHM: str = "HS256"


class ServiceSettings(AppSettings):
    CHAT_SERVICE_URL: str = "http://localhost:3000"


class RedisSetting(AppSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int


class StorageSetting(AppSettings):
    # Cloudinary Settings
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    
    STORAGE_PROVIDER: str = "cloudinary"


DatabaseSetting = Database_Setting()
mail_setting = MailSetting()
redis_setting = RedisSetting()
storage_setting = StorageSetting()
service_setting = ServiceSettings()
