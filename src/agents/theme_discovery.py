from .. import db
from .base import call_stage


def discover(discovery_source: str) -> dict:
    open_positions = db.get_open_positions()
    input_data = {
        "current_open_themes": [
            {"ticker": p["ticker"], "fund_name": p["fund_name"]} for p in open_positions
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
    return {"candidates": saved, "screened_out": parsed.get("screened_out", []),
            "citations": result["citations"]}
