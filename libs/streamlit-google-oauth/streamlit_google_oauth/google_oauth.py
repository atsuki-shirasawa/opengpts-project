"""google oauth"""

# 参考 https://github.com/yagays/streamlit-google-oauth/blob/main/streamlit_google_oauth.py
import asyncio
from typing import Any, Callable, Optional, Union

import streamlit as st
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.oauth2 import OAuth2Token

from streamlit_google_oauth.constants import (
    ENVIRONMENT,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    REDIRECT_URI,
)
from streamlit_google_oauth.message import get_login_message


def verify_oauth2_setting() -> tuple[str, str, str]:
    """Googke Oauth2 設定値チェック

    Raises:
        ValueError: 値が設定されていない場合、エラー

    Returns:
        tuple[str, str, str]: client_id, client_secret, redirect_uri
    """
    client_id = GOOGLE_CLIENT_ID
    client_secret = GOOGLE_CLIENT_SECRET
    redirect_uri = REDIRECT_URI

    if client_id is None or client_secret is None or redirect_uri is None:
        raise ValueError("google oauth2 setting error")

    return client_id, client_secret, redirect_uri


async def write_authorization_url(
    client: GoogleOAuth2,
    redirect_uri: str,
) -> str:
    """Authorization URL取得

    Args:
        client (GoogleOAuth2): _description_
        redirect_uri (str): _description_

    Returns:
        str: _description_
    """
    authorization_url = await client.get_authorization_url(
        redirect_uri,
        scope=["profile", "email"],
        extras_params={"access_type": "offline"},
    )
    return authorization_url


async def write_access_token(
    client: GoogleOAuth2,
    redirect_uri: str,
    code: str,
) -> Union[OAuth2Token, Any]:
    """アクセストークン取得

    Args:
        client (GoogleOAuth2): GoogleOAuth2 クライアント
        redirect_uri (str): リダイレクト URI
        code (str): _description_

    Returns:
        Union[OAuth2Token, Any]: アクセストークン
    """
    token = await client.get_access_token(code, redirect_uri)
    return token


async def get_email(
    client: GoogleOAuth2,
    token: str,
) -> tuple[str, Optional[str]]:
    """_summary_

    Args:
        client (GoogleOAuth2): GoogleOAuth2 クライアント
        token (str): トークン

    Returns:
        tuple[str, Optional[str]]: ユーザーID、メールアドレス
    """
    user_id, user_email = await client.get_id_email(token)
    return user_id, user_email


def google_oauth2_required(func: Callable) -> Callable:
    """Google OAuth2.0認証デコーダー

    Args:
        func (Callable): 関数
    """

    def wrapper(*args: Any, **kwargs: Any) -> None:
        """デコーダー"""
        # skip authorization if local environment variables are not set
        if ENVIRONMENT == "local":
            func(*args, **kwargs)
            return

        client_id, client_secret, redirect_uri = verify_oauth2_setting()

        client = GoogleOAuth2(client_id, client_secret)
        authorization_url = asyncio.run(
            write_authorization_url(client=client, redirect_uri=redirect_uri),
        )

        if "token" not in st.session_state:
            st.session_state.token = None

        if st.session_state.token is None:
            try:
                code = st.query_params["code"]
            except Exception:
                login_message = get_login_message(
                    authorization_url,
                    login_type="initial",
                )
                st.markdown(login_message, unsafe_allow_html=True)
            else:
                # Verify token is correct:
                try:
                    token = asyncio.run(
                        write_access_token(
                            client=client,
                            redirect_uri=redirect_uri,
                            code=code,
                        ),
                    )
                except Exception:
                    retry_ms = get_login_message(
                        authorization_url,
                        login_type="retry",
                    )
                    st.markdown(retry_ms, unsafe_allow_html=True)
                else:
                    # Check if token has expired:
                    if token.is_expired():
                        st.markdown(
                            get_login_message(
                                authorization_url,
                                login_type="expired",
                            ),
                            unsafe_allow_html=True,
                        )
                    else:
                        st.session_state["token"] = token
                        user_id, user_email = asyncio.run(
                            get_email(
                                client=client,
                                token=token["access_token"],
                            ),
                        )
                        st.session_state.user_id = user_id
                        st.session_state.user_email = user_email
                        func(*args, **kwargs)
        else:
            func(*args, **kwargs)

    return wrapper
