"""message"""

from typing import Literal

LOGIN_STYLE = (
    "<style>"
    ".login-style {"
    "    color: black;"
    "    font-size: 18px;"
    "    background-color: #DDEBFF;"
    "    padding: 20px;"
    "    border-radius: 10px;"
    "}"
    "</style>"
)


LOGIN_HTML = (
    "<p class='login-style'>Please login using this "
    "<a target='_self' href='{AUTHORIZATION_URL}'>url</a></p>"
)
RETRY_HTML = (
    "<p class='login-style'>This account is not allowed or page was refreshed. "
    "Please try again: "
    "<a target='_self' href='{AUTHORIZATION_URL}'>url</a></p>"
)
TOKEN_EXPIRED_HTML = (
    "<p class='login-style'>Login session has ended, "  # noqa: S105
    "please <a target='_self' href='{AUTHORIZATION_URL}'>login</a></p>"
)


def get_login_message(
    authorization_url: str,
    login_type: Literal["initial", "retry", "expired"],
) -> str:
    """ログインタイプに基づいてログインメッセージを生成

    Args:
        authorization_url (str): 認証ページへのURL。
        login_type (Literal["initial", "retry", "expired"]): \
            ログインのタイプ（初回、再試行、期限切れ）。

    Returns:
        str: ログインメッセージのHTML。
    """
    if login_type == "initial":
        html_template = LOGIN_HTML
    elif login_type == "retry":
        html_template = RETRY_HTML
    else:
        html_template = TOKEN_EXPIRED_HTML

    return LOGIN_STYLE + html_template.format(
        AUTHORIZATION_URL=authorization_url,
    )
