"""Checks that the video toolchain is installed and working.

Run with:  python -m pytest -v
"""

import configparser
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_python_version():
    # Manim's OpenGL dependencies (moderngl, glcontext) ship wheels up to 3.13.
    assert (3, 11) <= sys.version_info[:2] <= (3, 13), sys.version


def test_running_inside_project_venv():
    assert Path(sys.prefix).resolve() == (PROJECT_ROOT / ".venv").resolve(), (
        f"Tests are running on {sys.prefix}; activate .venv first."
    )


@pytest.mark.parametrize("module", ["manim", "numpy", "scipy", "PIL"])
def test_python_packages_import(module):
    __import__(module)


@pytest.mark.parametrize("tool", ["ffmpeg", "latex", "dvisvgm"])
def test_external_tool_on_path(tool):
    assert shutil.which(tool), f"'{tool}' not found on PATH (see README > Troubleshooting)"


def test_theme_background_matches_manim_cfg():
    from src.themes import default_theme

    cfg = configparser.ConfigParser()
    cfg.read(PROJECT_ROOT / "manim.cfg")
    assert cfg["CLI"]["background_color"].lower() == default_theme.BACKGROUND.lower()


def test_components_build():
    from manim import Square

    import src.components as c

    square = Square()
    built = [
        c.create_title("Title"),
        c.create_subtitle("Subtitle"),
        c.create_body_text("Body"),
        c.create_label("Label"),
        c.create_highlighted_text("Key"),
        c.create_section_label("Section"),
        c.create_equation("1", "+", "2", "=", "3"),
        c.create_number_line(0, 5),
        c.create_highlight_box(square),
        c.create_info_box("Remember"),
        c.create_arrow([-1, 0, 0], [1, 0, 0]),
        c.create_curved_arrow([-1, 0, 0], [1, 0, 0]),
        c.create_pointer(square, label="here"),
        c.create_underline(square),
        c.create_correct_indicator(),
        c.create_incorrect_indicator(),
    ]
    assert all(m.width > 0 for m in built)


def test_render_hello_students(tmp_path):
    """Renders tests/test_scene.py at low quality and checks an MP4 was written."""
    cmd = [
        sys.executable, "-m", "manim", "render", "tests/test_scene.py", "HelloStudents",
        "-ql", "--media_dir", str(tmp_path),
    ]
    env = {**os.environ, "PYTHONPATH": str(PROJECT_ROOT)}
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr

    videos = [p for p in tmp_path.rglob("HelloStudents.mp4") if "partial_movie_files" not in p.parts]
    assert videos, "no MP4 produced"
    assert videos[0].stat().st_size > 10_000
