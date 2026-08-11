from unittest.mock import patch

MOCK_RESULT = {
    "success": True,
    "exit_code": 0,
    "data": None,
    "output": "",
    "stderr": None,
}


def _get_cmd(mock_run):
    """Extract the command list passed to run_cli."""
    return mock_run.call_args[0][0]


class TestArgSplitting:
    """Verify quoted arguments are preserved as single tokens, not split on whitespace."""

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_quoted_flag_values(self, mock_run):
        from server import jira_cli

        jira_cli('issues create --project PROJ --summary "Fix login bug"')
        assert _get_cmd(mock_run) == [
            "jtk", "issues", "create", "--project", "PROJ",
            "--summary", "Fix login bug",
        ]

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_multiple_quoted_flags(self, mock_run):
        from server import jira_cli

        jira_cli('issues create --project PROJ --summary "Fix bug" --description "Users cannot log in"')
        cmd = _get_cmd(mock_run)
        assert cmd[cmd.index("--summary") + 1] == "Fix bug"
        assert cmd[cmd.index("--description") + 1] == "Users cannot log in"

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_single_word_args(self, mock_run):
        from server import jira_cli

        jira_cli("issues get PROJ-123 --output json")
        assert _get_cmd(mock_run) == [
            "jtk", "issues", "get", "PROJ-123", "--output", "json",
        ]

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_single_quoted_values(self, mock_run):
        from server import newrelic_cli

        newrelic_cli("logs query --nrql 'SELECT * FROM Log'")
        cmd = _get_cmd(mock_run)
        assert cmd[cmd.index("--nrql") + 1] == "SELECT * FROM Log"

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_all_cli_functions_use_shlex(self, mock_run):
        """Every generic CLI function must handle quoted args."""
        from server import jira_cli, slack_cli, confluence_cli, newrelic_cli, google_cli

        for fn in [jira_cli, slack_cli, confluence_cli, newrelic_cli, google_cli]:
            mock_run.reset_mock()
            fn('test --flag "value with spaces"')
            cmd = _get_cmd(mock_run)
            assert "value with spaces" in cmd, f"{fn.__name__} broke quoted args"


class TestConvenienceWrappers:
    """Convenience wrappers must pass semantic params as single argv elements."""

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_slack_search(self, mock_run):
        from server import slack_search_messages

        slack_search_messages("multi word query")
        cmd = _get_cmd(mock_run)
        assert "multi word query" in cmd

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_confluence_search(self, mock_run):
        from server import confluence_search

        confluence_search("page title here")
        cmd = _get_cmd(mock_run)
        assert "page title here" in cmd

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_gmail_search(self, mock_run):
        from server import gmail_search

        gmail_search("from:someone@example.com subject:hello")
        cmd = _get_cmd(mock_run)
        assert "from:someone@example.com subject:hello" in cmd

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_drive_search(self, mock_run):
        from server import drive_search

        drive_search("quarterly report 2026")
        cmd = _get_cmd(mock_run)
        assert "quarterly report 2026" in cmd

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_jira_get_issue(self, mock_run):
        from server import jira_get_issue

        jira_get_issue("PROJ-1234")
        assert _get_cmd(mock_run) == [
            "jtk", "issues", "get", "PROJ-1234", "--output", "json",
        ]


class TestSemanticParamsSingleArgv:
    """Regression tests for issue #8: semantic free-text params must reach the
    CLI as exactly one argv element, even with embedded quotes, apostrophes,
    or search operators."""

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_gmail_search_full_argv(self, mock_run):
        from server import gmail_search

        query = '"exact phrase" OR keyword OR "other phrase" newer_than:90d'
        gmail_search(query, limit=50)
        assert _get_cmd(mock_run) == [
            "gro", "gmail", "search", "--query", query, "--limit", "50", "--json",
        ]

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_gmail_search_embedded_quotes_preserved(self, mock_run):
        from server import gmail_search

        query = 'subject:"weekly report" -from:noreply@example.com'
        gmail_search(query)
        cmd = _get_cmd(mock_run)
        assert query in cmd, "query must be a single argv element with quotes intact"

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_drive_search_full_argv(self, mock_run):
        from server import drive_search

        query = 'name contains "budget" and modifiedTime > \'2026-01-01\''
        drive_search(query, limit=5)
        assert _get_cmd(mock_run) == [
            "gro", "drive", "search", query, "--limit", "5", "--json",
        ]

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_confluence_search_full_argv(self, mock_run):
        from server import confluence_search

        query = 'title ~ "release notes" AND space = ENG'
        confluence_search(query, limit=10)
        assert _get_cmd(mock_run) == [
            "cfl", "search", query, "--limit", "10", "--output", "json",
        ]

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_slack_search_full_argv(self, mock_run):
        from server import slack_search_messages

        query = '"deploy failed" in:#alerts before:2026-08-01'
        slack_search_messages(query, count=15)
        assert _get_cmd(mock_run) == [
            "slck", "search", "messages", query, "--count", "15", "--output", "json",
        ]

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_apostrophes_survive(self, mock_run):
        from server import drive_search, gmail_search

        query = "team's quarterly plan"
        for fn in (drive_search, gmail_search):
            mock_run.reset_mock()
            fn(query)
            assert query in _get_cmd(mock_run), f"{fn.__name__} mangled apostrophe"
