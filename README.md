# Open CLI MCP Server

An MCP (Model Context Protocol) server that exposes CLI tools from the [open-cli-collective](https://github.com/open-cli-collective) as tools for Claude Code and other MCP-compatible clients.

## Included Tools

| CLI | Binary | Description |
|-----|--------|-------------|
| [atlassian-cli](https://github.com/open-cli-collective/atlassian-cli) | `jtk` | Jira Cloud ticket management |
| [slack-chat-api](https://github.com/open-cli-collective/slack-chat-api) | `slck` | Slack workspace interaction |
| [atlassian-cli](https://github.com/open-cli-collective/atlassian-cli) | `cfl` | Confluence page and space management |
| [newrelic-cli](https://github.com/open-cli-collective/newrelic-cli) | `nrq` | New Relic observability platform |
| [google-readonly](https://github.com/open-cli-collective/google-readonly) | `gro` | Read-only Google services (Gmail, Calendar, Contacts, Drive) |
| [hubspot-cli](https://github.com/open-cli-collective/hubspot-cli) | `hspt` | HubSpot CRM (contacts, companies, deals, engagements) |
| [salesforce-cli](https://github.com/open-cli-collective/salesforce-cli) | `sfdc` | Salesforce (SOQL queries, records, objects) |
| [codereview-cli](https://github.com/open-cli-collective/codereview-cli) | `cr` | Automated pull-request reviews |

> [cpm](https://github.com/open-cli-collective/cpm) (Claude plugin manager) is not included because it is an interactive TUI.

## Installation

### Prerequisites

- Python 3.10+
- [Homebrew](https://brew.sh) (for installing the CLI tools)

### Install the CLI Tools

```bash
# Add the open-cli-collective tap
brew tap open-cli-collective/tap

# Install the tools you need (all are casks)
brew install --cask open-cli-collective/tap/jtk
brew install --cask open-cli-collective/tap/slck
brew install --cask open-cli-collective/tap/cfl
brew install --cask open-cli-collective/tap/nrq
brew install --cask open-cli-collective/tap/google-readonly
brew install --cask open-cli-collective/tap/hubspot-cli
brew install --cask open-cli-collective/tap/salesforce-cli
brew install --cask open-cli-collective/tap/codereview-cli
```

### Install the MCP Server

```bash
# Clone the repository
git clone https://github.com/open-cli-collective/open-cli-mcp.git
cd open-cli-mcp

# Install Python dependencies
pip install -r requirements.txt
```

## Configuration

### Claude Code

Add to your Claude Code MCP configuration (`~/.claude/mcp_servers.json`):

```json
{
  "open-cli-mcp": {
    "command": "python3",
    "args": ["/path/to/open-cli-mcp/server.py"]
  }
}
```

### Other MCP Clients

The server runs via stdio transport. Configure your client to execute:

```bash
python3 /path/to/open-cli-mcp/server.py
```

## Usage

Once configured, the MCP server exposes these tools:

### Generic CLI Access

- `cli_help(cli, subcommand?)` - Get help for any CLI or subcommand
- `jira_cli(args)` - Run any jtk (Jira) command
- `slack_cli(args)` - Run any slck (Slack) command
- `confluence_cli(args)` - Run any cfl (Confluence) command
- `newrelic_cli(args)` - Run any nrq (New Relic) command
- `google_cli(args)` - Run any gro (Google) command (Gmail, Calendar, Contacts, Drive)
- `hubspot_cli(args)` - Run any hspt (HubSpot) command
- `salesforce_cli(args)` - Run any sfdc (Salesforce) command
- `codereview_cli(args)` - Run any cr (codereview) command

### Convenience Wrappers

- `jira_get_issue(issue_key)` - Get a Jira issue by key
- `slack_search_messages(query, count?)` - Search Slack messages
- `confluence_search(query, limit?)` - Search Confluence pages
- `gmail_search(query, limit?)` - Search Gmail messages
- `calendar_today()` - Get today's calendar events
- `drive_search(query, limit?)` - Search Google Drive files
- `salesforce_query(soql)` - Run a SOQL query against Salesforce

### Tool Management

- `list_tools_status()` - Show installed tools and versions
- `check_for_updates()` - Check for available updates
- `update_tools(tools?)` - Update tools via Homebrew
- `install_missing_tools()` - Install any missing tools

## Examples

```
# Get help for jtk (Jira)
cli_help("jtk")

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

# Query Salesforce
salesforce_query("SELECT Id, Name FROM Account LIMIT 10")

# List HubSpot contacts
hubspot_cli("contacts list --limit 20 -o json")

# Plan a PR review without posting
codereview_cli("review 123 --dry-run")

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
