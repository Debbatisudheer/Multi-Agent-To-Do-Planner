from app.models import Task, Result
from app.registry import register, get_agent
from app.agents.flight_agent import agent as flight_agent
from app.agents.reminder_agent import agent as reminder_agent
from app.agents.email_agent import agent as email_agent
from app.planner.dag import DAG, Executor

# Register agents
register(flight_agent)
register(reminder_agent)
register(email_agent)

def dispatch(task: Task) -> Result:
    agent = get_agent(task.kind)
    return agent.run(task)

executor = Executor(dispatch)

def expand_runtime_tasks(results: dict[str, Result], dag: DAG):
    res = results.get("read_emails")
    if res and res.status == "ok":
        for t in res.data.get("extracted_tasks", []):
            task = Task(**t)
            if task.id not in dag.g:
                dag.add(task)
