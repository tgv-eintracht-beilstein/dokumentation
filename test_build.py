"""Tests for build.py — parse_frontmatter, strip_latex_commands, get_git_history."""

import logging
from pathlib import Path
from unittest.mock import patch

import pytest
from build import get_git_history, parse_frontmatter, strip_latex_commands


class TestParseFrontmatter:
    """Unit tests for parse_frontmatter."""

    def test_valid_frontmatter_with_title_and_author(self):
        content = "---\ntitle: Satzung\nauthor: TGV e.V.\n---\n# Body\n"
        meta, body = parse_frontmatter(content, "satzung.md")
        assert meta["title"] == "Satzung"
        assert meta["author"] == "TGV e.V."
        assert "# Body" in body

    def test_header_includes_stripped(self):
        content = (
            "---\ntitle: Test\nauthor: Me\n"
            "header-includes: |\n    \\usepackage{fancyhdr}\n---\nBody\n"
        )
        meta, body = parse_frontmatter(content)
        assert "header-includes" not in meta
        assert meta["title"] == "Test"

    def test_missing_frontmatter_raises(self):
        with pytest.raises(ValueError, match="missing YAML frontmatter"):
            parse_frontmatter("# No frontmatter here", "bad.md")

    def test_missing_closing_delimiter_raises(self):
        with pytest.raises(ValueError, match="no closing '---' delimiter"):
            parse_frontmatter("---\ntitle: Oops\n", "broken.md")

    def test_missing_title_raises(self):
        content = "---\nauthor: Someone\n---\nBody\n"
        with pytest.raises(ValueError, match="missing required 'title'"):
            parse_frontmatter(content, "notitle.md")

    def test_error_contains_filename(self):
        with pytest.raises(ValueError, match="myfile\\.md"):
            parse_frontmatter("no frontmatter", "myfile.md")

    def test_missing_author_defaults_to_empty(self, caplog):
        content = "---\ntitle: Solo\n---\nBody\n"
        with caplog.at_level(logging.WARNING):
            meta, body = parse_frontmatter(content, "solo.md")
        assert meta["author"] == ""
        assert "missing 'author'" in caplog.text

    def test_default_filename_in_error(self):
        with pytest.raises(ValueError, match="<unknown>"):
            parse_frontmatter("no frontmatter")

    def test_real_satzung_frontmatter(self):
        """Parse frontmatter matching the actual satzung.md format."""
        content = (
            "---\n"
            "title: Satzung\n"
            "author: TGV Eintracht Beilstein 1823 e.V.\n"
            "header-includes: |\n"
            "    \\usepackage{fancyhdr}\n"
            "    \\pagestyle{fancy}\n"
            "    \\fancyfoot[CO,CE]{TGV Eintracht Beilstein 1823 e.V.}\n"
            "    \\fancyfoot[LE,RO]{\\thepage}\n"
            "---\n\n"
            "\\newpage\n\nVorbemerkung\n"
        )
        meta, body = parse_frontmatter(content, "satzung.md")
        assert meta["title"] == "Satzung"
        assert meta["author"] == "TGV Eintracht Beilstein 1823 e.V."
        assert "header-includes" not in meta
        assert "\\newpage" in body


class TestStripLatexCommands:
    """Unit tests for strip_latex_commands."""

    def test_removes_newpage(self):
        assert strip_latex_commands("Hello\n\\newpage\nWorld") == "Hello\n\nWorld"

    def test_removes_usepackage(self):
        assert strip_latex_commands("\\usepackage{fancyhdr}") == ""

    def test_removes_pagestyle(self):
        assert strip_latex_commands("\\pagestyle{fancy}") == ""

    def test_removes_thepage(self):
        assert strip_latex_commands("Page \\thepage here") == "Page  here"

    def test_removes_fancyfoot_with_bracket_and_brace(self):
        result = strip_latex_commands("\\fancyfoot[CO,CE]{TGV Eintracht}")
        assert result == ""

    def test_removes_fancyhead_with_bracket_and_brace(self):
        result = strip_latex_commands("\\fancyhead[L]{Header Text}")
        assert result == ""

    def test_preserves_non_latex_content(self):
        text = "# Heading\n\nSome paragraph with normal text.\n\n1. List item\n"
        assert strip_latex_commands(text) == text

    def test_mixed_content_preserves_surrounding_text(self):
        text = "Before\n\\newpage\nAfter"
        result = strip_latex_commands(text)
        assert "Before" in result
        assert "After" in result
        assert "\\newpage" not in result

    def test_collapses_blank_lines_from_removed_commands(self):
        text = "Above\n\n\\newpage\n\nBelow"
        result = strip_latex_commands(text)
        # Should not have more than one blank line
        assert "\n\n\n" not in result
        assert "Above" in result
        assert "Below" in result

    def test_multiple_commands_removed(self):
        text = "\\usepackage{fancyhdr}\n\\pagestyle{fancy}\n\\fancyfoot[LE,RO]{\\thepage}\n"
        result = strip_latex_commands(text)
        assert "\\" not in result

    def test_empty_string(self):
        assert strip_latex_commands("") == ""

    def test_real_world_satzung_body(self):
        """Simulate the original satzung.md body with LaTeX commands."""
        body = "\\newpage\n\nVorbemerkung\n\n1. Allgemeines\n"
        result = strip_latex_commands(body)
        assert "\\newpage" not in result
        assert "Vorbemerkung" in result
        assert "1. Allgemeines" in result


class TestGetGitHistory:
    """Unit tests for get_git_history."""

    def test_parses_standard_git_log_output(self):
        fake_output = (
            "2024-07-26|Alice|Add section 3\n"
            "2024-01-10|Bob|Initial commit\n"
        )
        with patch("build.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = fake_output
            result = get_git_history(Path("some.md"))

        assert len(result) == 2
        assert result[0] == {"date": "2024-07-26", "author": "Alice", "message": "Add section 3"}
        assert result[1] == {"date": "2024-01-10", "author": "Bob", "message": "Initial commit"}

    def test_message_with_pipe_characters(self):
        """Commit messages containing pipes should be kept intact."""
        fake_output = "2024-03-01|Dev|fix: a|b|c edge case\n"
        with patch("build.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = fake_output
            result = get_git_history(Path("x.md"))

        assert len(result) == 1
        assert result[0]["message"] == "fix: a|b|c edge case"

    def test_empty_output_returns_empty_list(self):
        """Untracked file produces empty git log output."""
        with patch("build.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = ""
            result = get_git_history(Path("untracked.md"))

        assert result == []

    def test_git_not_found_returns_empty_list(self, caplog):
        with patch("build.subprocess.run", side_effect=FileNotFoundError):
            with caplog.at_level(logging.WARNING):
                result = get_git_history(Path("file.md"))

        assert result == []
        assert "git not available" in caplog.text

    def test_nonzero_returncode_returns_empty_list(self, caplog):
        with patch("build.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 128
            mock_run.return_value.stderr = "fatal: not a git repo"
            with caplog.at_level(logging.WARNING):
                result = get_git_history(Path("file.md"))

        assert result == []
        assert "git log failed" in caplog.text

    def test_timeout_returns_empty_list(self, caplog):
        import subprocess
        with patch("build.subprocess.run", side_effect=subprocess.TimeoutExpired("git", 10)):
            with caplog.at_level(logging.WARNING):
                result = get_git_history(Path("slow.md"))

        assert result == []
        assert "timed out" in caplog.text

    def test_newest_first_ordering_preserved(self):
        """Git log already returns newest first — verify we don't re-sort."""
        fake_output = (
            "2025-01-01|A|newest\n"
            "2024-06-15|B|middle\n"
            "2023-01-01|C|oldest\n"
        )
        with patch("build.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = fake_output
            result = get_git_history(Path("doc.md"))

        assert [e["date"] for e in result] == ["2025-01-01", "2024-06-15", "2023-01-01"]

    def test_malformed_line_skipped(self):
        """Lines without enough pipe separators are silently skipped."""
        fake_output = "2024-01-01|OnlyTwoParts\n2024-02-01|Good|Line\n"
        with patch("build.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = fake_output
            result = get_git_history(Path("x.md"))

        assert len(result) == 1
        assert result[0]["message"] == "Line"


from build import render_html


class TestRenderHtml:
    """Unit tests for render_html — validates Requirements 2.6, 3.1, 4.4, 5.1, 5.2, 8.1, 8.3."""

    def test_title_appears_on_cover_page(self):
        html = render_html("Satzung", "TGV e.V.", "<p>Body</p>", [], None)
        assert "<h1>Satzung</h1>" in html

    def test_author_passed_to_template(self):
        html = render_html("Test", "TGV Eintracht Beilstein 1823 e.V.", "<p>Body</p>", [], None)
        # Author is available in the rendered output (used by CSS footer via template)
        assert "TGV Eintracht Beilstein 1823 e.V." in html

    def test_body_html_rendered_in_content(self):
        body = "<h2>§1 Allgemeines</h2><p>Der Verein führt den Namen...</p>"
        html = render_html("Satzung", "Author", body, [], None)
        assert "§1 Allgemeines" in html
        assert "Der Verein führt den Namen" in html

    def test_logo_path_in_cover_img(self):
        html = render_html("Test", "Author", "<p>Body</p>", [], "file:///path/to/logo.svg")
        assert 'src="file:///path/to/logo.svg"' in html

    def test_logo_none_still_renders(self):
        html = render_html("Test", "Author", "<p>Body</p>", [], None)
        assert 'src="None"' in html or "<h1>Test</h1>" in html

    def test_history_section_rendered_when_present(self):
        history = [
            {"date": "2025-01-15", "author": "Alice", "message": "Update §3"},
            {"date": "2024-06-01", "author": "Bob", "message": "Initial version"},
        ]
        html = render_html("Satzung", "Author", "<p>Body</p>", history, None)
        assert "Änderungshistorie" in html
        assert "2025-01-15" in html
        assert "Alice" in html
        assert "Update §3" in html
        assert "2024-06-01" in html
        assert "Bob" in html
        assert "Initial version" in html

    def test_history_section_omitted_when_empty(self):
        html = render_html("Satzung", "Author", "<p>Body</p>", [], None)
        assert "Änderungshistorie" not in html

    def test_html_is_valid_document(self):
        html = render_html("Test", "Author", "<p>Hello</p>", [], None)
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html

    def test_club_name_on_cover(self):
        html = render_html("Test", "Author", "<p>Body</p>", [], None)
        assert "TGV Eintracht Beilstein 1823 e.V." in html
