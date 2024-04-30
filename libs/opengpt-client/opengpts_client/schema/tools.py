"""Tools schema"""

from typing import Optional

from pydantic import BaseModel, Field


class PropertySchema(BaseModel):
    """property"""

    type: str = Field(..., title="property name")
    title: Optional[str] = Field(None, title="property title")
    description: Optional[str] = Field(None, title="property description")


class ToolConfigSchema(BaseModel):
    title: str
    type: str
    required: list[str]
    properties: dict[str, PropertySchema]


class SchemaItemProperties(BaseModel):
    name: str
    type: str
    description: str
    config: ToolConfigSchema
    multi_use: bool


class SchemaItem(BaseModel):
    properties: SchemaItemProperties


class AgentTools(BaseModel):
    items: list[SchemaItem] = Field(..., alias="type==agent/tools")


class Configurable(BaseModel):
    properties: AgentTools


class ConfigSchemaProperties(BaseModel):
    configurable: Configurable


class ConfigSchema(BaseModel):
    properties: ConfigSchemaProperties


hoge = {
    "name": "sample-rag-2",
    "config": {
        "configurable": {
            "type": "agent",
            "type==agent/agent_type": "GPT 4 (Azure OpenAI)",
            "type==agent/interrupt_before_action": False,
            "type==agent/retrieval_description": "Can be used to look up information that was uploaded to this assistant.\nIf the user is referencing particular files, that is often a good hint that information may be here.\nIf the user asks a vague question, they are likely meaning to look up info from this retriever, and you should call it!",
            "type==agent/system_message": "You are a helpful assistant.",
            "type==agent/tools": [
                {
                    "id": "retrieval",
                    "type": "retrieval",
                    "name": "Retrieval",
                    "description": "Look up information in uploaded files.",
                    "config": {},
                },
                {
                    "id": "81018e81-da23-4460-ad74-79a4798c562f",
                    "type": "wikipedia",
                    "name": "Wikipedia",
                    "description": "Searches [Wikipedia](https://pypi.org/project/wikipedia/).",
                    "config": {},
                },
            ],
            "type==chat_retrieval/llm_type": "GPT 3.5 Turbo",
            "type==chat_retrieval/system_message": "You are a helpful assistant.",
            "type==chatbot/llm_type": "GPT 3.5 Turbo",
            "type==chatbot/system_message": "You are a helpful assistant.",
        },
    },
    "public": False,
}
