
from typer.testing import CliRunner

from gideon.cli import app


runner = CliRunner()


def test_explain_recognizes_grep_z_and_arguments():
    result = runner.invoke(
        app,
        ["explain", "grep -z ERROR file.txt"],
    )

    assert result.exit_code == 0
    assert "-z" in result.output
    assert "NUL-separated records" in result.output
    assert "PATTERN" in result.output
    assert "FILE" in result.output
    assert "Recognized argument" in result.output


def test_explain_expands_combined_short_flags():
    result = runner.invoke(
        app,
        ["explain", "grep -in ERROR file.txt"],
    )

    assert result.exit_code == 0
    assert "-i" in result.output
    assert "-n" in result.output
    assert "Ignore case" in result.output
    assert "line numbers" in result.output


def test_explain_respects_end_of_options_marker():
    result = runner.invoke(
        app,
        ["explain", "grep -- -filename.txt"],
    )

    assert result.exit_code == 0
    assert "End of options" in result.output
    assert "-filename.txt" in result.output
    assert "Recognized argument" in result.output


def test_explain_supports_basic_pipeline():
    result = runner.invoke(
        app,
        ["explain", "grep ERROR file.txt | wc -l"],
    )

    assert result.exit_code == 0
    assert "Pipeline stage 1" in result.output
    assert "Pipeline stage 2" in result.output
    assert "grep" in result.output
    assert "wc" in result.output
    assert "standard output" in result.output


def test_explain_marks_unknown_option_as_unverified():
    result = runner.invoke(
        app,
        ["explain", "grep --unknown ERROR file.txt"],
    )

    assert result.exit_code == 0
    assert "--unknown" in result.output
    assert "Unverified" in result.output
    assert "Option not found" in result.output


def test_explain_rejects_unsupported_shell_operators():
    result = runner.invoke(
        app,
        ["explain", "grep ERROR file.txt && echo done"],
    )

    assert result.exit_code == 2
    assert "doesn't analyze yet" in result.output
    assert "empty stage" not in result.output
