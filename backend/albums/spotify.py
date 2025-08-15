import os
import base64
import requests
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import SpotifyToken

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com/"

SCOPES = "user-read-email user-read-private"

def get_spotify_auth_url():
    return (
        f"{SPOTIFY_AUTH_URL}?response_type=code"
        f"&client_id={settings.SPOTIFY_CLIENT_ID}"
        f"&redirect_uri={settings.SPOTIFY_REDIRECT_URI}"
        f"&scope={SCOPES}"
    )

def get_tokens(code):
    """Exchange auth code for access + refresh tokens."""
    auth_str = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
    b64_auth_str = base64.urlsafe_b64encode(auth_str.encode()).decode()

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
    }

    headers = {
        "Authorization": f"Basic {b64_auth_str}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.post(SPOTIFY_TOKEN_URL, data=payload, headers=headers)
    return response.json()


def _basic_auth_header():
    """Return Basic auth header value for Spotify token endpoint"""
    auth_str = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
    b64 = base64.urlsafe_b64encode(auth_str.encode()).decode()
    return {"Authorization": f"Basic {b64}", "Content-Type": "application/x-www-form-urlencoded"}

def build_auth_url(state: str):
    """Return a Spotify authorization URL including state (must be url-encoded by Django redirect)"""
    params = {
        "response_type": "code",
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": SCOPES,
        "state": state,
        # "show_dialog": "true"  # optional: forces approval screen
    }
    # build query string manually to keep simple
    qs = "&".join([f"{k}={requests.utils.quote(v)}" for k, v in params.items()])
    return f"{SPOTIFY_AUTH_URL}?{qs}"

def exchange_code_for_token(code):
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
    }
    headers = _basic_auth_header()
    resp = requests.post(SPOTIFY_TOKEN_URL, data=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()

def refresh_access_token(refresh_token):
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    headers = _basic_auth_header()
    resp = requests.post(SPOTIFY_TOKEN_URL, data=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()

def tokens_response_to_saved_fields(token_json):
    """
    token_json example:
    {
      "access_token": "...",
      "token_type": "Bearer",
      "scope": "...",
      "expires_in": 3600,
      "refresh_token": "..."  # only present on code exchange
    }
    """
    access = token_json.get("access_token")
    refresh = token_json.get("refresh_token")
    token_type = token_json.get("token_type")
    scope = token_json.get("scope", "")
    expires_in = token_json.get("expires_in", 3600)
    expires_at = timezone.now() + timedelta(seconds=int(expires_in))
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": token_type,
        "scope": scope,
        "expires_at": expires_at,
    }

def make_spotify_request(user, endpoint):
    """
    Makes an authenticated request to the Spotify API.
    Refreshes token if necessary.
    """
    try:
        token_obj = user.spotify_token
    except SpotifyToken.DoesNotExist:
        raise Exception("User has no Spotify token.")

    # Check if the token is expired and refresh if needed
    if token_obj.is_expired():
        token_resp = refresh_access_token(token_obj.refresh_token)
        fields = tokens_response_to_saved_fields(token_resp)
        # Update and save the token object
        token_obj.access_token = fields["access_token"]
        token_obj.expires_at = fields["expires_at"]
        token_obj.save()

    # Make the request to the Spotify API
    headers = {"Authorization": f"Bearer {token_obj.access_token}"}
    response = requests.get(f"{SPOTIFY_API_BASE_URL}{endpoint}", headers=headers)
    response.raise_for_status()
    return response.json()