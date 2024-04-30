"""assistant"""

from datetime import datetime

from pydantic import BaseModel, Field


class Assistant(BaseModel):
    """Asistant"""

    assistant_id: str = Field(..., title="assistant id")
    user_id: str = Field(..., title="user id")
    name: str = Field(..., title="assistant name")
    config: dict = Field(..., title="config")
    updated_at: datetime = Field(..., title="update timestamp")
    public: bool = Field(..., title="is public")
