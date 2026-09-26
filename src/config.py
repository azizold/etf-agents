"""Environment configuration. All secrets come from the process environment
(GitHub Actions injects them from repo secrets; locally, load a .env file)."""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


DATABASE_URL = _require("DATABASE_URL")
FMP_API_KEY = _require("FMP_API_KEY")
ANTHROPIC_API_KEY = _require("ANTHROPIC_API_KEY")

# Optional — only needed when posting/updating GitHub Issues (deck delivery)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "azizold/etf-agents")

# Claude model used for agent reasoning stages. Override via env if desired.
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")

# Sandbox parameters (Section 9 of the policy)
NOTIONAL_STARTING_CAPITAL = 20_000.00
