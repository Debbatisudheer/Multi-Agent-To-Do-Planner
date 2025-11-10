from pathlib import Path
import re
from app.models import Task, Result

FLIGHT_RE = re.compile(r"flight from (\w+) to (\w+) on (\d{4}-\d{2}-\d{2})", re.I)
REMIND_RE = re.compile(r"remind me at (\d{2}:\d{2})", re.I)

class EmailAgent:
    name = "email_agent"
    capability = "read_emails"

    def run(self, task: Task) -> Result:
        tasks: list[Task] = []
        for p in Path("data/emails").glob("*.txt"):
            text = p.read_text(encoding="utf-8")
            if m := FLIGHT_RE.search(text):
                origin, dest, date = m.groups()
                tasks.append(Task(id=f"t_{p.stem}_flight", kind="book_flight",
                                  payload={"origin": origin, "dest": dest, "date": date}))
            if m := REMIND_RE.search(text):
                time = m.group(1)
                tasks.append(Task(id=f"t_{p.stem}_reminder", kind="schedule_reminder",
                                  payload={"time": time, "note": "Email-derived reminder"}))
        return Result(task_id=task.id, status="ok",
                      data={"extracted_tasks": [t.model_dump() for t in tasks]})

agent = EmailAgent()
