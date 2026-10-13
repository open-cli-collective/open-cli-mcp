import json
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
    """Convenience wrappers pass argument lists, so a value is one token whatever it contains."""

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_jira_get_issue(self, mock_run):
        from server import jira_get_issue

        jira_get_issue("PROJ-1234")
        assert _get_cmd(mock_run) == ["jtk", "issues", "get", "PROJ-1234"]

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_slack_search(self, mock_run):
        from server import slack_search_messages

        slack_search_messages("multi word query", count=5)
        assert _get_cmd(mock_run) == ["slck", "search", "messages", "multi word query", "--count", "5"]

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_confluence_search(self, mock_run):
        from server import confluence_search

        confluence_search("page title here", limit=3)
        assert _get_cmd(mock_run) == ["cfl", "search", "page title here", "--limit", "3"]

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_gmail_search(self, mock_run):
        from server import gmail_search

        gmail_search("from:someone@example.com subject:hello", limit=7)
        assert _get_cmd(mock_run) == [
            "gro", "mail", "search", "from:someone@example.com subject:hello", "--max", "7",
        ]

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_calendar_today(self, mock_run):
        from server import calendar_today

        calendar_today()
        assert _get_cmd(mock_run) == ["gro", "calendar", "today"]

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_drive_search(self, mock_run):
        from server import drive_search

        drive_search("quarterly report 2026", limit=2)
        assert _get_cmd(mock_run) == ["gro", "drive", "search", "quarterly report 2026", "--max", "2"]

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_query_with_quotes_stays_one_token(self, mock_run):
        from server import gmail_search

        gmail_search('"exact phrase" newer_than:1d')
        assert '"exact phrase" newer_than:1d' in _get_cmd(mock_run)


class TestGranolaPassthrough:
    """granola admits the read-only data commands and refuses sign-in, clearing
    the stored session, and tools call before anything runs."""

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_read_only_commands_run(self, mock_run):
        from server import granola

        for args in (
            "meetings list --time-range this_week --mine",
            "meetings get abc def",
            "meetings transcript abc",
            "m ls",
            "folders list",
            "account get",
            "tools list",
            "tools get list_meetings",
            "config show --json",
            "version",
            "--help",
            "-h",
        ):
            mock_run.reset_mock()
            granola(args)
            assert _get_cmd(mock_run) == ["granola"] + args.split(), args

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_query_keeps_quoted_question_and_long_timeout(self, mock_run):
        from server import granola

        granola('meetings query "what did we decide about the rollout?"')
        assert _get_cmd(mock_run) == [
            "granola", "meetings", "query", "what did we decide about the rollout?",
        ]
        assert mock_run.call_args.kwargs["timeout"] == 240

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_refused_commands_never_run(self, mock_run):
        from server import granola

        for args in (
            "",
            "login",
            "login --no-browser",
            "config clear",
            "config",
            "tools",
            "tools call get_account_info",
            "completion zsh",
            "-v login",
            "--help login",
            "-h config clear",
        ):
            out = json.loads(granola(args))
            assert out["success"] is False, args
            assert "not available through this passthrough" in out["error"], args
        mock_run.assert_not_called()

    @patch("server.run_cli", return_value=MOCK_RESULT)
    def test_unbalanced_quotes_are_an_error(self, mock_run):
        from server import granola

        out = json.loads(granola('meetings query "unterminated'))
        assert out["success"] is False
        assert "check quoting" in out["error"]
        mock_run.assert_not_called()
