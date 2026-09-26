"""Shared helper: load an agent's instruction doc, call Claude, log the run."""
import json
import pathlib

from .. import db
from ..claude_client import run_agent

DOCS_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "agents"

_DOC_CACHE: dict[str, str] = {}


def _load_doc(filename: str) -> str:
    if filename not in _DOC_CACHE:
        _DOC_CACHE[filename] = (DOCS_DIR / filename).read_text()
    return _DOC_CACHE[filename]


def call_stage(*, workflow: str, agent_name: str, doc_filename: str,
                input_data: dict, use_web_search: bool = False,
                theme_id=None, fund_id=None, position_id=None, deck_id=None,
                max_tokens: int = 4096) -> dict:
    """Runs one pipeline stage end to end: builds the prompt from the agent's
    doc + input data, calls Claude, logs the run, and returns the parsed
    output. Raises on failure after logging it."""
    system_prompt = _load_doc(doc_filename)
    user_content = (
        "Input data for this stage (JSON):\n\n" + json.dumps(input_data, indent=2, default=str)
    )

    run_id = db.start_agent_run(
        workflow=workflow, agent_name=agent_name, theme_id=theme_id,
        fund_id=fund_id, position_id=position_id, deck_id=deck_id,
        input_summary=input_data,
    )
    try:
        result = run_agent(system_prompt, user_content, use_web_search=use_web_search,
                            max_tokens=max_tokens)
        db.finish_agent_run(run_id, "ok", output_summary=result["parsed"])
        result["run_id"] = run_id
        return result
    except Exception as exc:
        db.finish_agent_run(run_id, "failed", error=str(exc))
        raise
