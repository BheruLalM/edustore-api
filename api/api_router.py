from fastapi import APIRouter
from api.auth.routes import router as request_otp
from api.auth.refresh_cookie import router as refresh
from api.auth.logout import router as logout
from api.profile.update_profile import router as update_profile
from api.profile.profile_get import router as get_profile
from api.profile.upload_url import router as avator
from api.profile.public_profile import router as public_profile
from api.profile.avatar_upload import router as avatar_upload
from api.document.document_upload import router as update_document
from api.document.get_document import router as get_doc
from api.document.user_documents import router as user_documents
from api.feed.feed import router as feed
from api.feed.download import router as download_doc
from api.feed.details import router as doc_details
from api.follow.follow import router as follow
from api.follow.unfollow import router as unfollow
from api.follow.list import router as list_of
from api.follow.status import router as follow_status
from api.feed.following_feed import router as following_feed
from api.search.document_search import router as document_search
from api.search.user_search import router as user_search
from api.comments.comments_route import router as comments
from api.like.like import router as like 
from api.bookmark.bookmark import router as bookmark
from api.document.post import router as create_post_router
from api.chat.chat_sync import router as chat_sync

api_router = APIRouter()

api_router.include_router(request_otp)
api_router.include_router(refresh)
api_router.include_router(logout)
api_router.include_router(update_profile)
api_router.include_router(get_profile)
api_router.include_router(avator)
api_router.include_router(public_profile)
api_router.include_router(avatar_upload)
api_router.include_router(update_document)
api_router.include_router(get_doc)
api_router.include_router(user_documents)
api_router.include_router(feed)
api_router.include_router(download_doc)
api_router.include_router(doc_details)
api_router.include_router(follow)
api_router.include_router(unfollow)
api_router.include_router(list_of)
api_router.include_router(follow_status)
api_router.include_router(document_search)
api_router.include_router(user_search)
api_router.include_router(comments)
api_router.include_router(like)
api_router.include_router(bookmark)


api_router.include_router(create_post_router)
api_router.include_router(chat_sync)







