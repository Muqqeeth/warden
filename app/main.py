from fastapi import FastAPI
from app.orchestrator import run_red_team_session

app = FastAPI(title="Warden", description="Self-red-teaming agent security tester")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/red-team")
def red_team(attempts_per_category: int = 1):
    """
    Run a full red-teaming session: generate attacks, fire them at the
    target agent, judge success, and return the results summary.
    """
    return run_red_team_session(attempts_per_category=attempts_per_category)