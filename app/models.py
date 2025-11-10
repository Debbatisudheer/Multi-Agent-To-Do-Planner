from pydantic import BaseModel
from typing import Literal, Dict, Any, List, Optional

class Task(BaseModel):
    id: str
    kind: Literal["book_flight", "schedule_reminder", "read_emails"]
    payload: Dict[str, Any] = {}
    depends_on: List[str] = []

class Result(BaseModel):
    task_id: str
    status: Literal["ok", "error"]
    data: Dict[str, Any] = {}
    error: Optional[str] = None
