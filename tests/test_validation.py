"""Layout validation (src/validation): text in boxes, frame, overlaps, sizes, auto-fit, generator integration."""

import json
import shutil
import textwrap
import uuid

import pytest
from manim import DOWN, LEFT, RIGHT, UP, Circle, Rectangle, RoundedRectangle, Scene, Text, VGroup, config

from src.config.settings import DEFAULTS, deep_merge
from src.config.video_config import MEDIA_DIR
from src.utils.errors import LMSError
from src.validation import ERROR, INFO, WARNING, LayoutValidator, format_report
from tests.test_pipeline import make_generator


class Stage(Scene):
    """A bare scene: mobjects are placed, never rendered."""


def validator(*mobjects, **config) -> LayoutValidator:
    scene = Stage()
    scene.add(*mobjects)
    return LayoutValidator(scene, config)


def codes(v: LayoutValidator) -> list[tuple[str, str]]:
    return [(i.severity, i.code) for i in v.issues]


# --------------------------------------------------------------- text in boxes

def test_text_overflowing_its_box_is_an_error_naming_both_objects():
    box = RoundedRectangle(width=2.0, height=1.0)
    label = Text("MEMBER FUNCTIONS", font_size=30).move_to(box)
    card = VGroup(box, label)
    v = validator(card)
    v.checkpoint()

    [issue] = v.issues
    assert (issue.severity, issue.code) == (ERROR, "text_overflow")
    assert issue.objects == ['label (Text "MEMBER FUNCTIONS")', "box (RoundedRectangle)"]
    assert "left" in issue.message and "right" in issue.message
    assert issue.line is not None                                     # the line in this file that checked
    assert "check_fit(label, box" in issue.fix


def test_text_that_fits_is_fine_and_a_text_filling_the_box_is_a_warning():
    roomy_box = Rectangle(width=4, height=1.2)
    roomy = Text("fits", font_size=30).move_to(roomy_box)
    v = validator(VGroup(roomy_box, roomy))
    v.checkpoint()
    assert v.issues == []

    label = Text("almost too wide", font_size=30)
    snug_box = Rectangle(width=label.width + 0.02, height=1.2).move_to(label)
    v = validator(VGroup(snug_box, label))
    v.checkpoint()
    assert codes(v) == [(WARNING, "text_too_large")]


def test_label_on_a_circle_rim_is_not_its_content_but_one_inside_must_fit():
    ring = Circle(radius=2)
    rim_label = Text("N", font_size=30).move_to(ring.point_at_angle(0.8))
    v = validator(ring, rim_label)
    v.checkpoint()
    assert v.issues == []

    small = Circle(radius=0.4)
    inside = Text("TOO LONG", font_size=30).move_to(small)
    v = validator(VGroup(small, inside))
    v.checkpoint()
    assert codes(v) == [(ERROR, "text_overflow")]


# ------------------------------------------------------------------- the frame

def test_frame_overflow_offscreen_and_safe_area():
    half_width = config.frame_width / 2
    cut = Text("cut off at the edge", font_size=36).move_to(RIGHT * half_width)
    gone = Text("parked off stage", font_size=36).move_to(LEFT * (half_width + 5))
    edge = Text("close to the edge", font_size=36)
    edge.move_to(UP * (config.frame_height / 2 - edge.height / 2 - 0.1))   # inside, but within the margin
    v = validator(cut, gone, edge)
    v.checkpoint()

    found = {i.code: i for i in v.issues}
    assert found["frame_overflow"].severity == ERROR and "right" in found["frame_overflow"].message
    assert found["off_screen"].severity == INFO
    assert found["safe_area"].severity == WARNING
    assert len(v.issues) == 3


def test_shapes_bigger_than_the_frame_are_backgrounds_not_overflow():
    background = Rectangle(width=config.frame_width + 2, height=config.frame_height + 2)
    v = validator(background)
    v.checkpoint()
    assert v.issues == []


# --------------------------------------------------------------------- overlap

def test_colliding_texts_are_reported_but_groups_and_glow_copies_are_not():
    a = Text("DATA MEMBERS", font_size=36)
    b = Text("MEMBER FUNCTIONS", font_size=36).move_to(a).shift(RIGHT * 0.3)
    v = validator(a, b)
    v.checkpoint()
    assert codes(v) == [(WARNING, "overlap")]

    grouped = VGroup(Text("DATA MEMBERS", font_size=36), Text("MEMBER FUNCTIONS", font_size=36).shift(RIGHT * 0.3))
    v = validator(grouped)
    v.checkpoint()
    assert v.issues == []                                             # one design on purpose

    title = Text("Glowing title", font_size=40)
    glow = title.copy().set_opacity(0.3)
    v = validator(title, glow)
    v.checkpoint()
    assert v.issues == []                                             # a glow layer is a copy


def test_touching_texts_within_tolerance_are_fine():
    a = Text("above", font_size=36)
    b = Text("below", font_size=36).next_to(a, DOWN, buff=0)
    v = validator(a, b)
    v.checkpoint()
    assert v.issues == []


# ------------------------------------------------------------------ text sizes

def test_text_too_small_after_scaling_is_a_warning_or_an_error():
    small = Text("small", font_size=24).scale(0.5).shift(UP)          # effective size 12
    tiny = Text("tiny", font_size=24).scale(0.3).shift(DOWN)          # effective size 7.2
    v = validator(small, tiny)
    v.checkpoint()
    severities = {i.objects[0]: i.severity for i in v.issues if i.code == "text_too_small"}
    assert severities == {'small (Text "small")': WARNING, 'tiny (Text "tiny")': ERROR}


def test_many_equally_small_labels_are_one_grouped_issue():
    row = VGroup(*[Text(str(n), font_size=12) for n in range(8)]).arrange(RIGHT, buff=0.5)
    v = LayoutValidator(Stage(), {})
    v.scene.add(*row)
    v.checkpoint()
    [issue] = v.issues
    assert issue.code == "text_too_small" and issue.similar == 7


# ------------------------------------------------------------ explicit checks

def test_check_fit_auto_fits_overflowing_text_into_its_box():
    box = RoundedRectangle(width=3.0, height=1.0)
    label = Text("A long label for a small card", font_size=36).move_to(box).shift(RIGHT * 0.4)
    v = validator(VGroup(box, label), min_font_size=10)

    assert v.check_fit(label, box, margin=0.1)
    assert label.width <= box.width - 0.2 + 1e-6
    assert box.get_left()[0] + 0.1 - 1e-6 <= label.get_left()[0] and label.get_right()[0] <= box.get_right()[0] - 0.1 + 1e-6
    assert codes(v) == [(INFO, "auto_fit")]
    v.checkpoint()
    assert codes(v) == [(INFO, "auto_fit")]                            # fitted: nothing else to report


def test_check_fit_never_shrinks_text_below_the_readable_minimum():
    box = Rectangle(width=1.0, height=0.6)
    label = Text("Far too much text for this box", font_size=30).move_to(box)
    before = label.width
    v = validator(VGroup(box, label))

    assert not v.check_fit(label, box)
    assert label.width == before                                     # left alone, reported instead
    [issue] = v.issues
    assert issue.severity == ERROR and "below the readable minimum" in issue.message


def test_check_fit_without_auto_fit_only_reports():
    box = Rectangle(width=1.5, height=0.8)
    label = Text("overflowing", font_size=36).move_to(box)
    before = label.width
    v = validator(VGroup(box, label), auto_fit=False)
    assert not v.check_fit(label, box)
    assert label.width == before and codes(v) == [(ERROR, "text_overflow")]


def test_fitting_is_identical_when_nothing_is_recorded():
    """While rendering the validator records nothing, but check_fit must still resize: same video."""
    sizes = []
    for record in (True, False):
        box = RoundedRectangle(width=3.0, height=1.0)
        label = Text("A long label for a small card", font_size=36).move_to(box)
        v = LayoutValidator(Stage(), {"min_font_size": 10}, record=record)
        v.check_fit(label, box)
        sizes.append((round(label.width, 6), tuple(label.get_center().round(6))))
        assert bool(v.issues) == record
    assert sizes[0] == sizes[1]


def test_spacing_size_frame_and_overlap_checks():
    a = Rectangle(width=1, height=1)
    b = Rectangle(width=1, height=1).next_to(a, RIGHT, buff=0.1)
    v = validator(a, b)
    assert not v.check_spacing(a, b, min_gap=0.3)
    assert v.check_spacing(a, b, min_gap=0.05, max_gap=0.2)
    assert not v.check_size(a, max_width=0.5)
    assert v.check_size(a, max_width=2, min_height=0.5)
    assert not v.check_in_frame(Text("out").move_to(RIGHT * 10))
    assert not v.check_no_overlap(a, Rectangle(width=1, height=1).shift(RIGHT * 0.5))
    assert [i.code for i in v.issues] == ["spacing", "size", "frame_overflow", "overlap"]
    assert all(i.severity == ERROR for i in v.issues)


def test_ignore_leaves_objects_out_of_the_automatic_checks():
    label = Text("deliberately off the edge").move_to(RIGHT * config.frame_width / 2)
    v = validator(label)
    v.ignore(label)
    v.checkpoint()
    assert v.issues == []


def test_results_are_machine_readable_and_the_report_is_readable():
    box = Rectangle(width=1.5, height=0.8)
    label = Text("overflowing", font_size=36).move_to(box)
    v = validator(VGroup(box, label))
    v.checkpoint()
    results = json.loads(json.dumps(v.results()))                     # plain JSON
    assert results["summary"] == {"ERROR": 1, "WARNING": 0, "INFO": 0}
    [issue] = results["issues"]
    assert issue["code"] == "text_overflow" and issue["boxes"]["text"] and "refs" not in issue
    text = format_report(results)
    assert text.startswith("Layout validation: 1 error(s)")
    assert "ERROR   [text_overflow]" in text and f"line {issue['line']}" in text


# --------------------------------------------------------------- generator

OVERFLOW_LESSON = textwrap.dedent('''
    from manim import *
    from src.animation import LMSScene

    class LayoutLesson(LMSScene):
        default_voice = "teacher_a"

        def construct(self):
            self.scene_start("cards")
            card = RoundedRectangle(width=2.0, height=1.0)
            label = Text("MEMBER FUNCTIONS", font_size=30).move_to(card)
            n = self.narrate("cards_01", "Here is a card.")
            self.play_with(n, FadeIn(VGroup(card, label)))
''')

FIT_LESSON = textwrap.dedent('''
    from manim import *
    from src.animation import LMSScene

    class FitLesson(LMSScene):
        default_voice = "teacher_a"

        def construct(self):
            self.scene_start("cards")
            card = RoundedRectangle(width=3.0, height=1.0)
            label = Text("A long label for a small card", font_size=36).move_to(card)
            self.validator.check_fit(label, card, margin=0.1)
            n = self.narrate("cards_01", "Here is a card.")
            self.play_with(n, FadeIn(VGroup(card, label)))
''')


@pytest.fixture
def make_lesson(tmp_path):
    made = []

    def make(source):
        folder = tmp_path / f"layout_{uuid.uuid4().hex[:8]}"
        folder.mkdir()
        (folder / "animation.py").write_text(source, encoding="utf-8")
        made.append(folder)
        return folder

    yield make
    for folder in made:
        shutil.rmtree(MEDIA_DIR / f"{folder.name}_narrated", ignore_errors=True)


def test_generator_stops_before_tts_on_layout_errors_when_configured(make_lesson, voices, tone_engine, tmp_path):
    gen = make_generator(make_lesson(OVERFLOW_LESSON), voices, tone_engine, tmp_path / "cache")
    gen.settings = deep_merge(gen.settings, {"validation": {"fail_on_error": True}})
    with pytest.raises(LMSError) as err:
        gen.run()
    assert "Layout validation found 1 error(s)" in err.value.message
    assert 'label (Text "MEMBER FUNCTIONS") overflows its box card (RoundedRectangle)' in err.value.message
    assert "scene 'cards'" in err.value.message and err.value.line == 13
    assert tone_engine.calls == []                                    # nothing synthesised, nothing rendered


def test_generator_reports_layout_errors_as_warnings_by_default(make_lesson, voices, tone_engine, tmp_path):
    lesson = make_lesson(OVERFLOW_LESSON)
    gen = make_generator(lesson, voices, tone_engine, tmp_path / "cache", audio=False)
    events = []
    gen.progress = events.append
    report = gen.run()
    assert any(w.startswith("Layout ERROR:") and "MEMBER FUNCTIONS" in w for w in report.warnings)
    metadata = json.loads((lesson / "generated" / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["layout_validation"]["summary"]["ERROR"] == 1
    [event] = [e for e in events if e["kind"] == "validation"]
    assert event["issues"][0]["code"] == "text_overflow"


def test_check_fit_in_animation_py_fits_the_rendered_text(make_lesson, voices, tone_engine, tmp_path):
    lesson = make_lesson(FIT_LESSON)
    gen = make_generator(lesson, voices, tone_engine, tmp_path / "cache", audio=False)
    report = gen.run()
    assert report.outputs["video"]
    assert [i["code"] for i in report.layout["issues"]] == ["auto_fit"]
    assert not any("Layout ERROR" in w for w in report.warnings)
    assert gen._validation_key()               # auto-fit settings are part of this lesson's render key


def test_lessons_without_problems_report_nothing(make_lesson, voices, tone_engine, tmp_path):
    from tests.test_pipeline import LESSON

    gen = make_generator(make_lesson(LESSON), voices, tone_engine, tmp_path / "cache", audio=False)
    report = gen.run()
    assert report.layout["issues"] == [] and gen._validation_key() == {}
