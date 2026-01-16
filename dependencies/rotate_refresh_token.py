from dependencies.refresh_cookie_store import revoke_refresh_token,store_refresh_token

def rotate_refresh_token(
    user_id,token_id
):
    revoke_refresh_token(user_id, token_id)
    
    return store_refresh_token(user_id)