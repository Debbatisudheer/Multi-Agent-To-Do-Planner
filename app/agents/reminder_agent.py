from app.models import Task, Result

class ReminderAgent:
    name = "reminder_agent"
    capability = "schedule_reminder"
    _reminders: list[dict] = []

    def run(self, task: Task) -> Result:
        self._reminders.append(task.payload)
        return Result(task_id=task.id, status="ok", data={"scheduled": task.payload})

agent = ReminderAgent()
