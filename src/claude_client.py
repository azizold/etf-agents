"""Wrapper around the Anthropic Messages API used by every agent stage.

Two things every agent needs, provided here once:
1. Optional server-side web search, so research stages (Theme Discovery,
   Composition, Valuation, Risk) can ground claims in real, citable sources —
   directly serving Section 1's "every stated fact must be sourced" rule.
2. Structured JSON output, since each stage hands a specific schema to the
   next stage rather than free text.
"""
import json
import re

import anthropic

from . import config

# A generous but bounded per-call timeout — a web-search-enabled call can
# legitimately take a while, but should never hang indefinitely. The job-level
# timeout-minutes in the workflow YAML is the outer safety net on top of this.
_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY, timeout=180.0)

WEB_SEARCH_TOOL = {"type": "web_search_20250305", "name": "web_search", "max_uses": 8}


def _extract_json(text: str) -> dict:
    """Pulls the first {...} or [...] block out of a model response."""
    match = re.search(r"\{.*\}|\[.*\]", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in model output:\n{text[:2000]}")
    # strict=False allows literal control characters (e.g. newlines) inside
    # string values, which models frequently emit despite instructions.
    return json.loads(match.group(0), strict=False)


def run_agent(system_prompt: str, user_content: str, use_web_search: bool = False,
              max_tokens: int = 4096) -> dict:
    """Sends one agent-stage request and returns parsed JSON plus any web
    citations Claude used, so callers can pass those citations straight into
    `sources` records (Section 1 / Verification Agent)."""
    kwargs = dict(
        model=config.CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    if use_web_search:
        kwargs["tools"] = [WEB_SEARCH_TOOL]

    response = _client.messages.create(**kwargs)

    text_parts = []
    citations = []
    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)
            for c in getattr(block, "citations", None) or []:
                citations.append({
                    "url": getattr(c, "url", None),
                    "title": getattr(c, "title", None),
                    "cited_text": getattr(c, "cited_text", None),
                })

    full_text = "\n".join(text_parts)
    try:
        parsed = _extract_json(full_text)
        if not parsed:  # valid JSON but empty ({} or []) — e.g. truncated by max_tokens
            raise ValueError("Parsed JSON was empty — likely truncated output")
    except (ValueError, json.JSONDecodeError) as exc:
        # One repair attempt: re-run the *original* request with more headroom
        # rather than asking the model to "fix" already-truncated output —
        # there's nothing to fix if the real content never got generated.
        retry_kwargs = dict(kwargs)
        retry_kwargs["max_tokens"] = max_tokens * 2
        retry = _client.messages.create(**retry_kwargs)
        retry_text = "\n".join(b.text for b in retry.content if b.type == "text")
        parsed = _extract_json(retry_text)
        if not parsed:
            raise ValueError(f"Still empty after retry with {max_tokens * 2} max_tokens "
                              f"(original error: {exc})")
        full_text = retry_text
        for block in retry.content:
            if block.type == "text":
                for c in getattr(block, "citations", None) or []:
                    citations.append({
                        "url": getattr(c, "url", None), "title": getattr(c, "title", None),
                        "cited_text": getattr(c, "cited_text", None),
                    })

    return {"parsed": parsed, "citations": citations, "raw_text": full_text}
