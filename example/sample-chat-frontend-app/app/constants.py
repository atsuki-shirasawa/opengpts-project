"""constants"""

import os

from dotenv import load_dotenv

load_dotenv()

OPENGPTS_URL = os.environ.get("OPENGPTS_URL", "http://localhost:8100")

# page layout
APP_PAGE_TITLE = os.environ.get("APP_PAGE_TITLE", "🤖💬 Sample ChatBot App")
APP_PAGE_ICON = os.environ.get("APP_PAGE_ICON", "🤖")
APP_SIDEBAR_LOGO = os.environ.get("APP_SIDEBAR_LOGO")

# target assistant id list
_target_assistant_ids = os.environ.get("TARGET_ASSISTANT_IDS")
TARGET_ASSISTANT_IDS = (
    None if _target_assistant_ids is None else _target_assistant_ids.split(",")
)
