from app.models import Task
from app.planner.dag import DAG
import re

TIME_RE = re.compile(r"\b([01]?\d|2[0-3]):([0-5]\d)\b")  # HH:MM 00-23

def plan(goal: str) -> DAG:
    g = goal.lower()
    dag = DAG()

    if "email" in g:
        dag.add(Task(id="read_emails", kind="read_emails"))

    if "flight" in g:
        dag.add(Task(id="book_flight", kind="book_flight"))

    if "remind" in g or "reminder" in g:
        payload = {}
        m = TIME_RE.search(g)
        if m:
            payload["time"] = m.group(0)
        dag.add(Task(id="reminder", kind="schedule_reminder", payload=payload))

    if len(dag.g.nodes) == 0:
        dag.add(Task(id="read_emails", kind="read_emails"))

    return dag
