from .. import db
from .base import call_stage

# How long a rejected theme stays "recently screened out" and gets skipped
# rather than fully re-researched. Long enough to stop paying for the same
# already-priced-in-theme research on every discovery run (11x/week);
# short enough that a theme with a genuinely fresh trigger can resurface —
# the doc still tells the agent it CAN re-propose one if something
# materially new justifies a second look.
SCREENED_OUT_COOLDOWN_DAYS = 14


def discover(discovery_source: str) -> dict:
    open_positions = db.get_open_positions()
    recent_screened_out = db.get_recent_screened_out_themes(days=SCREENED_OUT_COOLDOWN_DAYS)
    input_data = {
        "current_open_themes": [
            {"ticker": p["ticker"], "fund_name": p["fund_name"]} for p in open_positions
        ],
        "recently_screened_out_themes": [
            {
                "theme_name": t["name"], "reason": t["screened_out_reason"],
                "screened_out_at": str(t["discovered_at"]),
            }
            for t in recent_screened_out
        ],
    }
    result = call_stage(
        workflow="A", agent_name="theme_discovery", doc_filename="01_theme_discovery.md",
        input_data=input_data, use_web_search=True, max_tokens=16000,
    )
    parsed = result["parsed"]
    saved = []
    for c in parsed.get("candidates", []):
        theme = db.insert_theme(
            name=c["theme_name"], description=c["description"],
            convergence=c.get("convergence"), why_now=c.get("why_now"),
            discovery_source=discovery_source,
        )
        saved.append({**c, "theme_id": theme["id"]})

    screened_out = parsed.get("screened_out", [])
    for s in screened_out:
        db.insert_screened_out_theme(
            name=s["theme_name"], reason=s.get("reason", ""), discovery_source=discovery_source,
        )

    return {"candidates": saved, "screened_out": screened_out, "citations": result["citations"]}
