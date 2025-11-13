"""Helper script to generate Gmail API OAuth tokens."""

import json
import sys
from pathlib import Path
from typing import Any

from google_auth_oauthlib.flow import InstalledAppFlow

from gmail_datalake_extractor.config import config

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def extract_client_config_from_token(token_path: Path) -> dict[str, Any] | None:
    """Extract client_id and client_secret from existing token file.

    Args:
        token_path: Path to the token.json file

    Returns:
        Dictionary with client config if found, None otherwise
    """
    try:
        with token_path.open() as f:
            token_data = json.load(f)

        if "client_id" in token_data and "client_secret" in token_data:
            return {
                "installed": {
                    "client_id": token_data["client_id"],
                    "client_secret": token_data["client_secret"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "redirect_uris": ["http://localhost"],
                }
            }
    except Exception:
        pass
    return None


def generate_token(
    token_path: Path | None = None,
    credentials_path: Path | None = None,
) -> None:
    """Generate a new OAuth token for Gmail API access.

    Args:
        token_path: Path where to save the token (defaults to config value)
        credentials_path: Path to credentials.json file (optional if client info in token)
    """
    # Use configured token path if not provided
    if token_path is None:
        token_path = config.gmail_api.token_path
    if credentials_path is None:
        credentials_path = token_path.parent / "credentials.json"
    # Try to get client config from existing token or credentials file
    client_config = None

    if credentials_path and credentials_path.exists():
        print(f"Loading credentials from {credentials_path}")
        with credentials_path.open() as f:
            client_config = json.load(f)
    elif token_path.exists():
        print(
            f"Attempting to extract client config from existing token at {token_path}"
        )
        client_config = extract_client_config_from_token(token_path)

    if not client_config:
        print("ERROR: Could not find client credentials.")
        print("\nYou need to provide OAuth 2.0 client credentials.")
        print("Options:")
        print("  1. Download credentials.json from Google Cloud Console")
        print(
            "  2. Or ensure your existing token.json contains client_id and client_secret"
        )
        print("\nTo download credentials.json:")
        print("  1. Go to https://console.cloud.google.com/")
        print("  2. Select your project")
        print("  3. Go to APIs & Services > Credentials")
        print("  4. Create OAuth 2.0 Client ID (Desktop app)")
        print("  5. Download the JSON file")
        sys.exit(1)

    # Backup existing token if it exists
    if token_path.exists():
        backup_path = token_path.with_suffix(".json.backup")
        print(f"Backing up existing token to {backup_path}")
        token_path.rename(backup_path)

    # Run OAuth flow
    print("\nStarting OAuth flow...")
    print("A browser window will open. Please authorize the application.")
    print(f"Requested scopes: {', '.join(SCOPES)}\n")

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0)

    # Save token
    token_path.parent.mkdir(parents=True, exist_ok=True)
    with token_path.open("w") as token_file:
        token_file.write(creds.to_json())

    print(f"\n✓ Token successfully saved to {token_path}")
    print("You can now use the Gmail API with this token.")


def main() -> None:
    """Main entry point for the auth helper script."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate Gmail API OAuth token")
    parser.add_argument(
        "--token-path",
        type=Path,
        help="Path to save the token (defaults to configured path)",
    )
    parser.add_argument(
        "--credentials",
        type=Path,
        help="Path to credentials.json file from Google Cloud Console",
    )

    args = parser.parse_args()

    try:
        generate_token(
            token_path=args.token_path,
            credentials_path=args.credentials,
        )
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
