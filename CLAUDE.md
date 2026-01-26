# Open CLI MCP Server

This is an MCP server that exposes open-cli-collective CLI tools to Claude Code.

## Architecture

- `server.py` - FastMCP-based server exposing CLI tools as MCP tools
- All CLIs are installed via Homebrew casks from `open-cli-collective/tap`

## Included CLIs

| Binary | Cask | Description |
|--------|------|-------------|
| `jira-ticket-cli` | jira-ticket-cli | Jira Cloud management |
| `slck` | slack-chat-cli | Slack workspace interaction |
| `cfl` | cfl | Confluence CLI |
| `newrelic-cli` | newrelic-cli | New Relic observability |
| `gro` | google-readonly | Read-only Google services (Gmail, Calendar, Contacts, Drive) |

## Making Changes

When adding new tools:
1. Add to `CLI_CONFIG` dict with path, version_cmd, json_flag, source, and cask
2. Create a dedicated tool function (e.g., `@mcp.tool() def new_cli(args: str)`)
3. Optionally add convenience wrappers for common operations
4. Update README with the new tool

## Testing

Run the server directly to test:
```bash
python3 server.py
```

The server uses stdio transport and will wait for MCP protocol messages.
