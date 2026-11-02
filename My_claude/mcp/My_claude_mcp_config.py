
import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

_CONFIG_PATH = Path(__file__).parent.parent / "My_claude_mcp_servers.json"


def load_My_claude_mcp_configs() -> dict:
    """Load MCP server configuration and resolve environment variables."""

    os.environ.setdefault("CWD", str(Path.cwd()))

    raw = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))

    def resolve(value):
        if isinstance(value, dict):
            return {key: resolve(item) for key, item in value.items()}

        if isinstance(value, list):
            return [resolve(item) for item in value]

        if isinstance(value, str):
            return re.sub(
                r"\$\{(\w+)\}",
                lambda match: os.getenv(match.group(1), ""),
                value,
            )

        return value

    return resolve(raw).get("mcp_servers", {})
 