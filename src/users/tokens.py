import secrets
import jwt
from datetime import datetime, timedelta
import pytz

# To import JWT settings from project "settings.py" file
from django.conf import settings
JWT_AUTH = settings.JWT_AUTH

from .models import Users, AccessToken, RefreshToken

def token():
    return jwt.encode({'jti':secrets.token_urlsafe(60)}, JWT_AUTH['JWT_SECRET'], algorithm=JWT_AUTH['JWT_ALGORITHM']).decode('utf-8')


def token_obtain_pair(user):
    token_access = token()
    token_refresh = token()
    # Expiry for access token is 1 days
    access_expiry_at = datetime.now() + timedelta(days=1)
    
    # Expiry for refresh token is 15 days
    refresh_expiry_at = datetime.now() + timedelta(days=15)
    
    # will generate and save access token to the database
    db_access = AccessToken(
        user = user,
        token = token_access,
        expired_at = access_expiry_at
    )
    db_access.save()
    
    # will generate and save refresh token to the database
    db_refresh = RefreshToken(
        access_token_id = db_access.id,
        token = token_refresh,
        expired_at = refresh_expiry_at
    ).save()
    
    details = {
        "user_id" : user.id,
        "first_name" : user.first_name,
        "last_name" : user.last_name,
        "token":{
                "expiry_at" : access_expiry_at,
                "access_token" : token_access,
                "refresh_token" : token_refresh
                }
    }
    return details

def token_obtain_refresh(refresh_token):
    jwt.decode(refresh_token, JWT_AUTH['JWT_SECRET'], algorithm=JWT_AUTH['JWT_ALGORITHM'])
    utc=pytz.UTC
    db_refresh = RefreshToken.objects.filter(token = refresh_token).first()
    if not db_refresh:
        raise ValueError('Refresh token not found.')
    # check for refresh token expiry by removing timezone
    if datetime.now().replace(tzinfo=utc) >= db_refresh.expired_at.replace(tzinfo=utc):
        raise ValueError('Refresh token expired login again.')
    user = db_refresh.access_token.user
    # will delete the old access token
    AccessToken.objects.filter(token = db_refresh.access_token.token).first().delete()
    # will delete the old refresh token
    db_refresh.delete()
    # will return new pair of tokens
    return token_obtain_pair(user)