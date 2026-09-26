"""Workflow B — Standing Position Monitoring.

Runs on its own schedule (see .github/workflows/workflow_b.yml), independent
of Workflow A. For every open position: re-score the thesis, check lockup
status, and — only for a state change, a structural-risk flag, or a cleared
exit — post a monitoring deck. Routine "still exceeding, nothing changed"
re-scores are logged but do not spam a deck every run.
"""
import argparse

from . import db, github_issues
from .agents import portfolio_fit, risk, synthesis, verification


def run_monitoring() -> None:
    open_positions = db.get_open_positions()

    for position in open_positions:
        result = risk.monitor(position)
        verdict = verification.verify_monitoring(position, result)
        if not verdict.get("passed"):
            # Do not act on an unverified re-score; log and move on. A human
            # can inspect agent_runs for the specific failure.
            continue

        state_changed = result["thesis_state"] != position["thesis_state"]
        db.update_thesis_state(position["id"], result["thesis_state"], notes=result.get("what_changed"))

        urgent = result.get("structural_risk_flag") or result["thesis_state"] == "broken"
        if not (state_changed or urgent):
            continue  # nothing deck-worthy this run

        eligible_exit_at = db.get_position_eligible_exit_at(position["id"])
        lockup_status = {
            "eligible_exit_at": str(eligible_exit_at) if eligible_exit_at else None,
            "cleared": bool(eligible_exit_at) and eligible_exit_at <= __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ),
        }

        deck_content = synthesis.assemble_monitoring(position, result, lockup_status)
        deck = db.create_deck(
            deck_type="monitoring", content=deck_content, fund_id=position["fund_id"],
            position_id=position["id"], confidence=deck_content.get("confidence"),
            recommended_action=result.get("recommended_action"), urgent=urgent,
        )

        title_prefix = "[URGENT]" if urgent else "[Monitoring]"
        issue = github_issues.create_deck_issue(
            title=f"{title_prefix} {position['ticker']}: thesis {result['thesis_state']}",
            body=deck_content.get("markdown", "(no markdown rendered)") + "\n\n---\n"
                 + "**To respond:** comment `CONFIRM`, `OVERRIDE: <what to do instead>`, "
                   "or `MORE INFO: <question>`.",
            labels=["monitoring-deck"] + (["urgent"] if urgent else []),
        )
        db.set_deck_github_issue(deck["id"], issue["number"], issue["url"])

    check_cleared_exits(open_positions)


def check_cleared_exits(open_positions: list[dict]) -> None:
    for cleared in portfolio_fit.check_lockups(open_positions):
        # Find the most recent monitoring deck for this position and flag it.
        with db.get_conn() as conn, db.dict_cursor(conn) as cur:
            cur.execute(
                """select * from decks where position_id = %s and deck_type = 'monitoring'
                   order by created_at desc limit 1""",
                (cleared["id"],),
            )
            deck = cur.fetchone()
        if deck and deck["github_issue_number"]:
            github_issues.comment_on_issue(
                deck["github_issue_number"],
                "Lockup has now cleared — this position is **cleared for exit**. "
                "Comment `CONFIRM` to proceed once you've executed the sale, or "
                "`OVERRIDE` to hold instead.",
            )


def process_responses() -> None:
    with db.get_conn() as conn, db.dict_cursor(conn) as cur:
        cur.execute(
            "select * from decks where deck_type = 'monitoring' and status in ('pending','more_info_requested')"
        )
        pending = cur.fetchall()

    import re
    decision_re = re.compile(r"^\s*(CONFIRM|OVERRIDE|MORE INFO)\s*:?\s*(.*)$", re.IGNORECASE | re.DOTALL)

    for deck in pending:
        if not deck["github_issue_number"]:
            continue
        for c in github_issues.get_new_comments(deck["github_issue_number"]):
            match = decision_re.match(c["body"].strip())
            if not match:
                continue
            raw_decision, notes = match.groups()
            decision_key = raw_decision.strip().lower().replace(" ", "_")
            db.record_decision(deck["id"], decision_key, notes)
            if decision_key == "confirm" and deck["recommended_action"] == "exit":
                db.close_position(deck["position_id"])
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["monitor", "responses"], default="monitor", nargs="?")
    args = parser.parse_args()
    if args.mode == "monitor":
        run_monitoring()
    else:
        process_responses()
