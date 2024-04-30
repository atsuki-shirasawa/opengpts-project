"""message"""

from typing import Any, Optional, Union

from pydantic import BaseModel, Field


class FunctionCall(BaseModel):
    """FunctionCall"""

    name: Optional[str] = Field(None, title="function name")
    arguments: Optional[str] = Field(None, title="function argument")


class ToolCall(BaseModel):
    """Tool Call"""

    function: Optional[FunctionCall] = Field(None, title="function call")


class AdditionalKwargs(BaseModel):
    """Additional Kwargs"""

    name: Optional[str] = Field(None, title="additional kwarg name")
    function_call: Optional[FunctionCall] = Field(None, title="function call")
    tool_calls: Optional[list[ToolCall]] = Field(None, title="tools call")


class PageContent(BaseModel):
    """Page Content"""

    page_content: str = Field(..., title="document content")
    metadata: dict[str, Any] = Field(..., title="document metadata")


class Message(BaseModel):
    """Message"""

    type: str = Field(..., title="message content")
    content: Union[str, list[PageContent], dict] = Field(
        ...,
        title="message content",
    )
    id: Optional[str] = Field(None, title="message id")
    name: Optional[str] = Field(None, title="message name")
    example: Optional[bool] = Field(None, title="is example")
    additional_kwargs: Optional[AdditionalKwargs] = Field(
        None,
        title="additional kwargs",
    )

    def to_request_params(self) -> dict[str, Any]:
        """Convert API request params

        Returns:
            dict[str, Any]: request params
        """
        return {
            "type": self.type,
            "content": self.content,
            "additional_kwargs": (
                {}
                if self.additional_kwargs is None
                else self.additional_kwargs.model_dump()
            ),
            "example": self.example or False,
        }
