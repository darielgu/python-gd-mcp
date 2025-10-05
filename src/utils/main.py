from src.auth.main import refresh_credentials
from datetime import datetime, timezone


async def get_valid_token(user_id :str):
    """
    Return a valid Google access token for the user.
    If it's expired, refresh it and update the DB.
    """
    user_token = {} # update this to fetch from db
    if not user_token:
        raise Exception("User has no stored tokens")

    if user_token.expiry and user_token.expiry < datetime.now(timezone.utc):
        new_creds = refresh_credentials(user_token.refreshToken)
        # add update to DB logic
        
        return new_creds["access_token"]

    return user_token.accessToken