#!/usr/bin/env python3
"""Server script for running the FastAPI application."""

import uvicorn

from message_extract.config import config


def main() -> None:
    """Main function to run the FastAPI server."""
    uvicorn.run(
        "message_extract.api:app",  # Use import string for reload support
        host=config.server.host,
        port=config.server.port,
        reload=config.server.reload,  # Enable auto-reload for development
        log_level=config.server.log_level.lower(),
    )


if __name__ == "__main__":
    main()
