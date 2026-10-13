"""Human-readable layout validation report (console, logs, error messages)."""

from __future__ import annotations

from src.validation.layout import ERROR, INFO, WARNING


def summary_line(results: dict) -> str:
    counts = results.get("summary", {})
    parts = [f"{counts.get(s, 0)} {label}" for s, label in ((ERROR, "error(s)"), (WARNING, "warning(s)"), (INFO, "info"))]
    return "Layout validation: " + ", ".join(parts)


def location(issue: dict) -> str:
    parts = []
    if issue.get("scene"):
        parts.append(f"scene '{issue['scene']}'")
    if issue.get("time") is not None:
        parts.append(f"~{issue['time']:.1f}s")
    if issue.get("line"):
        parts.append(f"animation.py line {issue['line']}")
    return ", ".join(parts)


def format_issue(issue: dict) -> str:
    where = location(issue)
    seen = f" (+{issue['similar']} more like it)" if issue.get("similar") else ""
    text = f"{issue['severity']:<7} [{issue['code']}] {issue['message']}{seen}"
    if where:
        text += f"\n          at {where}"
    if issue.get("fix"):
        text += "\n          fix: " + issue["fix"].replace("\n", "\n          ")
    return text


def format_report(results: dict, include_info: bool = True) -> str:
    issues = [i for i in results.get("issues", []) if include_info or i["severity"] != INFO]
    lines = [summary_line(results)]
    lines += ["  " + format_issue(i) for i in issues]
    return "\n".join(lines)


def one_line(issue: dict) -> str:
    """Short form for warning lists (web UI, metadata.json)."""
    where = location(issue)
    return f"Layout {issue['severity']}: {issue['message']}" + (f" ({where})" if where else "")


def errors(results: dict) -> list[dict]:
    return [i for i in results.get("issues", []) if i["severity"] == ERROR]
