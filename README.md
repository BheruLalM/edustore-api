# 📚 EduStore Backend

A **production-grade backend system** built with **FastAPI** for secure document storage, sharing, and social interaction among students and educators.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.35-red?style=flat)](https://www.sqlalchemy.org/)
[![Redis](https://img.shields.io/badge/Redis-5.0.8-DC382D?style=flat&logo=redis&logoColor=white)](https://redis.io/)

---

## 🎯 Overview

EduStore is a **comprehensive educational platform backend** designed with **scalable architecture**, **clean separation of concerns**, and **real-world backend engineering patterns**. The system enables students to securely upload, share, and discover educational documents while building a social network around learning resources with features like likes, bookmarks, comments, and advanced search capabilities.

### Key Highlights

- 🔐 **Secure Authentication** - JWT-based auth with access & refresh tokens
- 📤 **Smart File Uploads** - Signed URL-based uploads (no file bytes on server)
- 🌐 **Public Feed** - Discover public educational documents
- 👥 **Social Features** - Follow/unfollow users, personalized feeds
- 💬 **Comments System** - Nested comments with replies support
- ❤️ **Likes & Bookmarks** - Save and like favorite documents
- 🔍 **Advanced Search** - Full-text search for documents and users
- 🗄️ **Storage Abstraction** - Pluggable storage providers (Supabase/Google Drive)
- 🔄 **Database Migrations** - Production-safe schema changes with Alembic
- ⚡ **High Performance** - Redis caching for OTP and session management
- 📧 **Email Integration** - SMTP-based OTP delivery
- 🛡️ **Rate Limiting** - Redis-based API rate limiting

---

## 🚀 Core Features

### Authentication & Authorization
- **OTP-based Authentication** - Email-based one-time password login
- **JWT Token System** - Secure access tokens (15 min) + refresh tokens (20 days)
- **Session Management** - Redis-backed refresh token storage
- **Protected Routes** - Dependency injection for route protection
- **Cookie-based Auth** - HttpOnly, Secure, SameSite cookies
- **Token Rotation** - Automatic refresh token rotation for enhanced security

### Document Management
- **2-Step Upload Flow** - Generate signed URL → Upload to storage → Commit metadata
- **Public/Private Visibility** - Control document access levels
- **Soft Delete** - Documents marked as deleted, not permanently removed
- **Document Types** - Support for notes, assignments, study materials
- **Metadata Tracking** - Original filename, content type, file size, timestamps
- **Document Download** - Secure signed download URLs with expiration

### User Profiles
- **Student Profiles** - Name, course, college, semester information
- **Avatar Management** - 2-step avatar upload with signed URLs
- **Profile Updates** - Partial updates with PATCH endpoint
- **Profile Visibility** - Public profile information for social features

### Social Features
- **Follow System** - Follow/unfollow other users
- **Follower/Following Lists** - View connections with pagination
- **Following Feed** - Personalized document feed from followed users
- **Public Feed** - Discover all public documents
- **User Discovery** - Search and find other students

### Engagement Features
- **Likes** - Like documents with toggle functionality
- **Bookmarks** - Save documents for later reference
- **Comments** - Add comments to documents
- **Nested Replies** - Reply to comments with hierarchical structure
- **Comment Management** - Edit and soft-delete comments

### Search & Discovery
- **Document Search** - Search documents by title, type, and content
- **User Search** - Find users by name, course, or college
- **Filtered Results** - Advanced filtering options
- **Pagination Support** - Efficient pagination for large result sets

### Storage System
- **Abstract Storage Interface** - Provider-agnostic design
- **Supabase Integration** - Production-ready Supabase storage
- **Signed URLs** - Secure, time-limited upload/download URLs
- **Factory Pattern** - Easy provider switching via configuration
- **Object Key Management** - Organized file structure in storage

---

## 🧱 Tech Stack

| Category             | Technology        | Version |
| -------------------- | ----------------- | ------- |
| **Framework**        | FastAPI           | 0.115.0 |
| **Server**           | Uvicorn           | 0.30.6  |
| **Database**         | PostgreSQL        | -       |
| **ORM**              | SQLAlchemy        | 2.0.35  |
| **Migrations**       | Alembic           | 1.17.2  |
| **Validation**       | Pydantic          | 2.9.2   |
| **Authentication**   | JWT (python-jose) | 3.3.0   |
| **Password Hashing** | Argon2            | 23.1.0  |
| **Caching**          | Redis             | 5.0.8   |
| **Email**            | FastAPI-Mail      | 1.4.1   |
| **Storage**          | Supabase          | -       |

---

## 📂 Project Structure

```
edustore-backend/
│
├── api/                          # API Routes Layer
│   ├── api_router.py            # Central router aggregator
│   │
│   ├── auth/                    # Authentication endpoints
│   │   ├── routes.py           # OTP request & verification
│   │   ├── refresh_cookie.py   # Token refresh endpoint
│   │   ├── logout.py           # Logout endpoint
│   │   └── schema.py           # Request/response schemas
│   │
│   ├── profile/                 # User profile management
│   │   ├── update_profile.py   # Update student details
│   │   ├── profile_get.py      # Get profile information
│   │   ├── upload_url.py       # Avatar upload URL generation
│   │   └── schema.py           # Profile schemas
│   │
│   ├── document/                # Document upload & management
│   │   ├── document_upload.py  # Upload URL generation & commit
│   │   ├── get_document.py     # Get user's documents
│   │   └── schema.py           # Document schemas
│   │
│   ├── feed/                    # Document feeds
│   │   ├── feed.py             # Public document feed
│   │   ├── following_feed.py   # Personalized feed
│   │   ├── details.py          # Document details
│   │   ├── download.py         # Download URL generation
│   │   └── schema.py           # Feed schemas
│   │
│   ├── follow/                  # Social features
│   │   ├── follow.py           # Follow user endpoint
│   │   ├── unfollow.py         # Unfollow user endpoint
│   │   └── list.py             # Followers/following lists
│   │
│   ├── like/                    # Like functionality
│   │   ├── like.py             # Like/unlike documents
│   │   └── schema.py           # Like schemas
│   │
│   ├── bookmark/                # Bookmark functionality
│   │   ├── bookmark.py         # Bookmark/unbookmark documents
│   │   └── schema.py           # Bookmark schemas
│   │
│   ├── comments/                # Comments system
│   │   ├── comments_route.py   # Comment CRUD operations
│   │   └── schema.py           # Comment schemas
│   │
│   └── search/                  # Search functionality
│       ├── document_search.py  # Document search endpoint
│       ├── user_search.py      # User search endpoint
│       └── schema.py           # Search schemas
│
├── services/                     # Business Logic Layer
│   ├── auth/                    # Authentication services
│   │   ├── jwt.py              # Token creation & validation
│   │   └── otp.py              # OTP generation & verification
│   │
│   ├── email/                   # Email services
│   │   ├── smtpprovider.py     # SMTP email sender
│   │   └── email_service.py    # Email service abstraction
│   │
│   ├── storage/                 # Storage abstraction
│   │   ├── base.py             # Abstract storage interface
│   │   ├── supabase.py         # Supabase implementation
│   │   ├── factory.py          # Storage factory
│   │   └── keys.py             # Object key generators
│   │
│   ├── feed_service/            # Feed logic
│   │   ├── feed_service.py     # Public feed service
│   │   └── following_feed_service.py  # Following feed service
│   │
│   ├── follow/                  # Follow/unfollow logic
│   │   ├── follow_service.py   # Follow operations
│   │   └── unfollow.py         # Unfollow operations
│   │
│   ├── file_service/            # File operations
│   │   ├── document_service.py # Document upload service
│   │   ├── avatar_service.py   # Avatar upload service
│   │   └── download.py         # Download URL generation
│   │
│   ├── like/                    # Like service
│   │   └── like_service.py     # Like/unlike logic
│   │
│   ├── bookmark/                # Bookmark service
│   │   └── bookmark_service.py # Bookmark/unbookmark logic
│   │
│   ├── comment_service/         # Comment service
│   │   ├── comments.py         # Comment CRUD logic
│   │   └── tree_creation.py    # Comment tree structure
│   │
│   └── search_service/          # Search service
│       ├── document_search.py  # Document search logic
│       └── user_search.py      # User search logic
│
├── models/                       # Database Models (SQLAlchemy)
│   ├── user.py                 # User model
│   ├── student.py              # Student profile model
│   ├── document.py             # Document model
│   ├── follow.py               # Follow relationship model
│   ├── likes.py                # Like model
│   ├── bookmark.py             # Bookmark model
│   └── comments.py             # Comment model (with nested replies)
│
├── dependencies/                 # FastAPI Dependencies
│   ├── get_current_user.py     # Auth dependency
│   ├── content_type.py         # Content type validation
│   ├── helper.py               # Helper functions
│   ├── auth.py                 # Auth utilities
│   ├── refresh_cookie_store.py # Refresh token storage
│   └── rotate_refresh_token.py # Token rotation
│
├── core/                         # Core Configuration
│   ├── config.py               # Environment settings
│   ├── exceptions.py           # Custom exceptions
│   └── redis.py                # Redis client
│
├── db/                           # Database Configuration
│   ├── base.py                 # SQLAlchemy base
│   ├── session.py              # Database session
│   └── deps.py                 # Database session dependency
│
├── alembic/                      # Database Migrations
│   └── versions/               # Migration files
│       ├── a40761a64fc4_initial_schema.py
│       ├── b02a83e39edb_initial_schema.py
│       ├── 2784fc090fc4_add_documents_table.py
│       ├── 6449282fafe6_add_follows_table.py
│       ├── 71f8b9ab01b4_add_follows_table.py
│       ├── 7788d5546191_follow_table_creation.py
│       ├── b796f708fd2a_harden_document_model.py
│       ├── 124c66072fdf_add_comments_table.py
│       └── 877c32e852ec_add_likes_and_bookmark_tables.py
│
├── main.py                       # FastAPI application entry point
├── requirements.txt              # Python dependencies
├── alembic.ini                   # Alembic configuration
├── .env                          # Environment variables
└── test.py                       # Test utilities

```

---

## 🔐 Authentication System

### OTP-Based Login Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Redis
    participant Email
    participant DB

    Client->>API: POST /auth/request-otp
    API->>API: Generate 6-digit OTP
    API->>Redis: Store OTP (5 min expiry)
    API->>Email: Send OTP via SMTP
    API-->>Client: OTP sent successfully

    Client->>API: POST /auth/verify-otp
    API->>Redis: Verify OTP
    Redis-->>API: Valid OTP
    API->>DB: Create/Update User
    API->>API: Generate JWT tokens
    API->>Redis: Store refresh token
    API-->>Client: Set cookies (access + refresh)
```

### Token Management

- **Access Token**: Short-lived (15 minutes), used for API authentication
- **Refresh Token**: Long-lived (20 days), used to obtain new access tokens
- **Token Storage**: Refresh tokens stored in Redis with user mapping
- **Cookie Security**: HttpOnly, Secure, SameSite=strict flags
- **Token Rotation**: Automatic refresh token rotation on each refresh

### Protected Routes

```python
@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    # current_user automatically injected after JWT validation
    return {"user_id": current_user.id}
```

---

## 📄 Document Upload System

### 2-Step Upload Flow

This architecture **never handles raw file bytes on the backend**, improving security and scalability.

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Storage
    participant DB

    Note over Client,DB: Step 1: Generate Upload URL
    Client->>API: POST /documents/upload-url
    API->>API: Generate object_key
    API->>Storage: Request signed upload URL
    Storage-->>API: Signed URL (5 min expiry)
    API-->>Client: {upload_url, object_key}

    Note over Client,DB: Step 2: Client Uploads Directly
    Client->>Storage: PUT file to signed URL
    Storage-->>Client: Upload successful

    Note over Client,DB: Step 3: Commit Metadata
    Client->>API: POST /documents/commit
    API->>Storage: Verify object exists
    API->>DB: Save document metadata
    API-->>Client: Document created
```

### Document Schema

```python
{
    "id": 123,
    "user_id": 456,
    "title": "Data Structures Notes",
    "doc_type": "notes",
    "object_key": "documents/456/uuid/filename.pdf",
    "original_filename": "ds_notes.pdf",
    "content_type": "application/pdf",
    "file_size": 2048576,
    "visibility": "public",  # or "private"
    "is_deleted": false,
    "created_at": "2025-12-27T10:00:00Z"
}
```

---

## 👤 Profile & Avatar System

### Avatar Upload (2-Step Process)

1. **Generate Upload URL**
   ```http
   POST /profile/avatar/upload-url
   Content-Type: application/json
   
   {
     "content_type": "image/jpeg"
   }
   ```

2. **Upload to Storage**
   ```http
   PUT <signed_upload_url>
   Content-Type: image/jpeg
   
   [binary image data]
   ```

3. **Backend Auto-Commit**
   - Backend verifies upload
   - Updates database with new avatar URL
   - Removes old avatar if present

### Profile Update

```http
PATCH /profile/update
Content-Type: application/json

{
  "name": "John Doe",
  "course": "Computer Science",
  "college": "MIT",
  "semester": "6"
}
```

---

## 🌐 Feed System

### Public Feed

Get all public documents with pagination:

```http
GET /feed/public?limit=20&offset=0
```

**Response:**
```json
{
  "documents": [
    {
      "id": 123,
      "title": "Machine Learning Notes",
      "doc_type": "notes",
      "user": {
        "id": 456,
        "name": "Jane Smith",
        "profile_url": "https://..."
      },
      "created_at": "2025-12-27T10:00:00Z",
      "likes_count": 42,
      "comments_count": 15
    }
  ],
  "total": 150
}
```

### Following Feed

Get documents from users you follow:

```http
GET /feed/following?limit=20&offset=0
```

---

## 👥 Social Features

### Follow User

```http
POST /users/{user_id}/follow
```

### Unfollow User

```http
POST /users/{user_id}/unfollow
```

### Get Followers/Following

```http
GET /users/{user_id}/followers?limit=20&offset=0
GET /users/{user_id}/following?limit=20&offset=0
```

**Response:**
```json
{
  "users": [
    {
      "id": 789,
      "name": "Alice Johnson",
      "profile_url": "https://...",
      "followed_at": "2025-12-20T10:00:00Z"
    }
  ],
  "total": 45
}
```

---

## 💬 Comments System

### Nested Comments Architecture

The comments system supports **hierarchical nested replies** with parent-child relationships.

### Add Comment

```http
POST /comments
Content-Type: application/json

{
  "document_id": 123,
  "content": "Great notes!",
  "parent_id": null  # null for top-level, or comment_id for reply
}
```

### Get Comments

```http
GET /comments/{document_id}?limit=20&offset=0
```

**Response:**
```json
{
  "comments": [
    {
      "id": 1,
      "user": {
        "id": 456,
        "name": "John Doe"
      },
      "content": "Great notes!",
      "created_at": "2025-12-27T10:00:00Z",
      "replies": [
        {
          "id": 2,
          "user": {
            "id": 789,
            "name": "Jane Smith"
          },
          "content": "Thanks!",
          "created_at": "2025-12-27T10:05:00Z"
        }
      ]
    }
  ]
}
```

### Update Comment

```http
PATCH /comments/{comment_id}
Content-Type: application/json

{
  "content": "Updated comment text"
}
```

### Delete Comment

```http
DELETE /comments/{comment_id}
```

---

## ❤️ Likes & Bookmarks

### Like/Unlike Document

```http
POST /documents/{document_id}/like
```

**Response:**
```json
{
  "liked": true,  # or false if unliked
  "likes_count": 43
}
```

### Bookmark/Unbookmark Document

```http
POST /documents/{document_id}/bookmark
```

**Response:**
```json
{
  "bookmarked": true,  # or false if unbookmarked
  "message": "Document bookmarked successfully"
}
```

### Get User's Bookmarks

```http
GET /bookmarks?limit=20&offset=0
```

---

## 🔍 Search System

### Document Search

Search documents by title, type, or content:

```http
GET /search/documents?query=machine+learning&doc_type=notes&limit=20&offset=0
```

**Response:**
```json
{
  "documents": [
    {
      "id": 123,
      "title": "Machine Learning Notes",
      "doc_type": "notes",
      "user": {
        "id": 456,
        "name": "Jane Smith"
      },
      "created_at": "2025-12-27T10:00:00Z"
    }
  ],
  "total": 25
}
```

### User Search

Search users by name, course, or college:

```http
GET /search/users?query=john&course=computer+science&limit=20&offset=0
```

**Response:**
```json
{
  "users": [
    {
      "id": 456,
      "name": "John Doe",
      "course": "Computer Science",
      "college": "MIT",
      "profile_url": "https://..."
    }
  ],
  "total": 12
}
```

---

## 🗄️ Storage Abstraction

### Design Pattern

The storage system uses the **Abstract Factory Pattern** for provider-agnostic file operations.

```python
# Abstract Interface
class Storage(ABC):
    @abstractmethod
    def generate_upload_url(self, *, object_key: str, content_type: str, expires_in: int = 300) -> str:
        pass
    
    @abstractmethod
    def generate_download_url(self, *, object_key: str, expires_in: int = 300) -> str:
        pass
    
    @abstractmethod
    def delete_object(self, *, object_key: str) -> None:
        pass
```

### Switching Providers

Change storage provider via environment variable:

```env
STORAGE_PROVIDER=supabase  # or "gdrive" (future)
```

### Current Implementation

- **Supabase Storage**: Production-ready implementation
- **Future**: Google Drive, AWS S3, Azure Blob

---

## 🔄 Database Migrations

### Alembic Setup

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

### Migration History

| Migration      | Description                            |
| -------------- | -------------------------------------- |
| `a40761a64fc4` | Initial schema (users, students)       |
| `b02a83e39edb` | Initial schema refinement              |
| `2784fc090fc4` | Add documents table                    |
| `6449282fafe6` | Add follows table                      |
| `71f8b9ab01b4` | Add follows table refinement           |
| `7788d5546191` | Follow table creation                  |
| `b796f708fd2a` | Harden document model (ENUMs, indexes) |
| `124c66072fdf` | Add comments table                     |
| `877c32e852ec` | Add likes and bookmark tables          |

---

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Supabase account (or other storage provider)

### 1. Clone Repository

```bash
git clone <repository-url>
cd edustore-backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/edustore

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=20
ALGORITHM=HS256

# Email (SMTP)
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Storage
STORAGE_PROVIDER=supabase
SUPABASE_URL=https://your-project.supabase.co/
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_BUCKET=student_files_photos
```

### 5. Database Setup

```bash
# Create database
createdb edustore

# Run migrations
alembic upgrade head
```

### 6. Run Development Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint            | Description                | Auth Required |
| ------ | ------------------- | -------------------------- | ------------- |
| POST   | `/auth/request-otp` | Request OTP via email      | ❌             |
| POST   | `/auth/verify-otp`  | Verify OTP & login         | ❌             |
| POST   | `/auth/refresh`     | Refresh access token       | ✅ (Refresh)   |
| POST   | `/auth/logout`      | Logout & invalidate tokens | ✅             |

### Profile

| Method | Endpoint                     | Description                | Auth Required |
| ------ | ---------------------------- | -------------------------- | ------------- |
| GET    | `/profile`                   | Get current user profile   | ✅             |
| PATCH  | `/profile/update`            | Update profile details     | ✅             |
| POST   | `/profile/avatar/upload-url` | Generate avatar upload URL | ✅             |

### Documents

| Method | Endpoint                | Description                  | Auth Required |
| ------ | ----------------------- | ---------------------------- | ------------- |
| POST   | `/documents/upload-url` | Generate document upload URL | ✅             |
| POST   | `/documents/commit`     | Commit uploaded document     | ✅             |
| GET    | `/documents`            | Get user's documents         | ✅             |
| DELETE | `/documents/{id}`       | Soft delete document         | ✅             |

### Feed

| Method | Endpoint                       | Description                       | Auth Required |
| ------ | ------------------------------ | --------------------------------- | ------------- |
| GET    | `/feed/public`                 | Get public documents              | ❌             |
| GET    | `/feed/following`              | Get documents from followed users | ✅             |
| GET    | `/feed/document/{id}`          | Get document details              | ❌             |
| GET    | `/feed/document/{id}/download` | Get download URL                  | ✅             |

### Social

| Method | Endpoint                | Description              | Auth Required |
| ------ | ----------------------- | ------------------------ | ------------- |
| POST   | `/users/{id}/follow`    | Follow user              | ✅             |
| POST   | `/users/{id}/unfollow`  | Unfollow user            | ✅             |
| GET    | `/users/{id}/followers` | Get user's followers     | ✅             |
| GET    | `/users/{id}/following` | Get users being followed | ✅             |

### Likes

| Method | Endpoint                | Description          | Auth Required |
| ------ | ----------------------- | -------------------- | ------------- |
| POST   | `/documents/{id}/like`  | Like/unlike document | ✅             |
| GET    | `/documents/{id}/likes` | Get document likes   | ❌             |

### Bookmarks

| Method | Endpoint                   | Description             | Auth Required |
| ------ | -------------------------- | ----------------------- | ------------- |
| POST   | `/documents/{id}/bookmark` | Bookmark/unbookmark doc | ✅             |
| GET    | `/bookmarks`               | Get user's bookmarks    | ✅             |

### Comments

| Method | Endpoint                  | Description           | Auth Required |
| ------ | ------------------------- | --------------------- | ------------- |
| POST   | `/comments`               | Add comment           | ✅             |
| GET    | `/comments/{document_id}` | Get document comments | ❌             |
| PATCH  | `/comments/{id}`          | Update comment        | ✅             |
| DELETE | `/comments/{id}`          | Delete comment        | ✅             |

### Search

| Method | Endpoint            | Description      | Auth Required |
| ------ | ------------------- | ---------------- | ------------- |
| GET    | `/search/documents` | Search documents | ❌             |
| GET    | `/search/users`     | Search users     | ❌             |

---

## 🧪 Testing

### Health Check

```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "message": "Hello! You are within the rate limit."
}
```

### Rate Limit Test

```bash
curl http://localhost:8000/test-rate-limit
```

### Manual Testing

Use the interactive API documentation at `/docs` to test endpoints.

---

## 🏗️ Architecture Principles

### Layered Architecture

```
┌─────────────────────────────────────┐
│         API Layer (Routes)          │  ← HTTP endpoints
├─────────────────────────────────────┤
│      Business Logic (Services)      │  ← Core logic
├─────────────────────────────────────┤
│      Data Access (Models/ORM)       │  ← Database operations
├─────────────────────────────────────┤
│       External Services (Storage)   │  ← Third-party integrations
└─────────────────────────────────────┘
```

### Design Patterns

- **Dependency Injection**: FastAPI's `Depends()` for loose coupling
- **Factory Pattern**: Storage provider abstraction
- **Repository Pattern**: Service layer for data access
- **Domain-Driven Design**: Custom exceptions for business logic
- **Separation of Concerns**: Clear separation between API, services, and models

### Error Handling

```python
# Custom domain exceptions
class DomainError(Exception):
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code

# Global exception handler
@app.exception_handler(DomainError)
async def domain_exception_handler(request, exc):
    return JSONResponse(
        status_code=ERROR_STATUS_MAP.get(type(exc), 400),
        content={"detail": str(exc), "error_code": exc.error_code}
    )
```

### Custom Exceptions

- `UserNotFound` (404)
- `CannotFollowYourself` (400)
- `NotFollowing` (404)
- `OTPCooldownActive` (429)
- `DocumentNotFound` (404)
- `DocumentAccessDenied` (403)
- `DownloadUrlGenerationFailed` (503)
- `DocumentOwnershipError` (400)
- `InvalidAvatarContentType` (400)
- `InvalidAvatarKey` (400)
- `AvatarUploadExpired` (400)
- `AvatarNotFound` (404)

---

## 🔒 Security Features

- ✅ **JWT Authentication** with short-lived access tokens
- ✅ **HttpOnly Cookies** prevent XSS attacks
- ✅ **Argon2 Password Hashing** (future password support)
- ✅ **Signed URLs** for secure file uploads/downloads
- ✅ **CORS Configuration** for controlled access
- ✅ **SQL Injection Protection** via SQLAlchemy ORM
- ✅ **Rate Limiting** on API endpoints (Redis-based)
- ✅ **Input Validation** with Pydantic schemas
- ✅ **Token Rotation** for enhanced security
- ✅ **OTP Cooldown** to prevent spam

---

## 📊 Database Schema

```mermaid
erDiagram
    User ||--o{ Student : has
    User ||--o{ Document : owns
    User ||--o{ Follow : follows
    User ||--o{ Follow : followed_by
    User ||--o{ Comment : writes
    User ||--o{ Like : likes
    User ||--o{ Bookmark : bookmarks
    Document ||--o{ Comment : has
    Document ||--o{ Like : has
    Document ||--o{ Bookmark : has
    Comment ||--o{ Comment : replies

    User {
        int id PK
        string email UK
        boolean is_verified
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    Student {
        int id PK
        int user_id FK
        string name
        string course
        string college
        string semester
        string profile_url
        datetime created_at
        datetime updated_at
    }

    Document {
        int id PK
        int user_id FK
        string title
        string doc_type
        string object_key UK
        string original_filename
        string content_type
        bigint file_size
        enum visibility
        boolean is_deleted
        datetime created_at
    }

    Follow {
        int id PK
        int follower_id FK
        int following_id FK
        datetime created_at
    }

    Like {
        int id PK
        int user_id FK
        int document_id FK
        datetime created_at
    }

    Bookmark {
        int id PK
        int user_id FK
        int document_id FK
        datetime created_at
    }

    Comment {
        int id PK
        int document_id FK
        int user_id FK
        int parent_id FK
        text content
        boolean is_deleted
        datetime created_at
        datetime updated_at
    }
```

---

## ✅ Completed Features

- [x] JWT-based authentication system
- [x] OTP email verification
- [x] Refresh token rotation
- [x] User profile management
- [x] Avatar upload system
- [x] Document upload with signed URLs
- [x] Public/private document visibility
- [x] Public document feed
- [x] Follow/unfollow system
- [x] Following feed
- [x] Secure document downloads
- [x] Storage abstraction (Supabase)
- [x] Database migrations with Alembic
- [x] Redis caching for sessions
- [x] Global exception handling
- [x] API documentation (Swagger/ReDoc)
- [x] Likes system
- [x] Bookmarks system
- [x] Comments with nested replies
- [x] Document search
- [x] User search
- [x] Rate limiting

---

## 🔜 Planned Enhancements

- [ ] **AI Document Q&A** - Chat with documents using LLMs
- [ ] **Recommendation System** - Personalized document suggestions
- [ ] **Document Versioning** - Track document updates
- [ ] **Analytics Dashboard** - User engagement metrics
- [ ] **Google Drive Integration** - Alternative storage provider
- [ ] **WebSocket Support** - Real-time notifications
- [ ] **Admin Panel** - Content moderation tools
- [ ] **Email Notifications** - Notify users of likes, comments, follows
- [ ] **Document Categories** - Organize documents by subject/topic
- [ ] **Advanced Filters** - Filter by course, semester, college
- [ ] **Document Sharing** - Share documents via links
- [ ] **User Badges** - Gamification features
- [ ] **Document Preview** - Preview documents before download

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where applicable
- Write docstrings for functions/classes
- Keep functions small and focused
- Add comments for complex logic

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Developer Notes

### Project Philosophy

- **Production-Ready**: Code is written for real-world deployment
- **Scalable**: Architecture supports horizontal scaling
- **Maintainable**: Clean separation of concerns
- **Secure**: Security-first approach to authentication & file handling
- **Developer-Friendly**: Easy onboarding with clear structure

### Performance Considerations

- Redis caching reduces database load
- Signed URLs eliminate backend file processing
- Database indexes on frequently queried columns
- Pagination for large result sets
- Soft deletes for data recovery
- Connection pooling for database efficiency

### Development Workflow

1. **Feature Development**: Create feature branch from `main`
2. **Database Changes**: Create Alembic migration
3. **Testing**: Test endpoints using `/docs`
4. **Code Review**: Submit PR for review
5. **Deployment**: Merge to `main` and deploy

### Environment Variables

All sensitive configuration is stored in `.env` file:
- Database credentials
- JWT secret key
- SMTP credentials
- Redis configuration
- Supabase credentials

**Never commit `.env` file to version control!**

---

## 🚀 Deployment

### Production Checklist

- [ ] Set strong `SECRET_KEY` in production
- [ ] Use production database (not SQLite)
- [ ] Configure Redis for production
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure CORS for production domain
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline
- [ ] Enable rate limiting
- [ ] Configure email service for production

### Recommended Hosting

- **Backend**: Railway, Render, DigitalOcean, AWS
- **Database**: Supabase, Railway, AWS RDS
- **Redis**: Upstash, Redis Cloud, AWS ElastiCache
- **Storage**: Supabase Storage, AWS S3, Cloudinary

---

## 📞 Support

For issues, questions, or contributions, please:
- Open an issue on GitHub
- Contact the development team
- Check the API documentation at `/docs`

---

**Built with ❤️ for students, by students**
