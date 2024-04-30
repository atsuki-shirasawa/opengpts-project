"""chatbot with slack-bolt"""

import json
import re
from logging import getLogger
from typing import Any, Optional

import functions_framework
from flask import Request, Response
from opengpts_client.client import OpenGPTsClient
from opengpts_client.schema import Message
from slack_bolt import App
from slack_bolt.adapter.google_cloud_functions import SlackRequestHandler
from slack_bolt.context.say import Say
from slack_sdk.models.blocks import (
    DividerBlock,
    MarkdownTextObject,
    SectionBlock,
)

from app.constants import (
    OPENGPTS_BOT_ID,
    OPENGPTS_URL,
    SLACK_BOT_TOKEN,
    SLACK_SIGNING_SECRET,
)

logger = getLogger(__name__)

# setting App
app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
    process_before_response=True,
)
handler = SlackRequestHandler(app)


def remove_mention(message: str) -> str:
    """メンションを削除したメッセージを取得

    Args:
        message (str): メンション有りメッセージ

    Returns:
        str: メンション削除後のメッセージ
    """
    return re.sub(r"^<.*>", "", message)


@app.event("app_mention")
def on_mention(event: dict[str, Any], say: Say) -> None:
    """botメンション時のチャット

    Args:
        event (dict[str, Any]): event request https://api.slack.com/events/app_mention
        say (Say): _description_
    """
    input_message: str = remove_mention(event["text"])
    thread_ts: Optional[str] = event.get("thread_ts")
    event_ts: str = event["ts"]
    channel: str = event["channel"]
    user_id: str = event["user"]

    opengpts_user_id = f"{channel}-{thread_ts or event_ts}"

    client = OpenGPTsClient(
        url=OPENGPTS_URL,
        opengpts_user_id=opengpts_user_id,
    )

    if thread_ts is None:
        thread = client.create_thread(
            name=input_message,
            assistant_id=OPENGPTS_BOT_ID,
        )
    else:
        thread = client.get_thread_list()[0]

    messages = client.run_and_get_messages(
        assistant_id=OPENGPTS_BOT_ID,
        thread_id=thread.thread_id,
        messages=[Message(type="human", content=input_message)],
    )
    response_text = messages[-1].content

    say(
        thread_ts=thread_ts or event_ts,
        channel=channel,
        mrkdwn=True,
        unfurl_links=True,
        blocks=[
            SectionBlock(
                text=MarkdownTextObject(
                    text=f"<@{user_id}>\n {response_text}",
                ),
            ),
            DividerBlock(),
        ],
    )


@functions_framework.http
def slack_bot(request: Request) -> Response:
    """Slack のイベントリクエストを受信して各処理を実行する関数

    Args:
        request: Slack のイベントリクエスト

    Returns:
        SlackRequestHandler への接続
    """
    header = request.headers
    body = request.get_json()

    # url_verification: https://api.slack.com/events/url_verification
    if body.get("type") == "url_verification":
        logger.info("url verification started")
        return Response(
            response=json.dumps({"challenge": body["challenge"]}),
            status=200,
            headers={"Content-Type": "application/json"},
        )
    # ignore slack retry request
    # https://api.slack.com/apis/connections/events-api#retries
    elif header.get("x-slack-retry-num"):
        logger.info("slack retry received")
        return Response(
            response=json.dumps({"message": "No need to resend"}),
            status=200,
        )
    # request to slack
    logger.info("exec slack bot")
    return handler.handle(request)
