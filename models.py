from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, JSON, Column

class Task(SQLModel, table=True):
    task_id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, nullable=False)
    task_type: str
    payload: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    priority: int = 1
    status: str = "pending"  # pending, processing, completed, failed
    result: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    agent_assigned: Optional[str] = None
