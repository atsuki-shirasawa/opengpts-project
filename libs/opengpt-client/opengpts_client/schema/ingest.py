from datetime import datetime
from typing import Any, Optional, Union

from pydantic import BaseModel


class IngestConfig(BaseModel):
    namespace: str
    chunk_size: int = 1000
    chunk_overlap: int = 200
    separators: Optional[list[str]] = None


class IngestConfig(BaseModel):
    configurable: IngestConfig
