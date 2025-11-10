import csv
from pathlib import Path
from app.models import Task, Result

class FlightAgent:
    name = "flight_agent"
    capability = "book_flight"

    def run(self, task: Task) -> Result:
        q = task.payload
        matches = []
        with open(Path("data") / "flights.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if ((not q.get("origin") or row["origin"] == q["origin"]) and
                    (not q.get("dest") or row["dest"] == q["dest"]) and
                    (not q.get("date") or row["date"] == q["date"])):
                    matches.append(row)
        if not matches:
            return Result(task_id=task.id, status="error", error="No flights found")
        best = sorted(matches, key=lambda r: int(r["price"]))[0]
        return Result(task_id=task.id, status="ok",
                      data={"itinerary": best, "alternatives": matches})

agent = FlightAgent()
