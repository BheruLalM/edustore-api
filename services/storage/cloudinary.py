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
        """Generate Cloudinary download URL with proper handling for raw files (PDFs)"""
        self._validate_object_key(object_key)
        
        try:
            import os
            # Use the exact same public_id logic as upload
            # Cloudinary public ID for matching MUST include the edustore prefix
            public_id = f"edustore/{object_key}"
            
            # Determine resource_type
            # IMPORTANT: PDFs use 'image' type for browser preview support
            _, ext = os.path.splitext(object_key)
            ext = ext.lower()
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.ico'}
            pdf_extensions = {'.pdf'}
            
            if ext in image_extensions:
                resource_type = 'image'
            elif ext in pdf_extensions:
                resource_type = 'image'  # PDFs as 'image' for browser preview
            else:
                resource_type = 'raw'
            
            # For images and PDFs, Cloudinary expects ID without extension
            # For raw files (docs), keep the extension
            if resource_type == 'image':
                public_id = public_id.rsplit('.', 1)[0]
            
            from cloudinary.utils import cloudinary_url
            
            # For raw files, we need to add flags for proper download/viewing
            if resource_type == 'raw':
                # Use fl_attachment for downloads, but for viewing we need the direct URL
                # We'll generate a URL that works for both preview and download
                url, _ = cloudinary_url(
                    public_id,
                    secure=True,
                    resource_type=resource_type,
                    type='upload'
                )
            else:
                # For images, standard URL generation
                url, _ = cloudinary_url(
                    public_id,
                    secure=True,
                    resource_type=resource_type
                )
            
            print(f"🔗 Generated {resource_type} URL: {url}")
            return url
            
        except Exception as e:
            print(f"❌ URL generation failed for {object_key}: {str(e)}")
            raise StorageOperationFailed(f"Failed to generate download URL: {str(e)}") from e
    
    def delete_object(self, *, object_key: str) -> None:
        """Delete file from Cloudinary"""
        self._validate_object_key(object_key)
        
        try:
            import os
            public_id = f"edustore/{object_key}"
            _, ext = os.path.splitext(object_key)
            ext = ext.lower()
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.ico'}
            pdf_extensions = {'.pdf'}
            
            if ext in image_extensions:
                resource_type = 'image'
            elif ext in pdf_extensions:
                resource_type = 'image'  # PDFs as 'image' for browser preview
            else:
                resource_type = 'raw'
            
            if resource_type == 'image':
                public_id = public_id.rsplit('.', 1)[0]
            
            cloudinary.uploader.destroy(
                public_id,
                resource_type=resource_type,
                invalidate=True
            )
        except Exception as e:
            raise StorageOperationFailed(f"Failed to delete object: {str(e)}") from e
    
    def upload_file(
        self,
        *,
        object_key: str,
        file_content: bytes,
        content_type: str,
    ) -> str:
        """Upload file directly to Cloudinary and return secure URL - Simplified Pathing"""
        self._validate_object_key(object_key)
        
        try:
            import os
            # Standardize: public_id includes the 'edustore/' prefix
            # This allows generate_download_url to be perfectly consistent.
            public_id = f"edustore/{object_key}"
            
            _, ext = os.path.splitext(object_key)
            ext = ext.lower()
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.ico'}
            pdf_extensions = {'.pdf'}
            
            if ext in image_extensions:
                resource_type = 'image'
            elif ext in pdf_extensions:
                resource_type = 'image'  # PDFs as 'image' for browser preview
            else:
                resource_type = 'raw'
            
            # For images and PDFs, we strip the extension from public_id
            # Cloudinary will serve them with proper content-type headers
            # For raw, we MUST keep it.
            if resource_type == 'image':
                public_id = public_id.rsplit('.', 1)[0]
                
            print(f"📤 Uploading: {public_id} (Type: {resource_type})")
            
            result = cloudinary.uploader.upload(
                file_content,
                public_id=public_id,
                resource_type=resource_type,
                overwrite=True
            )
            
            secure_url = result.get('secure_url')
            print(f"✅ Upload successful! URL: {secure_url}")
            return secure_url
            
        except Exception as e:
            print(f"❌ Upload failed: {str(e)}")
            raise StorageOperationFailed(f"Failed to upload file: {str(e)}") from e
