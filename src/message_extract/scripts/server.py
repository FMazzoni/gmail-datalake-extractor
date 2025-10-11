#!/usr/bin/env python3
"""Server script for running the FastAPI application."""

import uvicorn


def main() -> None:
    """Main function to run the FastAPI server."""
    uvicorn.run(
        "message_extract.api:app",  # Use import string for reload support
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
    )


if __name__ == "__main__":
    main()
