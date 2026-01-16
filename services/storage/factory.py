from services.storage.base import Storage
from core.config import storage_setting


class StorageFactory:
    @staticmethod
    def get_storage() -> Storage:
        provider = storage_setting.STORAGE_PROVIDER.lower()
        
        if provider == "cloudinary":
            from services.storage.cloudinary import CloudinaryStorage
            return CloudinaryStorage()
        
        raise RuntimeError(f"Unsupported storage provider: {provider}. Only 'cloudinary' is supported.")