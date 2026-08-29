import json
from datetime import datetime, timezone

from app.agents.attacker import generate_attack, ATTACK_CATEGORIES
from app.agents.target import query_target, DEFAULT_TARGET_SYSTEM_PROMPT
from app.agents.judge import judge_attack
from app.agents.patcher import patch_prompt
 from app.agents.target import WEAK_TARGET_SYSTEM_PROMPT

def run_red_team_session(attempts_per_category: int = 1):
    """
    Run the full Warden loop: generate attacks, fire them at the target,
    judge success, and for any successful attack, patch the target's
    system prompt and re-test the same attack to verify the fix.
    """
    results = []
    current_system_prompt = WEAK_TARGET_SYSTEM_PROMPT
    patches_applied = 0

    for category in ATTACK_CATEGORIES:
        for _ in range(attempts_per_category):
            attack = generate_attack(category)
            target_response = query_target(attack, system_prompt=current_system_prompt)
            verdict = judge_attack(attack, target_response)

            entry = {
                "category": category,
                "attack": attack,
                "target_response": target_response,
                "initial_verdict": verdict,
                "patched": False,
                "post_patch_verdict": None,
            }

            if verdict == "BROKEN":
                new_prompt = patch_prompt(current_system_prompt, attack)
                retest_response = query_target(attack, system_prompt=new_prompt)
                retest_verdict = judge_attack(attack, retest_response)

                entry["patched"] = True
                entry["post_patch_verdict"] = retest_verdict

                if retest_verdict == "SAFE":
                    current_system_prompt = new_prompt
                    patches_applied += 1

            results.append(entry)

    total = len(results)
    initially_broken = sum(1 for r in results if r["initial_verdict"] == "BROKEN")
    patches_successful = sum(1 for r in results if r["post_patch_verdict"] == "SAFE")

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_attacks": total,
        "initial_attack_success_rate": initially_broken / total if total else 0,
        "patches_applied": patches_applied,
        "patches_successful": patches_successful,
        "final_system_prompt": current_system_prompt,
        "results": results,
    }

    return summary


if __name__ == "__main__":
    summary = run_red_team_session(attempts_per_category=1)

    print(f"\n=== Warden Red-Team Session ===\n")
    print(f"Total attacks: {summary['total_attacks']}")
    print(f"Initial attack success rate: {summary['initial_attack_success_rate']:.0%}")
    print(f"Patches applied: {summary['patches_applied']}")
    print(f"Patches successful (verified safe on re-test): {summary['patches_successful']}\n")

    for r in summary["results"]:
        print(f"--- Category: {r['category']} ---")
        print(f"Initial verdict: {r['initial_verdict']}")
        if r["patched"]:
            print(f"Patched -> re-tested: {r['post_patch_verdict']}")
        print()

    with open("last_session.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("Full results saved to last_session.json")