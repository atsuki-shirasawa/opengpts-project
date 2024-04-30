"""sample frontend app"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

import streamlit as st
from opengpts_client.client import OpenGPTsClient
from opengpts_client.schema import Assistant, Message
from streamlit_cookies_controller import CookieController
from streamlit_google_oauth.google_oauth import google_oauth2_required

from app.constants import OPENGPTS_URL, TARGET_ASSISTANT_IDS
from app.ui import set_page_layout


def get_opengpts_user_id() -> str:
    """cookieからOpenGPTs user idを取得

    Returns:
        str: OpenGPTs user id
    """
    cookie_manager = CookieController()
    user_id: Optional[str] = cookie_manager.get("opengpts_user_id")

    if st.session_state.get("init") is not None and user_id is None:
        user_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(days=1000)
        cookie_manager.set(
            cookie="opengpts_user_id",
            val=user_id,
            expires_at=expires_at,
        )
    return user_id


@st.cache_resource
def opengpt_client(url: str, opengpts_user_id: str) -> OpenGPTsClient:
    """OpenGPTs Client

    Returns:
        OpenGPTsClient: OpenGPTs Client
    """
    return OpenGPTsClient(url=url, opengpts_user_id=opengpts_user_id)


def get_assitants(
    _client: OpenGPTsClient,
    target_assistant_ids: Optional[list[str]] = None,
) -> list[Assistant]:
    """Get OpenGPTs Assistants

    Args:
        _client (OpenGPTsClient): OpenGPTs Client
        target_assistant_ids (Optional[list[str]], optional): \
            target assistant list. Defaults to None.

    Raises:
        ValueError: _description_

    Returns:
        list[Assistant]: _description_
    """
    if target_assistant_ids is None:
        assistant_list = _client.get_assistant_list()
    else:
        assistant_list = [
            _client.get_assistant(assistant_id=assistant_id)
            for assistant_id in target_assistant_ids
        ]

    if len(assistant_list) == 0:
        raise ValueError("target assistant does not exist")

    return assistant_list


def select_assistant(assistant_list: list[Assistant]) -> str:
    """Select Assistant

    Args:
        assistant_list (list[Assistant]): assitant list

    Returns:
        str: assistant id
    """
    st.sidebar.markdown("# 🤖 Bot")
    index = st.sidebar.selectbox(
        "assistant",
        range(len(assistant_list)),
        format_func=lambda x: assistant_list[x].name,
    )
    return assistant_list[index].assistant_id


def select_thread(
    client: OpenGPTsClient,
    assistant_id: str,
    current_thread_id: Optional[str] = None,
) -> Optional[str]:
    """Select thread by assistant id

    Args:
        client (OpenGPTsClient): OpenGPTs Client
        assistant_id (str): assistant id
        current_thread_id (str): current selected assistant id

    Returns:
        Optional[str]: thread id
    """
    st.sidebar.markdown("# 💬 Thread")
    thread_list = [
        thread
        for thread in client.get_thread_list()
        if thread.assistant_id == assistant_id
    ]
    thread_list = sorted(thread_list, key=lambda x: x.updated_at, reverse=True)

    hoge = 0
    if current_thread_id is not None:
        for idx, thread in enumerate(thread_list, start=1):
            if thread.thread_id == current_thread_id:
                hoge = idx

    thread_name_list = [thread.name[:15] for thread in thread_list]
    thread_name_list.insert(0, "New Chat")
    thread_update_list = [
        thread.updated_at.strftime("%Y/%m/%d %H:%M") for thread in thread_list
    ]
    thread_update_list.insert(0, "New Chat")

    index = st.sidebar.radio(
        "select chat",
        range(len(thread_name_list)),
        index=hoge,
        format_func=lambda x: thread_name_list[x],
        captions=thread_update_list,
        label_visibility="collapsed",
    )

    if index == 0:
        return None
    return thread_list[index - 1].thread_id


def display_thread_history(
    client: OpenGPTsClient,
    thread_id: Optional[str] = None,
) -> list[Message]:
    """Display thread message

    Args:
        client (OpenGPTsClient): OpenGPTs Client
        thread_id (str, optional): thread id. Defaults to None.

    Returns:
        list[Message]: _description_
    """
    if thread_id is None:
        return []

    message_list = client.get_messages(thread_id=thread_id).messages

    tools_message_list = []
    for msg in message_list:
        if msg.content == "":
            continue
        if msg.type in ["function", "tool"]:
            tools_message_list.append(msg)
        elif msg.type == "human":
            st.chat_message(msg.type).write(msg.content)
        elif msg.type == "ai":
            with st.chat_message(msg.type):
                st.write(msg.content)
                for tools_msg in tools_message_list:
                    display_function_or_tool_result(message=tools_msg)
            tools_message_list.clear()

    return message_list


def display_function_or_tool_result(message: Message) -> None:
    """Display function result

    Args:
        message (Message): message
    """
    label = message.name or message.additional_kwargs.name
    with st.expander(label):
        if isinstance(message.content, list):
            for content in message.content:
                source = (
                    content.metadata["source"] or content.page_content[:15]
                ).replace("\n", " ")
                with st.popover(label=f"📑 source: {source}"):
                    st.caption(f"{content.page_content}")
        else:
            source = message.content[:25]
            with st.popover(label=f"📑 source: {source}"):
                st.text(message.content)


@google_oauth2_required
def main() -> None:
    """Main"""
    set_page_layout()

    user_id = get_opengpts_user_id()
    if user_id is None:
        return

    if "thread_id" not in st.session_state:
        st.session_state["thread_id"] = None

    client = opengpt_client(url=OPENGPTS_URL, opengpts_user_id=user_id)

    assistant_list = get_assitants(client, TARGET_ASSISTANT_IDS)

    assistant_id = select_assistant(assistant_list)
    thread_id = select_thread(
        client,
        assistant_id,
        st.session_state["thread_id"],
    )

    message_list = display_thread_history(client=client, thread_id=thread_id)

    if prompt := st.chat_input():
        st.chat_message("user").write(prompt)

        if thread_id is None:
            thread_id = client.create_thread(
                name=prompt,
                assistant_id=assistant_id,
            ).thread_id
            st.session_state["thread_id"] = thread_id

        response = client.run_stream(
            assistant_id=assistant_id,
            thread_id=thread_id,
            messages=[Message(type="human", content=prompt)],
        )

        with st.chat_message("assistant"):
            message_placeholder = st.markdown("▌")
            full_response = ""

            for res in response:
                result: list[Message] = res[len(message_list) :]
                if result[-1].type != "ai":
                    continue
                full_response = result[-1].content
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)
            for res in result:
                if res.type in ["human", "ai"]:
                    continue
                display_function_or_tool_result(res)


if __name__ == "__main__":
    main()
