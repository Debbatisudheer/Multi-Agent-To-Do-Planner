# main.py
from app.agentic_planner import run_agent

if __name__ == "__main__":
    goal = input("Enter your goal: ")
    result = run_agent(goal)
    print("\nFINAL RESULT:\n", result)
