"""Gmail API authentication utilities."""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from message_extract.config import config


def get_credentials() -> Credentials:
    """Get Gmail API credentials, refreshing if necessary.

    Returns:
        Credentials: Valid Gmail API credentials

    Raises:
        FileNotFoundError: If token file doesn't exist
        ValueError: If token is missing from credentials
        Exception: For other authentication errors
    """
    try:
        if not config.token_path.exists():
            raise FileNotFoundError(f"Token file not found at {config.token_path}")
        creds = Credentials.from_authorized_user_file(
            str(config.token_path), config.scopes
        )
        if not creds.token:
            raise ValueError("Token not found in credentials")
        if creds.expired:
            creds.refresh(Request())
            with config.token_path.open("w") as token:
                _ = token.write(creds.to_json())
    except Exception as e:
        raise Exception(f"Error getting credentials: {e}")
    return creds


def get_service():
    """Get authenticated Gmail API service.

    Returns:
        Resource: Authenticated Gmail API service
    """
    creds = get_credentials()
    return build("gmail", "v1", credentials=creds)
