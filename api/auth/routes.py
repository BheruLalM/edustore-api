from fastapi import APIRouter, Depends, Response, BackgroundTasks
from sqlalchemy.orm import Session

from api.auth.schema import login, otp_verify, google_login
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from core.config import mail_setting, DatabaseSetting, app_settings
from db.deps import get_db
from models.user import User
from services.auth.jwt import create_access_token, create_refresh_token
from dependencies.refresh_cookie_store import store_refresh_token
from services.auth.otp import save_otp, otp_generator, invalidate_otp, verify_otp
from services.email.brevo_provider import BrevoProvider
from core.exceptions import (
    RedisUploadFailed,
    OTPCooldownActive,
    EmailSendFailed,
    RedisFetchFailed,
)
from services.chat.sync_service import sync_user_to_chat

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/request-otp")
def request_otp(data: login, background_tasks: BackgroundTasks):
    otp = otp_generator()
    email = data.email.strip().lower()

    try:
        save_otp(email, otp)

        subject = "EduStore OTP"
        body = f"This is your OTP {otp} valid for 5 minutes"

        emailer = BrevoProvider()
        background_tasks.add_task(emailer.send_email, email, subject, body)

        return {"message": "OTP sent successfully"}

    except (OTPCooldownActive, EmailSendFailed, RedisUploadFailed) as exc:
        # Let global exception handler handle these
        raise exc


@router.post("/verify-otp")
def verify_otp_endpoint(
    data: otp_verify,
    response: Response,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    email = data.email.strip().lower()

    if not verify_otp(email, data.otp):
        # Domain-level error
        from core.exceptions import DomainError
        raise DomainError("Invalid or expired OTP")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        user = User(email=email, is_verified=True)
        db.add(user)
    else:
        user.is_verified = True

    db.commit()
    db.refresh(user)



    # Sync to Chat Server
    # Get profile picture URL
    from models.student import Student
    from services.storage.factory import StorageFactory
    
    student = db.query(Student).filter(Student.user_id == user.id).first()
    profile_url_signed = ""
    
    if student and student.profile_url:
        if student.profile_url.startswith("http"):
             profile_url_signed = student.profile_url
        else:
            try:
                storage = StorageFactory.get_storage()
                profile_url_signed = storage.generate_download_url(
                    object_key=student.profile_url,
                    expires_in=31536000,
                )
            except Exception:
                profile_url_signed = ""

    full_name = student.name if student and student.name else email.split("@")[0]
    
    sync_data = {
        "email": user.email,
        "fullName": full_name,
        "postgresId": str(user.id),
        "profilePic": profile_url_signed,
        "bio": ""
    }
    background_tasks.add_task(sync_user_to_chat, sync_data)

    refresh_token_id = store_refresh_token(user.id)


    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id, refresh_token_id)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=app_settings.is_production,
        samesite="none" if app_settings.is_production else "lax",
        max_age=mail_setting.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=app_settings.is_production,
        samesite="none" if app_settings.is_production else "lax",
        max_age=mail_setting.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/google")
def google_auth_endpoint(
    data: google_login,
    response: Response,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    try:
        # Verify Google ID Token
        idinfo = id_token.verify_oauth2_token(
            data.credential, 
            google_requests.Request(), 
            DatabaseSetting.GOOGLE_CLIENT_ID
        )

        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            from core.exceptions import DomainError
            raise DomainError("Invalid issuer")

        email = idinfo["email"].lower()
        full_name = idinfo.get("name", email.split("@")[0])
        picture = idinfo.get("picture", "")

        # Get or Create User
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, is_verified=True)
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create Student record if it doesn't exist (optional, but good for consistency)
            from models.student import Student
            student = Student(user_id=user.id, name=full_name, profile_url=picture)
            db.add(student)
            db.commit()
        else:
            user.is_verified = True
            db.commit()
            
            # Update student info if missing
            from models.student import Student
            student = db.query(Student).filter(Student.user_id == user.id).first()
            if not student:
                student = Student(user_id=user.id, name=full_name, profile_url=picture)
                db.add(student)
                db.commit()
            elif not student.name:
                student.name = full_name
                db.commit()

        # Sync to Chat Server
        sync_data = {
            "email": user.email,
            "fullName": full_name,
            "postgresId": str(user.id),
            "profilePic": picture,
            "bio": ""
        }
        background_tasks.add_task(sync_user_to_chat, sync_data)

        # Issue Tokens
        refresh_token_id = store_refresh_token(user.id)
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id, refresh_token_id)

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=app_settings.is_production,
            samesite="none" if app_settings.is_production else "lax",
            max_age=mail_setting.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=app_settings.is_production,
            samesite="none" if app_settings.is_production else "lax",
            max_age=mail_setting.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        )

        return {
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    except ValueError:
        from core.exceptions import DomainError
        raise DomainError("Invalid Google token")
    except Exception as e:
        print(f"Google login error: {str(e)}")
        from core.exceptions import DomainError
        raise DomainError("Google authentication failed")
