# Open CLI Tools MCP Server

An MCP (Model Context Protocol) server that exposes CLI tools from the [open-cli-collective](https://github.com/open-cli-collective) as tools for Claude Code and other MCP-compatible clients.

## Included Tools

| CLI | Binary | Description |
|-----|--------|-------------|
| [jira-ticket-cli](https://github.com/open-cli-collective/jira-ticket-cli) | `jira-ticket-cli` | Jira Cloud ticket management |
| [slack-chat-api](https://github.com/open-cli-collective/slack-chat-api) | `slck` | Slack workspace interaction |
| [confluence-cli](https://github.com/open-cli-collective/confluence-cli) | `cfl` | Confluence page and space management |
| [newrelic-cli](https://github.com/open-cli-collective/newrelic-cli) | `newrelic-cli` | New Relic observability platform |
| [google-readonly](https://github.com/open-cli-collective/google-readonly) | `gro` | Read-only Google services (Gmail, Calendar, Contacts, Drive) |

## Installation

### Prerequisites

- Python 3.10+
- [Homebrew](https://brew.sh) (for installing the CLI tools)

### Install the CLI Tools

```bash
# Add the open-cli-collective tap
brew tap open-cli-collective/tap

# Install the tools you need (all are casks)
brew install --cask open-cli-collective/tap/jira-ticket-cli
brew install --cask open-cli-collective/tap/slack-chat-cli
brew install --cask open-cli-collective/tap/cfl
brew install --cask open-cli-collective/tap/newrelic-cli
brew install --cask open-cli-collective/tap/google-readonly
```

### Install the MCP Server

```bash
# Clone the repository
git clone https://github.com/open-cli-collective/open-cli-tools.git
cd open-cli-tools

# Install Python dependencies
pip install -r requirements.txt
```

## Configuration

### Claude Code

Add to your Claude Code MCP configuration (`~/.claude/mcp_servers.json`):

```json
{
  "open-cli-tools": {
    "command": "python3",
    "args": ["/path/to/open-cli-tools/server.py"]
  }
}
```

### Other MCP Clients

The server runs via stdio transport. Configure your client to execute:

```bash
python3 /path/to/open-cli-tools/server.py
```

## Usage

Once configured, the MCP server exposes these tools:

### Generic CLI Access

- `cli_help(cli, subcommand?)` - Get help for any CLI or subcommand
- `jira_cli(args)` - Run any jira-ticket-cli command
- `slack_cli(args)` - Run any slck command
- `confluence_cli(args)` - Run any cfl command
- `newrelic_cli(args)` - Run any newrelic-cli command
- `google_cli(args)` - Run any gro command (Gmail, Calendar, Contacts, Drive)

### Convenience Wrappers

- `jira_get_issue(issue_key)` - Get a Jira issue by key
- `slack_search_messages(query, count?)` - Search Slack messages
- `confluence_search(query, limit?)` - Search Confluence pages
- `gmail_search(query, limit?)` - Search Gmail messages
- `calendar_today()` - Get today's calendar events
- `drive_search(query, limit?)` - Search Google Drive files

### Tool Management

- `list_tools_status()` - Show installed tools and versions
- `check_for_updates()` - Check for available updates
- `update_tools(tools?)` - Update tools via Homebrew
- `install_missing_tools()` - Install any missing tools

## Examples

```
# Get help for jira-ticket-cli
cli_help("jira-ticket-cli")

# Get a Jira issue
jira_get_issue("PROJ-1234")

# Search Slack
slack_search_messages("deployment failed", count=10)

# Search Confluence
confluence_search("API documentation", limit=5)

# Search Gmail
gmail_search("from:boss@company.com", limit=10)

# Get today's calendar
calendar_today()

# Search Google Drive
drive_search("quarterly report", limit=5)

# Check tool versions
list_tools_status()
```

## Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run the server directly
python3 server.py
```

## Contributing

Contributions are welcome! Please see the [open-cli-collective organization](https://github.com/open-cli-collective) for contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
