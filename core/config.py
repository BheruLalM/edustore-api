from pydantic_settings import BaseSettings
<<<<<<< HEAD
=======
from typing import Literal
import sys
>>>>>>> 5cfc842 (new version of it)


class AppSettings(BaseSettings):
    class Config:
        env_file = ".env"
        extra = "ignore"
    
<<<<<<< HEAD
    GOOGLE_CLIENT_ID: str = "715484256238-t9k2t4d6qoedf3bik945uk2depejkd8t.apps.googleusercontent.com"
        # Mapping for environment variables that might be lowercase in .env but uppercase here
        # Actually pydantic BaseSettings handles case-insensitivity by default usually, but let's be safe
=======
    # Environment Detection (REQUIRED)
    ENVIRONMENT: Literal["development", "production"] = "development"
    
    # Frontend URL for CORS
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = "715484256238-t9k2t4d6qoedf3bik945uk2depejkd8t.apps.googleusercontent.com"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT == "development"
>>>>>>> 5cfc842 (new version of it)


class Database_Setting(AppSettings):
    DATABASE_URL: str


class MailSetting(AppSettings):
    # Brevo API Settings
    BREVO_API_KEY: str
    EMAIL_FROM: str
    EMAIL_FROM_NAME: str = "EduStore"
    
    # SMTP Settings (Legacy)
    SMTP_USER: str
    SMTP_PASS: str
    
    # JWT Settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 20
    ALGORITHM: str = "HS256"


class ServiceSettings(AppSettings):
    CHAT_SERVICE_URL: str = "http://localhost:3000"


class RedisSetting(AppSettings):
    UPSTASH_REDIS_REST_URL: str = ""
    UPSTASH_REDIS_REST_TOKEN: str = ""


class StorageSetting(AppSettings):
    # Cloudinary Settings
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    
    STORAGE_PROVIDER: str = "cloudinary"
    DEFAULT_AVATAR_URL: str = "https://res.cloudinary.com/dly8p9v99/image/upload/v1736616449/edustore/avatars/default-avatar_v0r4j8.png"


<<<<<<< HEAD
=======
# Initialize settings
app_settings = AppSettings()
>>>>>>> 5cfc842 (new version of it)
DatabaseSetting = Database_Setting()
mail_setting = MailSetting()
redis_setting = RedisSetting()
storage_setting = StorageSetting()
service_setting = ServiceSettings()
<<<<<<< HEAD
=======


# Startup Validation
def validate_environment():
    """Validate required environment variables are set correctly"""
    errors = []
    
    # Validate environment value
    if app_settings.ENVIRONMENT not in ["development", "production"]:
        errors.append(f"ENVIRONMENT must be 'development' or 'production', got '{app_settings.ENVIRONMENT}'")
    
    # Production-specific validations
    if app_settings.is_production:
        # No localhost URLs in production
        if "localhost" in service_setting.CHAT_SERVICE_URL.lower():
            errors.append("CHAT_SERVICE_URL cannot contain 'localhost' in production")
        
        if "localhost" in app_settings.FRONTEND_URL.lower():
            errors.append("FRONTEND_URL cannot contain 'localhost' in production")
        
        # Strong secret key
        if len(mail_setting.SECRET_KEY) < 32:
            errors.append("SECRET_KEY must be at least 32 characters in production")

        # Brevo API Validations
        if not mail_setting.BREVO_API_KEY or mail_setting.BREVO_API_KEY == "your_api_key_here":
            errors.append("BREVO_API_KEY must be set to a valid key in production")
        elif not mail_setting.BREVO_API_KEY.startswith("xkeysib-"):
            errors.append("BREVO_API_KEY looks invalid (should start with 'xkeysib-')")

        if not mail_setting.EMAIL_FROM or "@" not in mail_setting.EMAIL_FROM:
            errors.append("EMAIL_FROM must be a valid email address in production")
    
    if errors:
        print("\n❌ ENVIRONMENT VALIDATION FAILED:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease fix the above errors in your .env file or environment variables.\n")
        sys.exit(1)
    
    print(f"✅ Environment validation passed (mode: {app_settings.ENVIRONMENT})")


# Run validation on import
validate_environment()
>>>>>>> 5cfc842 (new version of it)
