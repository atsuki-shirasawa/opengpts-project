"""Thread schema"""

from datetime import datetime

from pydantic import BaseModel, Field

from opengpts_client.schema import Message


class ThreadMessages(BaseModel):
    """Thread Message list"""

    messages: list[Message] = Field(..., title="message list")
    resumeable: bool = Field(..., title="resumeable")


class Thread(BaseModel):
    """Thread Info"""

    thread_id: str = Field(..., title="thread id")
    user_id: str = Field(..., title="user id")
    assistant_id: str = Field(..., title="assistant id")
    name: str = Field(..., title="thread name")
    updated_at: datetime = Field(..., title="update timestamp")


class ThreadConfigurable:
    """Thread Config"""

    thread_id: str = Field(..., title="thread id")
    thread_ts: datetime = Field(..., title="thread timestamp")


class ThreadConfig:
    """Thread Config"""

    configurable: ThreadConfigurable = Field(..., title="configurable")


class ThreadHistory(BaseModel):
    """Thread History"""

    values: list[Message] = Field(..., title="message list")
    resumeable: bool = Field(..., title="resumeable")
    # config: ThreadConfig
