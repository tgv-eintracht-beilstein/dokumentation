"""PDF build pipeline for TGV Eintracht Beilstein 1823 e.V. club documents."""

from __future__ import annotations

import base64
import locale
import logging
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent
DOCS_DIR = ROOT / "docs"
TEMPLATE_DIR = ROOT / "templates"
ASSETS_DIR = ROOT / "assets"
LOGO_PATH = ASSETS_DIR / "TGV Logo.png"
LOGO_SW_PATH = ASSETS_DIR / "TGV Logo SW.svg"


@dataclass
class BuildResult:
    source: Path
    output: Path | None
    success: bool
    error: str | None = None


def parse_frontmatter(content: str, filename: str = "<unknown>") -> tuple[dict, str]:
    """Split YAML frontmatter from Markdown body."""
    if not content.startswith("---"):
        raise ValueError(f"{filename}: missing YAML frontmatter (no opening '---' delimiter)")

    end_index = content.find("---", 3)
    if end_index == -1:
        raise ValueError(f"{filename}: missing YAML frontmatter (no closing '---' delimiter)")

    yaml_block = content[3:end_index].strip()
    body = content[end_index + 3:].lstrip("\n")

    metadata: dict = yaml.safe_load(yaml_block) or {}
    metadata.pop("header-includes", None)

    if "title" not in metadata:
        raise ValueError(f"{filename}: missing required 'title' field in frontmatter")

    if "author" not in metadata:
        logger.warning("%s: missing 'author' field, using empty string", filename)
        metadata["author"] = ""

    return metadata, body


def strip_latex_commands(text: str) -> str:
    """Remove any remaining LaTeX commands from markdown text."""
    text = re.sub(r"\\newpage\b", "", text)
    text = re.sub(r"\\usepackage\{[^}]*\}", "", text)
    text = re.sub(r"\\pagestyle\{[^}]*\}", "", text)
    text = re.sub(r"\\fancyfoot\[[^\]]*\]\{[^}]*\}", "", text)
    text = re.sub(r"\\fancyhead\[[^\]]*\]\{[^}]*\}", "", text)
    text = re.sub(r"\\thepage\b", "", text)
    # Clean up blank lines left behind
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def get_git_history(file_path: Path) -> list[dict]:
    """Extract git log entries for a file, newest first."""
    try:
        result = subprocess.run(
            ["git", "log", "--format=%ad|%an|%s", "--date=short", "--", str(file_path)],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            logger.warning("git log failed for %s: %s", file_path, result.stderr.strip())
            return []
    except FileNotFoundError:
        logger.warning("git not available, skipping history for %s", file_path)
        return []
    except subprocess.TimeoutExpired:
        logger.warning("git log timed out for %s", file_path)
        return []
    except subprocess.SubprocessError as exc:
        logger.warning("git log error for %s: %s", file_path, exc)
        return []

    entries = []
    for line in result.stdout.strip().splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3:
            entries.append({"date": parts[0], "author": parts[1], "message": parts[2]})
    return entries



def extract_toc(body: str) -> list[dict]:
    """Extract top-level TOC entries from markdown headings.

    Returns a flat list of top-level sections (## N. Title) with an id for linking.
    """
    sections: list[dict] = []

    for line in body.splitlines():
        match = re.match(r"^##\s+(\d+)\.\s+(.+)$", line)
        if match:
            number = match.group(1)
            title = match.group(2).strip()
            slug = f"section-{number}"
            sections.append({"number": number, "title": title, "id": slug})

    return sections







def svg_to_data_uri(svg_path: Path) -> str | None:
    """Convert an SVG file to a small PNG and return a base64 data URI."""
    if not svg_path.exists():
        logger.warning("SVG not found: %s", svg_path)
        return None
    import cairosvg  # noqa: PLC0415

    png_bytes = cairosvg.svg2png(url=str(svg_path), output_height=80)
    b64 = base64.b64encode(png_bytes).decode("ascii")
    return f"data:image/png;base64,{b64}"


def render_html(
    title: str, author: str, body_html: str,
    history: list[dict], logo_path: str | None,
    preface: str | None = None,
    toc: list[dict] | None = None,
    footer_logo_uri: str | None = None,
) -> str:
    """Render the full HTML document using the Jinja2 template."""
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("template.html")

    # Format build date in German locale style: "16. Februar 2026"
    try:
        locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
        build_date = date.today().strftime("%-d. %B %Y")
        build_month_year = date.today().strftime("%B %Y")
    except locale.Error:
        # Fallback: manual German month names
        months = [
            "", "Januar", "Februar", "März", "April", "Mai", "Juni",
            "Juli", "August", "September", "Oktober", "November", "Dezember",
        ]
        today = date.today()
        build_date = f"{today.day}. {months[today.month]} {today.year}"
        build_month_year = f"{months[today.month]} {today.year}"

    return template.render(
        title=title, author=author, body_html=body_html,
        history=history, logo_path=logo_path, preface=preface,
        toc=toc or [], build_date=build_date,
        build_month_year=build_month_year,
        footer_logo_uri=footer_logo_uri,
    )




def build_document(md_path: Path, output_dir: Path) -> BuildResult:
    """Build a single PDF from a Markdown source file."""
    try:
        content = md_path.read_text(encoding="utf-8")
        metadata, body = parse_frontmatter(content, md_path.name)
        body = strip_latex_commands(body)

        toc = extract_toc(body)

        body_html = markdown.markdown(body, extensions=["tables", "toc"])

        # Inject id attributes into h2 tags so TOC links can target them
        for entry in toc:
            pattern = re.compile(
                rf'<h2 id="[^"]*">\s*{re.escape(entry["number"])}\.\s*',
            )
            body_html = pattern.sub(
                f'<h2 id="{entry["id"]}">{entry["number"]}. ',
                body_html,
                count=1,
            )

        history = get_git_history(md_path)

        logo_uri = LOGO_PATH.as_uri() if LOGO_PATH.exists() else None
        footer_logo_uri = svg_to_data_uri(LOGO_SW_PATH)

        html_str = render_html(
            title=metadata["title"],
            author=metadata.get("author", ""),
            body_html=body_html,
            history=history,
            logo_path=logo_uri,
            preface=metadata.get("preface"),
            toc=toc,
            footer_logo_uri=footer_logo_uri,
        )

        output_path = output_dir / f"{md_path.stem}.pdf"
        # Lazy import — WeasyPrint needs native libs (Pango/GLib) only at PDF time
        from weasyprint import HTML  # noqa: PLC0415
        HTML(string=html_str, base_url=str(TEMPLATE_DIR)).write_pdf(str(output_path))

        logger.info("✓ %s → %s", md_path.name, output_path.name)
        return BuildResult(source=md_path, output=output_path, success=True)

    except Exception as e:
        logger.error("✗ %s: %s", md_path.name, e)
        return BuildResult(source=md_path, output=None, success=False, error=str(e))


def build_all() -> None:
    """Discover all .md files in project root and build PDFs."""
    output_dir = ROOT / "dist"
    output_dir.mkdir(exist_ok=True)

    md_files = sorted(DOCS_DIR.glob("*.md"))
    if not md_files:
        logger.error("No .md files found in %s", DOCS_DIR)
        sys.exit(1)

    logger.info("Building %d documents...", len(md_files))
    results = [build_document(f, output_dir) for f in md_files]

    successes = [r for r in results if r.success]
    failures = [r for r in results if not r.success]

    print(f"\n{'='*40}")
    print(f"  {len(successes)} succeeded, {len(failures)} failed")
    if failures:
        for f in failures:
            print(f"  FAIL: {f.source.name} — {f.error}")
        sys.exit(1)
    print(f"  PDFs in: {output_dir}/")
    print(f"{'='*40}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    build_all()
