class AppException(Exception):
    default_message = "Application error"
    error_code = "APP_ERROR"

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)

    def __str__(self):
        return self.message


# =========================
# Infra / Service Errors
# =========================

class EmailSendFailed(AppException):
    default_message = "Failed to send email"
    error_code = "EMAIL_SEND_FAILED"


class SMTPConnectionFailed(AppException):
    default_message = "SMTP connection failed"
    error_code = "SMTP_CONNECTION_FAILED"


class SMTPTimeout(AppException):
    default_message = "SMTP connection timeout"
    error_code = "SMTP_TIMEOUT"


class RedisUploadFailed(AppException):
    default_message = "Redis upload failed"
    error_code = "REDIS_UPLOAD_FAILED"


class RedisFetchFailed(AppException):
    default_message = "Redis fetch failed"
    error_code = "REDIS_FETCH_FAILED"


class StorageOperationFailed(AppException):
    default_message = "Storage operation failed"
    error_code = "STORAGE_OPERATION_FAILED"


class RateLimitExceeded(AppException):
    default_message = "Too many requests, please try again later"
    error_code = "RATE_LIMIT_EXCEEDED"


class DatabaseOperationFailed(AppException):
    default_message = "Database operation failed"
    error_code = "DB_OPERATION_FAILED"


# =========================
# Domain Errors (Base)
# =========================

class DomainError(AppException):
    error_code = "DOMAIN_ERROR"


# =========================
# OTP Errors
# =========================

class OTPCooldownActive(DomainError):
    default_message = "OTP cooldown is active"
    error_code = "OTP.COOLDOWN_ACTIVE"


class OTPInvalid(DomainError):
    default_message = "Invalid OTP provided"
    error_code = "OTP.INVALID"


class OTPExpired(DomainError):
    default_message = "OTP has expired"
    error_code = "OTP.EXPIRED"


# =========================
# Auth / User Errors
# =========================

class AuthError(DomainError):
    error_code = "AUTH_ERROR"


class InvalidCredentials(AuthError):
    default_message = "Invalid email or password"
    error_code = "AUTH.INVALID_CREDENTIALS"


class UnauthorizedAccess(AuthError):
    default_message = "Unauthorized access"
    error_code = "AUTH.UNAUTHORIZED"


class UserInactive(AuthError):
    default_message = "User account is inactive"
    error_code = "AUTH.USER_INACTIVE"


# =========================
# Follow Errors
# =========================

class FollowError(DomainError):
    error_code = "FOLLOW_ERROR"


class CannotFollowYourself(FollowError):
    default_message = "You cannot follow yourself"
    error_code = "FOLLOW.CANNOT_FOLLOW_SELF"


class UserNotFound(FollowError):
    default_message = "User not found"
    error_code = "FOLLOW.USER_NOT_FOUND"


class NotFollowing(FollowError):
    default_message = "You are not following this user"
    error_code = "FOLLOW.NOT_FOLLOWING"


class AlreadyFollowing(FollowError):
    default_message = "You are already following this user"
    error_code = "FOLLOW.ALREADY_FOLLOWING"


# =========================
# Document Errors
# =========================

class DocumentError(DomainError):
    error_code = "DOCUMENT_ERROR"


class DocumentNotFound(DocumentError):
    default_message = "Document not found"
    error_code = "DOCUMENT.NOT_FOUND"


class DocumentAccessDenied(DocumentError):
    default_message = "You do not have access to this document"
    error_code = "DOCUMENT.ACCESS_DENIED"


class DownloadUrlGenerationFailed(DocumentError):
    default_message = "Failed to generate download URL"
    error_code = "DOCUMENT.DOWNLOAD_URL_FAILED"


class DocumentOwnershipError(DocumentError):
    default_message = "Object key does not belong to the user's documents"
    error_code = "DOCUMENT.OWNERSHIP_ERROR"


class DocumentDeleted(DocumentError):
    default_message = "Document is deleted"
    error_code = "DOCUMENT.DELETED"


# =========================
# Avatar Errors
# =========================

class AvatarError(DomainError):
    error_code = "AVATAR_ERROR"


class InvalidAvatarContentType(AvatarError):
    default_message = "Invalid avatar content type"
    error_code = "AVATAR.INVALID_CONTENT_TYPE"


class InvalidAvatarKey(AvatarError):
    default_message = "Invalid avatar object key"
    error_code = "AVATAR.INVALID_OBJECT_KEY"


class AvatarUploadExpired(AvatarError):
    default_message = "Uploaded avatar not found or expired"
    error_code = "AVATAR.UPLOAD_EXPIRED"


class AvatarNotFound(AvatarError):
    default_message = "No avatar to delete"
    error_code = "AVATAR.NOT_FOUND"


# =========================
# Search Errors
# =========================

class SearchError(DomainError):
    error_code = "SEARCH_ERROR"


class QueryTooShort(SearchError):
    default_message = "Search query too short"
    error_code = "SEARCH.QUERY_TOO_SHORT"


# =========================
# Comment Errors
# =========================

class CommentError(DomainError):
    error_code = "COMMENT_ERROR"


class CommentNotFound(CommentError):
    default_message = "Comment not found"
    error_code = "COMMENT.NOT_FOUND"


class InvalidParentComment(CommentError):
    default_message = "Invalid parent comment"
    error_code = "COMMENT.INVALID_PARENT"


class DocumentCommentNotAllowed(CommentError):
    default_message = "You are not allowed to comment on this document"
    error_code = "COMMENT.NOT_ALLOWED"


class CommentDepthExceeded(CommentError):
    default_message = "Maximum comment depth exceeded"
    error_code = "COMMENT.DEPTH_EXCEEDED"


# =========================
# Like Errors
# =========================

class LikeError(DomainError):
    error_code = "LIKE_ERROR"


class AlreadyLiked(LikeError):
    default_message = "Document already liked"
    error_code = "LIKE.ALREADY_LIKED"


class LikeNotFound(LikeError):
    default_message = "Like not found"
    error_code = "LIKE.NOT_FOUND"


class LikeNotAllowed(LikeError):
    default_message = "You are not allowed to like this document"
    error_code = "LIKE.NOT_ALLOWED"
    

# =========================
# Bookmark Errors
# =========================

class BookmarkError(DomainError):
    error_code = "BOOKMARK_ERROR"


class AlreadyBookmarked(BookmarkError):
    default_message = "Document already bookmarked"
    error_code = "BOOKMARK.ALREADY_EXISTS"


class BookmarkNotFound(BookmarkError):
    default_message = "Bookmark not found"
    error_code = "BOOKMARK.NOT_FOUND"


# =========================
# Error Status Map
# =========================

ERROR_STATUS_MAP = {
    OTPCooldownActive: 429,
    OTPInvalid: 400,
    OTPExpired: 400,
    InvalidCredentials: 401,
    UnauthorizedAccess: 401,
    UserInactive: 403,
    CannotFollowYourself: 400,
    UserNotFound: 404,
    NotFollowing: 400,
    AlreadyFollowing: 400,
    DocumentNotFound: 404,
    DocumentAccessDenied: 403,
    DownloadUrlGenerationFailed: 500,
    DocumentOwnershipError: 403,
    DocumentDeleted: 404,
    InvalidAvatarContentType: 400,
    InvalidAvatarKey: 400,
    AvatarUploadExpired: 404,
    AvatarNotFound: 404,
}

