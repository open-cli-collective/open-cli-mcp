Review only for FastMCP stdio CLI wrapper safety and behavior regressions.

Prioritize 0-5 concrete findings. Return no findings if the diff is acceptable. Avoid broad style feedback.

Focus areas:
- Subprocess boundaries and whether wrapper code preserves safe, explicit command execution.
- `shlex.split` preservation and regressions in argument quoting/escaping behavior.
- JSON output parsing, timeout handling, and consistent stdout/stderr/error result shape.
- Separation between generic CLI access and convenience wrappers.
- Homebrew cask install/update flows and whether they stay correct and unsurprising.
- Read-only expectations for the Google CLI wrapper.
- Tests that protect quoting, parsing, wrapper behavior, and failure modes.

Flag only issues that are likely to cause unsafe execution, broken wrapper behavior, misleading install/update behavior, or missing regression coverage in touched areas.
