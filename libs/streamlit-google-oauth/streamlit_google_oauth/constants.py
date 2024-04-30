"""constants"""

import os
from pathlib import Path

from dotenv import load_dotenv

env_filepath = Path.cwd().joinpath(".env")
if env_filepath.exists():
    load_dotenv(env_filepath)
else:
    load_dotenv()

# app environment
ENVIRONMENT = os.getenv("ENV", "dev")

# Google OAuth2 setting
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI")
