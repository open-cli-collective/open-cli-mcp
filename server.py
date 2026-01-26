#!/usr/bin/env python3
"""
Open CLI MCP Server

Exposes CLI tools from the open-cli-collective as MCP tools for Claude Code.
Provides both convenience wrappers for common operations and generic access
to full CLI functionality.
"""

import json
import logging
import subprocess
from typing import Optional

from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("open-cli-mcp")

# CLI configuration - only open-cli-collective tools
# All tools installed via: brew install --cask open-cli-collective/tap/<name>
CLI_CONFIG = {
    "jira-ticket-cli": {
        "path": "jira-ticket-cli",
        "version_cmd": ["--version"],
        "json_flag": "--output json",
        "source": "cask",
        "cask": "open-cli-collective/tap/jira-ticket-cli",
    },
    "slck": {
        "path": "slck",
        "version_cmd": ["--version"],
        "json_flag": "--output json",
        "source": "cask",
        "cask": "open-cli-collective/tap/slack-chat-cli",
    },
    "cfl": {
        "path": "cfl",
        "version_cmd": ["--version"],
        "json_flag": "--output json",
        "source": "cask",
        "cask": "open-cli-collective/tap/cfl",
    },
    "newrelic-cli": {
        "path": "newrelic-cli",
        "version_cmd": ["--version"],
        "json_flag": "--output json",
        "source": "cask",
        "cask": "open-cli-collective/tap/newrelic-cli",
    },
    "gro": {
        "path": "gro",
        "version_cmd": ["--version"],
        "json_flag": "--json",
        "source": "cask",
        "cask": "open-cli-collective/tap/google-readonly",
    },
}


def run_cli(cmd: list[str], timeout: int = 60) -> dict:
    """Run a CLI command and return structured output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        output = result.stdout.strip()
        stderr = result.stderr.strip()

        # Try to parse as JSON
        try:
            data = json.loads(output) if output else None
        except json.JSONDecodeError:
            data = None

        return {
            "success": result.returncode == 0,
            "exit_code": result.returncode,
            "data": data,
            "output": output if not data else None,
            "stderr": stderr if stderr else None,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Command timed out after {timeout}s"}
    except FileNotFoundError as e:
        return {"success": False, "error": f"CLI not found: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# =============================================================================
# GENERIC CLI ACCESS - Full functionality for any CLI
# =============================================================================


@mcp.tool()
def cli_help(cli: str, subcommand: Optional[str] = None) -> str:
    """
    Get help documentation for a CLI or its subcommands.
    Use this to discover available commands and options.

    cli: CLI name (jira-ticket-cli, slck, cfl, newrelic-cli, gro)
    subcommand: Optional subcommand path (e.g., "issues create" or "page list")

    Examples:
    - cli_help("jira-ticket-cli") - Get top-level help
    - cli_help("jira-ticket-cli", "issues") - Get issues subcommands
    - cli_help("cfl", "page list") - Get specific command help
    - cli_help("gro", "gmail") - Get Gmail subcommands
    """
    if cli not in CLI_CONFIG:
        return json.dumps(
            {"error": f"Unknown CLI: {cli}. Available: {list(CLI_CONFIG.keys())}"}
        )

    config = CLI_CONFIG[cli]
    cmd = [config["path"]]

    if subcommand:
        cmd.extend(subcommand.split())

    cmd.append("--help")
    result = run_cli(cmd)
    return json.dumps(result, indent=2)


@mcp.tool()
def jira_cli(args: str) -> str:
    """
    Run any jira-ticket-cli command. Full access to Jira functionality.

    args: Space-separated arguments (e.g., "issues get PROJ-1234 --output json")

    Common commands:
    - issues get <key>
    - issues create --project <key> --summary "Title" --type Task
    - issues list --project <key> --status "In Progress"
    - sprints list --board <id>
    - sprints issues --board <id> --state active
    - transitions do <key> --to "In Progress"
    - comments add <key> --body "Comment text"
    - me (show current user)

    Use cli_help("jira-ticket-cli") to discover all available commands.
    """
    config = CLI_CONFIG["jira-ticket-cli"]
    cmd = [config["path"]] + args.split()
    result = run_cli(cmd)
    return json.dumps(result, indent=2)


@mcp.tool()
def slack_cli(args: str) -> str:
    """
    Run any slck (Slack) command. Full access to Slack functionality.

    args: Space-separated arguments (e.g., "messages history --channel general --limit 50")

    Common commands:
    - channels list [--limit N]
    - channels info --channel <name-or-id>
    - messages history --channel <name> --limit N
    - messages send --channel <name> --text "Message"
    - search messages "query" [--count N]
    - users list
    - users info --user <id>
    - workspace info

    Use cli_help("slck") to discover all available commands.
    """
    config = CLI_CONFIG["slck"]
    cmd = [config["path"]] + args.split()
    result = run_cli(cmd)
    return json.dumps(result, indent=2)


@mcp.tool()
def confluence_cli(args: str) -> str:
    """
    Run any cfl (Confluence) command. Full access to Confluence functionality.

    args: Space-separated arguments (e.g., "page get <page-id> --output json")

    Common commands:
    - search "query" [--limit N]
    - page get <page-id>
    - page list --space <key>
    - page create --space <key> --title "Title" --body "Content"
    - space list
    - space get <key>
    - attachment list --page <id>

    Use cli_help("cfl") to discover all available commands.
    """
    config = CLI_CONFIG["cfl"]
    cmd = [config["path"]] + args.split()
    result = run_cli(cmd)
    return json.dumps(result, indent=2)


@mcp.tool()
def newrelic_cli(args: str) -> str:
    """
    Run any newrelic-cli command. Full access to New Relic functionality.

    args: Space-separated arguments (e.g., "logs query --nrql 'SELECT * FROM Log'")

    Common commands:
    - apps list
    - apps get <id>
    - logs query --nrql "SELECT * FROM Log WHERE ..."
    - nerdgraph query "GraphQL query"
    - alerts list
    - dashboards list
    - entities search --name "pattern"

    Use cli_help("newrelic-cli") to discover all available commands.
    """
    config = CLI_CONFIG["newrelic-cli"]
    cmd = [config["path"]] + args.split()
    result = run_cli(cmd)
    return json.dumps(result, indent=2)


@mcp.tool()
def google_cli(args: str) -> str:
    """
    Run any gro (google-readonly) command. Read-only access to Google services.

    args: Space-separated arguments

    Gmail commands:
    - gmail search --query "from:someone@example.com"
    - gmail read <message-id>
    - gmail thread <message-id>
    - gmail labels

    Calendar commands:
    - calendar list
    - calendar events --calendar <id>
    - calendar today
    - calendar week

    Contacts commands:
    - contacts list
    - contacts search "name"
    - contacts get <id>
    - contacts groups

    Drive commands:
    - drive list [--folder <id>]
    - drive search "query"
    - drive get <file-id>
    - drive download <file-id> --output <path>
    - drive tree [--folder <id>]

    Use cli_help("gro") to discover all available commands.
    """
    config = CLI_CONFIG["gro"]
    cmd = [config["path"]] + args.split()
    result = run_cli(cmd)
    return json.dumps(result, indent=2)


# =============================================================================
# CONVENIENCE WRAPPERS - Common operations with better ergonomics
# =============================================================================


@mcp.tool()
def jira_get_issue(issue_key: str) -> str:
    """Get a Jira issue by key (e.g., PROJ-1234)."""
    return jira_cli(f"issues get {issue_key} --output json")


@mcp.tool()
def slack_search_messages(query: str, count: int = 20) -> str:
    """Search Slack messages."""
    return slack_cli(f'search messages "{query}" --count {count} --output json')


@mcp.tool()
def confluence_search(query: str, limit: int = 25) -> str:
    """Search Confluence pages."""
    return confluence_cli(f'search "{query}" --limit {limit} --output json')


@mcp.tool()
def gmail_search(query: str, limit: int = 20) -> str:
    """Search Gmail messages."""
    return google_cli(f'gmail search --query "{query}" --limit {limit} --json')


@mcp.tool()
def calendar_today() -> str:
    """Get today's calendar events."""
    return google_cli("calendar today --json")


@mcp.tool()
def drive_search(query: str, limit: int = 20) -> str:
    """Search Google Drive files."""
    return google_cli(f'drive search "{query}" --limit {limit} --json')


# =============================================================================
# TOOL MANAGEMENT - Updates and status
# =============================================================================


def get_brew_path() -> str:
    """Get the brew binary path based on platform."""
    import platform

    if platform.machine() == "arm64":
        return "/opt/homebrew/bin/brew"
    return "/usr/local/bin/brew"


@mcp.tool()
def list_tools_status() -> str:
    """
    List all available CLI tools, their versions, and update status.
    Shows which CLIs are installed and whether updates are available.
    """
    status = {}
    brew = get_brew_path()

    for name, config in CLI_CONFIG.items():
        tool_status = {"source": config["source"], "cask": config["cask"]}

        # Check if installed and get version
        try:
            cmd = [config["path"]] + config["version_cmd"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            version_output = result.stdout.strip() or result.stderr.strip()
            tool_status["installed"] = True
            tool_status["version"] = version_output.split("\n")[0]
        except Exception as e:
            tool_status["installed"] = False
            tool_status["error"] = str(e)
            status[name] = tool_status
            continue

        # Check for updates via brew
        try:
            cask_name = config["cask"].split("/")[-1]
            brew_result = subprocess.run(
                [brew, "outdated", "--cask", "--greedy"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if brew_result.returncode == 0:
                tool_status["update_available"] = cask_name in brew_result.stdout
        except Exception:
            pass

        status[name] = tool_status

    return json.dumps(status, indent=2)


@mcp.tool()
def check_for_updates() -> str:
    """
    Check if any CLI tools have updates available.
    Returns a summary of tools that can be updated.
    """
    updates_available = []
    brew = get_brew_path()

    try:
        brew_result = subprocess.run(
            [brew, "outdated", "--cask", "--greedy"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if brew_result.returncode == 0:
            outdated_lines = brew_result.stdout.strip().split("\n")
            for name, config in CLI_CONFIG.items():
                cask_name = config["cask"].split("/")[-1]
                for line in outdated_lines:
                    if cask_name in line:
                        parts = line.split()
                        updates_available.append(
                            {
                                "cli": name,
                                "cask": cask_name,
                                "current": parts[1] if len(parts) > 1 else "unknown",
                                "latest": parts[-1] if len(parts) > 2 else "unknown",
                                "source": "cask",
                            }
                        )
                        break
    except Exception as e:
        logger.warning(f"Failed to check cask updates: {e}")

    return json.dumps(
        {
            "updates_available": len(updates_available) > 0,
            "tools": updates_available,
            "message": (
                f"{len(updates_available)} tool(s) have updates available"
                if updates_available
                else "All tools are up to date"
            ),
        },
        indent=2,
    )


@mcp.tool()
def update_tools(tools: Optional[list[str]] = None) -> str:
    """
    Update CLI tools to their latest versions.

    tools: Optional list of specific tools to update. If not provided, updates all tools with available updates.
           Valid names: jira-ticket-cli, slck, cfl, newrelic-cli, gro

    All tools are updated via Homebrew casks from open-cli-collective/tap.
    """
    results = []
    brew = get_brew_path()

    # Determine which tools to update
    if tools:
        tools_to_update = [t for t in tools if t in CLI_CONFIG]
    else:
        # Check what has updates
        check_result = json.loads(check_for_updates())
        tools_to_update = [t["cli"] for t in check_result.get("tools", [])]

    if not tools_to_update:
        return json.dumps({"message": "No tools to update", "results": []})

    # All tools are cask-based
    casks = [CLI_CONFIG[t]["cask"] for t in tools_to_update]
    try:
        upgrade_result = subprocess.run(
            [brew, "upgrade", "--cask"] + casks,
            capture_output=True,
            text=True,
            timeout=300,
        )
        results.append(
            {
                "tools": tools_to_update,
                "source": "homebrew cask",
                "success": upgrade_result.returncode == 0,
                "output": (
                    upgrade_result.stdout
                    if upgrade_result.returncode == 0
                    else upgrade_result.stderr
                ),
            }
        )
    except Exception as e:
        results.append(
            {
                "tools": tools_to_update,
                "source": "homebrew cask",
                "success": False,
                "error": str(e),
            }
        )

    return json.dumps(
        {
            "updated": tools_to_update,
            "results": results,
        },
        indent=2,
    )


@mcp.tool()
def install_missing_tools() -> str:
    """
    Install any CLI tools that are missing.
    All tools are installed via Homebrew casks from open-cli-collective/tap.
    """
    results = []
    missing = []
    brew = get_brew_path()

    # Check what's missing
    for name, config in CLI_CONFIG.items():
        try:
            subprocess.run(
                [config["path"]] + config["version_cmd"],
                capture_output=True,
                timeout=5,
            )
        except FileNotFoundError:
            missing.append(name)

    if not missing:
        return json.dumps({"message": "All tools are installed", "missing": []})

    # Ensure tap is added
    subprocess.run(
        [brew, "tap", "open-cli-collective/tap"], capture_output=True, timeout=60
    )

    casks = [CLI_CONFIG[t]["cask"] for t in missing]
    try:
        install_result = subprocess.run(
            [brew, "install", "--cask"] + casks,
            capture_output=True,
            text=True,
            timeout=300,
        )
        results.append(
            {
                "tools": missing,
                "source": "homebrew cask",
                "success": install_result.returncode == 0,
                "output": (
                    install_result.stdout[:500]
                    if install_result.returncode == 0
                    else install_result.stderr[:500]
                ),
            }
        )
    except Exception as e:
        results.append(
            {
                "tools": missing,
                "source": "homebrew cask",
                "success": False,
                "error": str(e),
            }
        )

    return json.dumps(
        {
            "missing_tools": missing,
            "results": results,
        },
        indent=2,
    )


if __name__ == "__main__":
    logger.info("Starting Open CLI MCP Server...")
    mcp.run(transport="stdio")
