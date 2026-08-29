import json
from datetime import datetime

from app.agents.attacker import generate_attack, ATTACK_CATEGORIES
from app.agents.target import query_target
from app.agents.judge import judge_attack


def run_red_team_session(attempts_per_category: int = 1):
    """
    Run the full Warden red-teaming loop: generate attacks across categories,
    fire them at the target, judge whether each attack broke the target,
    and return a structured results log.
    """
    results = []

    for category in ATTACK_CATEGORIES:
        for _ in range(attempts_per_category):
            attack = generate_attack(category)
            target_response = query_target(attack)
            verdict = judge_attack(attack, target_response)

            results.append({
                "category": category,
                "attack": attack,
                "target_response": target_response,
                "verdict": verdict,
            })

    total = len(results)
    broken = sum(1 for r in results if r["verdict"] == "BROKEN")
    success_rate = broken / total if total else 0

    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_attacks": total,
        "successful_attacks": broken,
        "attack_success_rate": success_rate,
        "results": results,
    }

    return summary


if __name__ == "__main__":
    summary = run_red_team_session(attempts_per_category=1)

    print(f"\n=== Warden Red-Team Session ===\n")
    print(f"Total attacks: {summary['total_attacks']}")
    print(f"Successful (target broken): {summary['successful_attacks']}")
    print(f"Attack success rate: {summary['attack_success_rate']:.0%}\n")

    for r in summary["results"]:
        print(f"--- Category: {r['category']} ---")
        print(f"Attack: {r['attack'][:150]}...")
        print(f"Verdict: {r['verdict']}\n")

    with open("last_session.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("Full results saved to last_session.json")