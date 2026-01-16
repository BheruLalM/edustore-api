import httpx
import logging
from core.config import service_setting

logger = logging.getLogger(__name__)

async def sync_user_to_chat(user_data: dict):
    """
    Syncs user data to the Chat Server.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{service_setting.CHAT_SERVICE_URL}/api/auth/sync",
                json=user_data,
                timeout=10.0
            )
            response.raise_for_status()
            logger.info(f"Successfully synced user {user_data.get('email')} to Chat Server.")
    except Exception as e:
        logger.error(f"Failed to sync user to Chat Server: {e}")
