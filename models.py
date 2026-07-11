from __future__ import annotations
from typing import Any, Literal, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class Task(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True)
    task_id: UUID
    task_type: str
    payload: dict[str, Any]
    priority: int = Field(default=1)

class AgentResponse(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True)
    agent_name: str
    status: Literal["success", "failed"]
    result: dict[str, Any]
    metadata: Optional[dict[str, Any]] = Field(default=None)
