"""Gmail API authentication utilities."""

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from gmail_datalake_extractor.config import config


class AuthenticationError(Exception):
    """Raised when Gmail API authentication fails."""

    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message)
        self.original_error = original_error


def get_credentials() -> Credentials:
    """Get Gmail API credentials, refreshing if necessary.

    Returns:
        Credentials: Valid Gmail API credentials

    Raises:
        FileNotFoundError: If token file doesn't exist
        ValueError: If token is missing from credentials
        AuthenticationError: For authentication errors with helpful guidance
    """
    try:
        if not config.gmail_api.token_path.exists():
            raise FileNotFoundError(
                f"Token file not found at {config.gmail_api.token_path}"
            )
        creds = Credentials.from_authorized_user_file(
            str(config.gmail_api.token_path), config.gmail_api.scopes
        )
        if not creds.token:
            raise ValueError("Token not found in credentials")

        # Try to refresh if expired or if refresh is needed
        if creds.expired or not creds.valid:
            try:
                creds.refresh(Request())
                # Save refreshed token
                with config.gmail_api.token_path.open("w") as token:
                    token.write(creds.to_json())
            except RefreshError as e:
                error_msg = (
                    "Refresh token is invalid or expired. Re-authentication required.\n\n"
                    "This typically happens when:\n"
                    "  - The refresh token hasn't been used for 6+ months\n"
                    "  - The token was revoked in your Google Account settings\n"
                    "  - The OAuth client credentials changed\n\n"
                    "To fix this:\n"
                    "  1. Run: uv run gmail-auth\n"
                    "  2. If running in Docker, run the command on the host machine\n"
                    "  3. Ensure the new token.json is mounted/available at the configured path\n\n"
                    f"Token path: {config.gmail_api.token_path}"
                )
                raise AuthenticationError(error_msg, original_error=e) from e
    except FileNotFoundError:
        raise
    except ValueError:
        raise
    except AuthenticationError:
        raise
    except Exception as e:
        raise AuthenticationError(
            f"Unexpected error getting credentials: {e}",
            original_error=e,
        ) from e
    return creds


def get_service():
    """Get authenticated Gmail API service.

    Returns:
        Resource: Authenticated Gmail API service
    """
    creds = get_credentials()
    return build("gmail", "v1", credentials=creds)
