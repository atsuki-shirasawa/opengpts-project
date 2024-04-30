"""constants"""

import os

from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
"""aaa"""

SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
"""aaa"""

OPENGPTS_BOT_ID = os.environ["OPENGPTS_BOT_ID"]
"""BOT ID created by OpenGPTs"""

OPENGPTS_URL = os.environ.get("OPENGPTS_URL", "http://localhost:8100")
"""OpenGPTs URL"""
