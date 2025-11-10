# app/planner/planner_llm.py
import os, json
from typing import List, Dict, Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from openai import OpenAI
from app.models import Task
from app.planner.dag import DAG

load_dotenv()

# ----- Pydantic schemas for validation -----
class PlannedTask(BaseModel):
    id: str = Field(..., description="Unique id for the task")
    kind: str = Field(..., description="One of: book_flight, schedule_reminder, read_emails")
    payload: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list)

class PlanOutput(BaseModel):
    tasks: List[PlannedTask]

SYSTEM = (
    "You are a planning assistant. Convert the user's goal into a minimal set of tasks. "
    "Allowed kinds: book_flight, schedule_reminder, read_emails. "
    "Return ONLY a compact JSON object with this shape:\n"
    "{ \"tasks\": [ {\"id\":\"...\",\"kind\":\"book_flight|schedule_reminder|read_emails\","
    "\"payload\":{...},\"depends_on\":[\"...\"]} ] }"
)


def plan_with_gpt(goal: str, model: str = "gpt-4.1-mini") -> DAG:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing in .env")

    client = OpenAI(api_key=api_key)

    # ✅ LIMIT INPUT to approx. 120 tokens (400 chars) to control cost
    trimmed_system = SYSTEM[:400]
    trimmed_goal = goal[:400]

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": trimmed_system},
            {"role": "user", "content": trimmed_goal},
        ],
        response_format={"type": "json_object"},  # force JSON
        max_completion_tokens=120                # ✅ LIMIT OUTPUT tokens to 120
    )

    json_text = resp.choices[0].message.content  # JSON output here

    try:
        parsed = PlanOutput.model_validate_json(json_text)
    except ValidationError as e:
        raise RuntimeError(f"Planner JSON validation failed: {e}")

    dag = DAG()
    for t in parsed.tasks:
        dag.add(Task(id=t.id, kind=t.kind, payload=t.payload, depends_on=t.depends_on))
    return dag
