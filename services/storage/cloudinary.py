"""
Cloudinary Storage Implementation
Handles file uploads and URL generation using Cloudinary
"""
import time
import cloudinary
import cloudinary.uploader
import cloudinary.api
from services.storage.base import Storage
from core.config import storage_setting
from core.exceptions import StorageOperationFailed


class CloudinaryStorage(Storage):
    """Cloudinary storage provider implementation"""
    
    def __init__(self):
        """Initialize Cloudinary with credentials from config"""
        cloudinary.config(
            cloud_name=storage_setting.CLOUDINARY_CLOUD_NAME,
            api_key=storage_setting.CLOUDINARY_API_KEY,
            api_secret=storage_setting.CLOUDINARY_API_SECRET,
            secure=True
        )
    
    def _validate_object_key(self, object_key: str):
        """Validate object key format"""
        if not object_key:
            raise ValueError("object_key empty")
        if ".." in object_key:
            raise ValueError("invalid object_key")
    
    def generate_upload_url(
        self,
        *,
        object_key: str,
        content_type: str,
        expires_in: int = 300,
    ) -> str:
        """
        For Cloudinary, we don't use presigned URLs like Supabase
        Instead, return a simple upload URL
        The actual upload will be handled by upload_file method
        """
        self._validate_object_key(object_key)
        
        # Return the Cloudinary upload endpoint
        # This is just for API compatibility - actual uploads use upload_file()
        upload_url = f"https://api.cloudinary.com/v1_1/{storage_setting.CLOUDINARY_CLOUD_NAME}/auto/upload"
        return upload_url
    
    def generate_download_url(
        self,
        *,
        object_key: str,
        expires_in: int = 300,
    ) -> str:
        """
        Generate Cloudinary download URL
        Note: Cloudinary URLs don't expire by default (public URLs)
        """
        self._validate_object_key(object_key)
        
        try:
            # Build Cloudinary URL using CloudinaryImage
            # Format: https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}
            # Cloudinary automatically determines resource type from the file
            public_id = f"edustore/{object_key}"
            
            # Use CloudinaryImage for proper URL construction
            from cloudinary import CloudinaryImage
            url = CloudinaryImage(public_id).build_url(
                secure=True,
                type='upload',
                version=False  # Don't include version in URL
            )
            
            print(f"🔗 Generated URL: {url}")
            
            return url
            
        except Exception as e:
            raise StorageOperationFailed(f"Failed to generate download URL: {str(e)}") from e
    
    def delete_object(self, *, object_key: str) -> None:
        """Delete file from Cloudinary"""
        self._validate_object_key(object_key)
        
        try:
            cloudinary.uploader.destroy(
                f"edustore/{object_key}",
                invalidate=True  # Invalidate CDN cache
            )
        except Exception as e:
            raise StorageOperationFailed(f"Failed to delete object: {str(e)}") from e
    
    def upload_file(
        self,
        *,
        object_key: str,
        file_content: bytes,
        content_type: str,
    ) -> None:
        """Upload file directly to Cloudinary"""
        self._validate_object_key(object_key)
        
        try:
            # Remove file extension from object_key since Cloudinary adds it automatically
            import os
            object_key_without_ext = os.path.splitext(object_key)[0]
            public_id = f"edustore/{object_key_without_ext}"
            
            print(f"📤 Uploading to Cloudinary: {public_id}")
            
            result = cloudinary.uploader.upload(
                file_content,
                public_id=public_id,
                resource_type='auto',  # Auto-detect image/video/raw
                overwrite=True  # Allow overwriting
            )
            
            print(f"✅ Upload successful! URL: {result.get('secure_url')}")
            
        except Exception as e:
            print(f"❌ Upload failed: {str(e)}")
            raise StorageOperationFailed(f"Failed to upload file: {str(e)}") from e
