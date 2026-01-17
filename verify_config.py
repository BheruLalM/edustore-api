"""
Quick verification script to test environment configuration
"""
import sys
sys.path.insert(0, '.')

try:
    from core.config import mail_setting, service_setting
    
    print("✅ Configuration loaded successfully!\n")
    
    print("📧 Email Configuration:")
    print(f"   EMAIL_FROM: {mail_setting.EMAIL_FROM}")
    print(f"   EMAIL_FROM_NAME: {mail_setting.EMAIL_FROM_NAME}")
    print(f"   BREVO_API_KEY: {mail_setting.BREVO_API_KEY[:20]}...")
    
    print("\n💬 Chat Service Configuration:")
    print(f"   CHAT_SERVICE_URL: {service_setting.CHAT_SERVICE_URL}")
    
    print("\n✅ All configurations are valid!")
    
except Exception as e:
    print(f"❌ Configuration error: {e}")
    sys.exit(1)
