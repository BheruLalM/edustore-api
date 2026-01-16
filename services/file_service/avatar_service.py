from sqlalchemy.orm import Session

from models.user import User
from models.student import Student
from services.storage.factory import StorageFactory
from services.storage.keys import profile_avatar_key
from dependencies.helper import _validate_avatar_key
from dependencies.content_type import _extension_from_content_type
from core.exceptions import (
    InvalidAvatarContentType,
    InvalidAvatarKey,
    AvatarUploadExpired,
    AvatarNotFound,
    StorageOperationFailed,
)


class AvatarService:

    @staticmethod
    def generate_upload_url(*, current_user: User, content_type: str) -> dict:
        try:
            extension = _extension_from_content_type(content_type)
        except ValueError:
            raise InvalidAvatarContentType()

        object_key = profile_avatar_key(
            user_id=current_user.id,
            extension=extension,
        )

        storage = StorageFactory.get_storage()

        try:
            upload_url = storage.generate_upload_url(
                object_key=object_key,
                content_type=content_type,
                expires_in=300,
            )
        except Exception:
            raise StorageOperationFailed()

        return {
            "upload_url": upload_url,
            "object_key": object_key,
        }

    @staticmethod
    def commit_avatar(
        *,
        db: Session,
        current_user: User,
        object_key: str,
    ) -> dict:
        try:
            _validate_avatar_key(
                object_key=object_key,
                user_id=current_user.id,
            )
        except ValueError:
            raise InvalidAvatarKey()

        storage = StorageFactory.get_storage()

        try:
            storage.generate_download_url(
                object_key=object_key,
                expires_in=60,
            )
        except Exception:
            raise AvatarUploadExpired()

        student = (
            db.query(Student)
            .filter(Student.user_id == current_user.id)
            .first()
        )

        old_avatar_key = None

        if not student:
            student = Student(
                user_id=current_user.id,
                profile_url=object_key,
            )
            db.add(student)
        else:
            old_avatar_key = student.profile_url
            student.profile_url = object_key

        db.commit()
        db.refresh(student)

        if old_avatar_key and old_avatar_key != object_key:
            try:
                storage.delete_object(object_key=old_avatar_key)
            except Exception:
                pass

        return {
            "profile_url": student.profile_url,
        }

    @staticmethod
    def delete_avatar(*, db: Session, current_user: User) -> dict:
        student = (
            db.query(Student)
            .filter(Student.user_id == current_user.id)
            .first()
        )

        if not student or not student.profile_url:
            raise AvatarNotFound()

        storage = StorageFactory.get_storage()

        try:
            storage.delete_object(object_key=student.profile_url)
        except Exception:
            pass

        student.profile_url = None
        db.commit()

        return {
            "deleted": True,
        }
