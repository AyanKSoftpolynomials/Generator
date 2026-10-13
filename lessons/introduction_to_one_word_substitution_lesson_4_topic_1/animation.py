"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 4 - One-Word Substitution
Video  : 01 - Introduction to One-Word Substitution (Video 1 of 6)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 4 - One-Word Substitution\\01 - Introduction to One-Word Substitution.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

First video of Lesson 4: the intro recaps Lessons 1-3 (words to phrases) and announces the new lesson.
The hook's language family lives in FAMILY as (category, core idea, qualifier); first_fail(word, definition) computes which condition each option breaks, and that drives the analogy filter and the Hook, Solved strike reasons.
The "definition = conditions" card (category, core, qualifier, pass all) stays pinned top-right through the worked examples and Hook, Solved.
"""

import math

import numpy as np
from manim import *

from src.animation import LMSScene

# ============================================================== style ====

BG = "#0B1020"
INK = "#E6EAF2"
MUTED = "#8B95A7"
PANEL = "#151C2E"
CELL = "#1B2440"

TERM = INK             # series terms
DIFF = "#4FC3F7"       # first differences
SECOND = "#CE93D8"     # second differences / pattern of the differences
RATIO = "#FFB74D"      # ratios (the next topic's tool)
FOCUS = "#FFD54F"      # "look here" / predicted value
GOOD = "#66BB6A"       # confirmed answer
BAD = "#EF5350"        # wrong / trap

FONT = "Segoe UI"
MIN_FONT = 22          # readable floor: text is never shrunk below this
TITLE = 46
BODY = 30
LABEL = 28
SMALL = 24

# ============================================================= layout ====

FRAME_W = config.frame_width
FRAME_H = config.frame_height
SAFE = 0.45                                   # margin kept clear on every side
SAFE_W = FRAME_W - 2 * SAFE
SAFE_H = FRAME_H - 2 * SAFE

ZONE_W = 6.2                                  # width of each half-screen zone
LEFT_ZONE = LEFT * 3.35                       # centre of the left half
RIGHT_ZONE = RIGHT * 3.35                     # centre of the right half
TOP_Y = FRAME_H / 2 - SAFE - 0.9              # first row under the top edge
BOTTOM_Y = -FRAME_H / 2 + SAFE + 0.45         # caption / tracker row

CARD_TOP = FRAME_H / 2 - SAFE - 0.2           # top edge of a question card


# ======================================================= text helpers ====

def text(s, size=BODY, color=INK, weight=NORMAL, t2c=None):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight, t2c=t2c or {})


def fit_width(mob, max_width):
    """Scale ``mob`` down (never up) to at most ``max_width``."""
    if mob.width > max_width:
        mob.scale_to_fit_width(max_width)
    return mob


def fit_height(mob, max_height):
    """Scale ``mob`` down (never up) to at most ``max_height``."""
    if mob.height > max_height:
        mob.scale_to_fit_height(max_height)
    return mob


def fit_within(mob, max_width, max_height):
    return fit_height(fit_width(mob, max_width), max_height)


def wrap_words(s, max_chars):
    """Greedy word wrap into lines of at most ``max_chars`` characters."""
    lines, line = [], ""
    for word in s.split():
        if line and len(line) + 1 + len(word) > max_chars:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    lines.append(line)
    return "\n".join(lines)


def wrap_lines(s, n_lines):
    """Wrap ``s`` into at most ``n_lines`` lines that are as even as possible."""
    for max_chars in range(math.ceil(len(s) / n_lines), len(s) + 1):
        wrapped = wrap_words(s, max_chars)
        if wrapped.count("\n") < n_lines:
            return wrapped
    return s


def fitted_text(s, max_width, size=BODY, color=INK, weight=NORMAL, max_lines=3, t2c=None):
    """Readable text no wider than ``max_width`` (never below MIN_FONT)."""
    floor = max(MIN_FONT, 0.85 * size)
    for lines in range(1, max_lines + 1):
        body = s if lines == 1 else wrap_lines(s, lines)
        mob = text(body, size, color, weight, t2c)
        if mob.width <= max_width:
            return mob
        if size * max_width / mob.width >= floor:
            return mob.scale(max_width / mob.width)
        floor = MIN_FONT
    if size * max_width / mob.width >= MIN_FONT:
        return mob.scale(max_width / mob.width)
    raise ValueError(f"Text {s!r} cannot fit {max_width:.2f} units at a readable size; "
                     "shorten it or give it a wider container.")


def pill(label, color=FOCUS, size=SMALL, fill_opacity=0.14):
    """Short keyword tag. The box is sized from the text, so text cannot escape."""
    t = text(label, size, color, BOLD)
    box = RoundedRectangle(corner_radius=(t.height + 0.26) / 2, width=t.width + 0.5, height=t.height + 0.26,
                           stroke_color=color, stroke_width=2, fill_color=color, fill_opacity=fill_opacity)
    t.move_to(box)
    return VGroup(box, t)



# ================================================== vocabulary helpers ====

WORD = "#4FC3F7"          # the question word
OPTION = INK              # option text
TRAP = BAD                # eliminated options
KEY = GOOD                # the answer
STEP_COLS = {"READ": "#4FC3F7", "PREDICT": "#CE93D8", "ELIMINATE": "#EF5350", "CONFIRM": "#66BB6A"}


def process_strip(size=LABEL):
    """READ → PREDICT → ELIMINATE → CONFIRM as four chips."""
    parts = []
    for i, (name, col) in enumerate(STEP_COLS.items()):
        if i:
            parts.append(text("→", size, MUTED))
        parts.append(pill(name, col, size=size))
    return VGroup(*parts).arrange(RIGHT, buff=0.2)


def step_chip(strip, name):
    """The chip for one step inside a process strip."""
    return strip[2 * list(STEP_COLS).index(name)]


class OptionQuestion:
    """WORD: (a) … (b) … (c) … (d) …, with elimination and confirmation effects.
    ``key`` is the letter of the answer; ``traps`` maps letters to the reason
    each wrong option is removed."""

    def __init__(self, word, options, key, traps, width=6.0, word_size=TITLE):
        assert key in "abcd"[:len(options)] and set(traps) | {key} == set("abcd"[:len(options)])
        self.key, self.traps = key, traps
        self.word = pill(word, WORD, size=word_size)
        self.rows = VGroup(*[VGroup(text(f"({l})", LABEL, MUTED), fitted_text(o, width - 1.0, BODY, OPTION))
                             .arrange(RIGHT, buff=0.25) for l, o in zip("abcd", options)])
        self.rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        self.group = VGroup(self.word, self.rows).arrange(DOWN, buff=0.45, aligned_edge=LEFT)

    def row(self, letter):
        return self.rows["abcd".index(letter)]

    def strike(self, letter, reason_color=TRAP):
        """Animations: strike through a wrong option, dim it, and tag the reason."""
        r = self.row(letter)
        line = Line(r.get_left() + LEFT * 0.05, r.get_right() + RIGHT * 0.05, color=TRAP, stroke_width=3)
        tag = pill(self.traps[letter], reason_color, size=SMALL).next_to(r, RIGHT, buff=0.35)
        return VGroup(line, tag), [Create(line), r.animate.set_opacity(0.4), FadeIn(tag, shift=LEFT * 0.1)]

    def confirm(self):
        r = self.row(self.key)
        box = SurroundingRectangle(r, color=KEY, buff=0.12, corner_radius=0.1)
        return box, [Create(box), r[1].animate.set_color(KEY)]


def meaning_circles(words, centres, radii, colors, label_size=LABEL):
    """Each word's meaning as a translucent circle with its label inside."""
    out = VGroup()
    for w, c, r, col in zip(words, centres, radii, colors):
        circ = Circle(radius=r, color=col, stroke_width=3, fill_color=col, fill_opacity=0.15).move_to(c)
        out.add(VGroup(circ, text(w, label_size, col, BOLD).move_to(c)))
    return out


def pair_chip(a, b, color, note=None, size=LABEL):
    """'a ≈ b' chip, optionally with a small note underneath."""
    chip = pill(f"{a}  ≈  {b}", color, size=size)
    if note:
        return VGroup(chip, text(note, SMALL, MUTED)).arrange(DOWN, buff=0.12)
    return chip


# ============================================================= lesson ====

CONDITIONS = ("CATEGORY", "CORE", "QUALIFIER")
COND_COL = dict(zip(CONDITIONS, [WORD, RATIO, SECOND]))

# word -> (category, core idea, qualifier): the "language family" from the hook.
FAMILY = {
    "linguist": ("person", "studies languages", None),
    "polyglot": ("person", "speaks languages", "many"),
    "translator": ("person", "converts between languages", None),
    "bilingual": ("person", "speaks languages", "two"),
}
HOOK_DEFINITION = ("person", "speaks languages", "two")


def first_fail(word, definition):
    """The first condition of the definition that the word breaks: (name, what the word has), or None."""
    for name, want, have in zip(CONDITIONS, definition, FAMILY[word]):
        if want != have:
            return name, have
    return None


assert [w for w in FAMILY if first_fail(w, HOOK_DEFINITION) is None] == ["bilingual"]


class IntroductionToOneWordSubstitutionVideo(LMSScene):
    lesson_title = "Introduction to One-Word Substitution"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_atheist()
        self.example_bibliography()
        self.example_acrophobia()
        self.rules()
        self.process()
        self.hook_solved()
        self.exam_patterns()
        self.common_mistakes()
        self.practice()
        self.answers()
        self.recap()
        self.next_video()

    # ---------------------------------------------------- scene helpers --

    def clear_stage(self, run_time=0.6):
        """Scene transition: fade out everything on screen."""
        if self.mobjects:
            self.play(FadeOut(Group(*self.mobjects)), run_time=run_time)

    def card(self, content, width=None, height=None, color=MUTED, pad=0.3):
        """Container-aware card (grows to content; a fixed height is a minimum)."""
        # A fixed height is a minimum: the card grows to its content and never
        # shrinks text (shrinking pushed labels below the readable minimum).
        if width is not None:
            fit_width(content, width - 2 * pad)
        w = width if width is not None else content.width + 2 * pad
        h = max(height or 0, content.height + 2 * pad)
        box = RoundedRectangle(corner_radius=0.18, width=w, height=h, stroke_color=color,
                               stroke_width=2.5, fill_color=PANEL, fill_opacity=1)
        box.move_to(content)
        self.validator.check_fit(content, box, margin=0.1)
        return VGroup(box, content)

    def caption(self, s, color=INK):
        """One-line keyword caption in a fixed-width bar at the bottom of the frame."""
        t = fitted_text(s, SAFE_W - 1.0, BODY, color)
        bar = self.card(t, width=SAFE_W - 0.4, height=t.height + 0.9)
        return bar.move_to(UP * BOTTOM_Y)

    def breadcrumb(self, *parts):
        """Silent 'where are we' trail: Module > Lesson > Topic."""
        colors = [DIFF, "#F48FB1", RATIO]
        items = []
        for i, p in enumerate(parts):
            if i:
                items.append(text("›", LABEL, MUTED))
            items.append(pill(p, colors[i % 3], size=SMALL))
        return fit_width(VGroup(*items).arrange(RIGHT, buff=0.25), SAFE_W)

    def verdict_card(self, good, s, width):
        """A ✓ (green) or ✗ (red) card with fitted text."""
        color = GOOD if good else BAD
        body = VGroup(text("✓" if good else "✗", 34, color, BOLD),
                      fitted_text(s, width - 1.3, SMALL, color, max_lines=2)).arrange(RIGHT, buff=0.25)
        return self.card(body, width=width, height=1.2, color=color)

    def countdown(self, seconds):
        """Thinking-time ring that empties over ``seconds`` (for pause_after)."""
        centre = RIGHT * (FRAME_W / 2 - SAFE - 0.5) + DOWN * (FRAME_H / 2 - SAFE - 0.5)
        tracker = ValueTracker(1.0)
        track = Circle(radius=0.38, stroke_color=MUTED, stroke_width=3).move_to(centre)
        ring = always_redraw(lambda: Arc(radius=0.38, start_angle=PI / 2, angle=max(TAU * tracker.get_value(), 1e-3),
                                         arc_center=centre, stroke_color=FOCUS, stroke_width=8))
        label = pill("Think", FOCUS).next_to(track, LEFT, buff=0.3)
        self.play(FadeIn(track), FadeIn(label), run_time=0.3)
        self.add(ring)
        self.play(tracker.animate.set_value(0.0), run_time=max(0.5, seconds - 0.3), rate_func=linear)
        self.remove(ring)
        self.play(FadeOut(track), FadeOut(label), run_time=0.3)

    def table_rows(self, header, rows, widths, size=SMALL):
        """A small table as a VGroup of rows (header first). Each cell is fitted
        to its column and left-aligned at the column's left edge."""
        lefts, x = [], -sum(widths) / 2
        for w in widths:
            lefts.append(x)
            x += w
        out = VGroup()
        for i, cells in enumerate([header] + rows):
            color, weight = (FOCUS, BOLD) if i == 0 else (INK, NORMAL)
            row = VGroup(*[fitted_text(c, w - 0.3, size, color, weight, max_lines=2) for c, w in zip(cells, widths)])
            for cell, left in zip(row, lefts):
                cell.set_x(left + cell.width / 2)
            out.add(row)
        out.arrange(DOWN, buff=0.3)
        for row in out:                      # arrange() recentres rows; restore column alignment
            for cell, left in zip(row, lefts):
                cell.set_x(left + cell.width / 2)
        return out

    def recap_card(self, title, rows):
        """'Recap Card': term on the left, one-line meaning on the right."""
        table = self.table_rows([title, "what it means"], rows, [3.4, 8.0], size=LABEL)
        table[0][0].set_color(INK)
        card = self.card(table, width=SAFE_W - 0.4)
        return card, table

    def no_overlap(self, *mobs, gap=0.05):
        """Layout guard: the bounding boxes of the given blocks must not intersect
        (checked before anything is played, so a layout change can't silently overlap)."""
        for i, a in enumerate(mobs):
            for b in mobs[i + 1:]:
                apart_x = a.get_right()[0] + gap <= b.get_left()[0] or b.get_right()[0] + gap <= a.get_left()[0]
                apart_y = a.get_bottom()[1] >= b.get_top()[1] + gap or b.get_bottom()[1] >= a.get_top()[1] + gap
                if not (apart_x or apart_y):
                    raise ValueError(f"overlapping blocks: {a.__class__.__name__} at {a.get_center()} and "
                                     f"{b.__class__.__name__} at {b.get_center()}")

    # ----------------------------------------------------- pinned panel --
    PIN_W = 3.4                                   # width of the pinned reference panel

    def pin(self, card, corner=UR):
        """Animation: park a reference card in a corner. It stays on screen across scenes
        (``clear_stage`` leaves it) until ``unpin``."""
        fit_within(card, self.PIN_W, SAFE_H - 1.0)
        card.to_corner(corner, buff=SAFE)
        self.pinned = card
        return FadeIn(card, shift=LEFT * 0.2)

    def unpin(self):
        card, self.pinned = getattr(self, "pinned", None), None
        return FadeOut(card) if card is not None else Wait(0.01)

    def free_area(self):
        """(centre_x, width) of the stage left free by the pinned panel (full safe width if none)."""
        card = getattr(self, "pinned", None)
        left = -FRAME_W / 2 + SAFE
        right = (card.get_left()[0] - 0.3) if card is not None else FRAME_W / 2 - SAFE
        return (left + right) / 2, right - left

    def place_free(self, mob, y=None):
        """Fit ``mob`` into the free area (beside the pinned panel) and centre it there."""
        cx, w = self.free_area()
        fit_width(mob, w)
        mob.set_x(cx)
        if y is not None:
            mob.set_y(y)
        if getattr(self, "pinned", None) is not None:
            self.no_overlap(mob, self.pinned)
        return mob

    def clear_stage(self, run_time=0.6):
        """Scene transition: fade out everything except the pinned panel."""
        keep = getattr(self, "pinned", None)
        mobs = [m for m in self.mobjects if m is not keep]
        if mobs:
            self.play(FadeOut(Group(*mobs)), run_time=run_time)

    def steps_pin(self, title, steps):
        """A compact numbered-steps card for the pinned panel. ``steps`` = [(text, colour), ...]."""
        rows = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), text(t, SMALL, INK)).arrange(RIGHT, buff=0.2)
                        for i, (t, c) in enumerate(steps)]).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        return self.card(VGroup(text(title, SMALL, MUTED, BOLD), rows).arrange(DOWN, buff=0.2, aligned_edge=LEFT),
                         color=FOCUS)

    def pin_step(self, i, color=FOCUS):
        """Animation: light up row i of the pinned steps card."""
        return Indicate(self.pinned[1][1][i], color=color, scale_factor=1.08)

    def condition_pin(self):
        return self.steps_pin("definition = conditions", [("CATEGORY: who / what?", WORD), ("CORE idea", RATIO),
                                                          ("QUALIFIER: two? many?", SECOND),
                                                          ("the word must pass ALL", GOOD)])

    def job_card(self, fill=None):
        head = text("JOB POST  ·  draft", SMALL, RATIO, BOLD)
        s_ = (f"“Wanted: a {fill} support executive.”" if fill
              else "“Wanted: a support executive who can speak two languages fluently.”")
        cx, w = self.free_area()
        line = fitted_text(s_, min(w - 1.4, SAFE_W - 1.8), LABEL, INK, NORMAL, max_lines=2,
                           t2c={fill or "who can speak two languages fluently": GOOD if fill else WORD})
        card = self.card(VGroup(head, line).arrange(DOWN, buff=0.2, aligned_edge=LEFT), width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def condition_chips(self, values, size=SMALL):
        """One chip per condition: CATEGORY / CORE / QUALIFIER with its value."""
        return VGroup(*[VGroup(pill(name, COND_COL[name], size=size), text(str(v), LABEL, INK)).arrange(RIGHT, buff=0.2)
                        for name, v in zip(CONDITIONS, values) if v is not None])

    def condition_example(self, definition, values, word, near, near_meaning):
        """Definition split into conditions, the word that passes them all, and the near-miss."""
        cx, w = self.free_area()
        head = fitted_text(f"“{definition}”", w - 0.8, BODY, INK, NORMAL, max_lines=2)
        chips = self.condition_chips(values).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        answer = VGroup(text("→", BODY, MUTED), pill(word, GOOD, size=BODY)).arrange(RIGHT, buff=0.3)
        miss = text(f"not {near}: {near_meaning}", LABEL, BAD)
        block = VGroup(head, chips, answer, miss).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_height(block, SAFE_H - 1.6)
        self.place_free(block, y=0.1)
        self.no_overlap(head, chips, answer, miss)
        self.validator.check_in_frame(block)
        return head, chips, answer, miss

    # ========================================= 0. LESSON INTRO ==========
    # First video of a NEW LESSON: silent trail, a one-line recap of Lessons 1-3
    # (words → phrases), one line that Lesson 4 starts, the title and objectives.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 4 · One-Word Substitution", "Video 1")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        before = VGroup(text("Lessons 1 to 3", SMALL, MUTED), pill("words", WORD, size=LABEL), text("→", LABEL, MUTED),
                        pill("phrases", SECOND, size=LABEL)).arrange(RIGHT, buff=0.3)
        now = VGroup(text("Lesson 4", SMALL, FOCUS), pill("a whole phrase", SECOND, size=LABEL), text("→", LABEL, MUTED),
                     pill("ONE precise word", GOOD, size=LABEL)).arrange(RIGHT, buff=0.3)
        roots = pill("main tool: the roots on the prerequisite page", RATIO, size=SMALL)
        VGroup(before, now, roots).arrange(DOWN, buff=0.6).move_to(DOWN * 0.1)
        self.no_overlap(crumb, before, now, roots)
        self.validator.check_in_frame(VGroup(crumb, before, now, roots))

        n = self.narrate(
            id="intro_01",
            text="In lessons one to three, you went from words to phrases.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "words")
        self.play(FadeIn(before, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Now we start lesson four, one-word substitution. This lesson goes the other way: from a whole phrase to "
                 "one precise word. The roots on the prerequisite page are your main tool.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "lesson", occurrence=1)
        self.play(Indicate(crumb[2], color="#F48FB1", scale_factor=1.1))
        self.at_word(n, "other")
        self.play(FadeIn(now, shift=UP * 0.1))
        self.at_word(n, "roots")
        self.play(FadeIn(roots, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Introduction to One-Word Substitution", SAFE_W, 64, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=GOOD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [
            ("Explain what one-word substitution tests", WORD),
            ("Match a definition to a word: category, core idea and scope", GOOD),
        ]
        rows = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.4, BODY, INK))
                        .arrange(RIGHT, buff=0.35) for i, (s_, c) in enumerate(goals)])
        rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        heading = text("By the end of this video, you will:", LABEL, MUTED, BOLD)
        objectives = self.card(VGroup(heading, rows).arrange(DOWN, buff=0.4, aligned_edge=LEFT))
        small_title = title.copy().scale(0.6)
        small_title.next_to(crumb, DOWN, buff=0.3)
        objectives.next_to(small_title, DOWN, buff=0.35)
        self.validator.check_in_frame(VGroup(crumb, small_title, objectives))
        n = self.narrate(
            id="intro_03",
            text="This is the introduction to one-word substitution. By the end of this video, you'll be able to explain "
                 "what one-word substitution tests, and match a definition to a word by checking its category, core idea "
                 "and scope.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(before, now, roots), shift=UP * 0.3))
        self.at_word(n, "introduction")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["explain", "match"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK_OPTIONS = ["linguist", "polyglot", "translator", "bilingual"]

    def hook_question(self, word_size=TITLE):
        traps = {}
        for letter, w in zip("abcd", self.HOOK_OPTIONS):
            fail = first_fail(w, HOOK_DEFINITION)
            if fail:
                traps[letter] = f"fails {fail[0]}: {fail[1] or 'a job, not an ability'}"
        key = "abcd"[self.HOOK_OPTIONS.index("bilingual")]
        return OptionQuestion("one word?", self.HOOK_OPTIONS, key, traps, word_size=word_size)

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        job = self.job_card()
        hr = pill("HR:  one word for the highlighted phrase, please", FOCUS, size=LABEL)
        opts = self.hook_question().rows.copy().arrange(RIGHT, buff=0.8)
        fit_width(opts, SAFE_W)
        notes = VGroup(pill("all four are about languages", MUTED, size=SMALL),
                       pill("only ONE matches the definition exactly", GOOD, size=SMALL)).arrange(RIGHT, buff=0.4)
        hr.next_to(job, DOWN, buff=0.5)
        opts.next_to(hr, DOWN, buff=0.6)
        notes.next_to(opts, DOWN, buff=0.6)
        self.no_overlap(job, hr, opts, notes)
        self.validator.check_in_frame(VGroup(job, hr, opts, notes))

        n = self.narrate(
            id="hook_01",
            text="HR is shortening a job post, and wants one word for: a person who can speak two languages fluently. Which "
                 "word goes in the ad?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "shortening")
        self.play(FadeIn(job, shift=DOWN * 0.2))
        self.at_word(n, "one")
        self.play(FadeIn(hr, shift=UP * 0.1))
        self.at_word(n, "Which")
        self.play(Indicate(job[1][1], color=WORD, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Linguist, polyglot, translator, or bilingual? All four are about languages. Only one matches the "
                 "definition exactly.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(opts, ["Linguist", "polyglot", "translator", "bilingual"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.at_word(n, "All")
        self.play(FadeIn(notes[0], shift=UP * 0.1))
        self.at_word(n, "Only")
        self.play(FadeIn(notes[1], shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("one-word substitute:  a descriptive phrase  →  a single precise word", GOOD, size=LABEL)
        fit_width(head, SAFE_W)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        rows = VGroup(*[VGroup(text(f"“{phrase}”", LABEL, INK), text("→", LABEL, MUTED), pill(word, GOOD, size=LABEL))
                        .arrange(RIGHT, buff=0.35) for phrase, word in [
                            ("a person who speaks two languages", "bilingual"),
                            ("a list of books read or referred to", "bibliography"),
                            ("a speech made without preparation", "extempore")]])
        rows.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_width(rows, SAFE_W)
        rows.next_to(head, DOWN, buff=0.7)
        self.no_overlap(head, rows)
        self.validator.check_in_frame(VGroup(head, rows))

        n = self.narrate(
            id="concept_01",
            text="A one-word substitute replaces a descriptive phrase with a single precise word. A person who speaks two "
                 "languages: bilingual. A list of books read or referred to: bibliography. A speech made without "
                 "preparation: extempore.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "replaces")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        for r, (first, word) in zip(rows, [("person", "bilingual"), ("list", "bibliography"), ("speech", "extempore")]):
            self.at_word(n, first)
            self.play(FadeIn(r[0], shift=RIGHT * 0.2), run_time=0.4)
            self.at_word(n, word)
            self.play(FadeIn(r[1:], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        # The same family.
        fam_head = pill("the tricky part: options from the SAME FAMILY", BAD, size=LABEL)
        fam_head.move_to(UP * (CARD_TOP - fam_head.height / 2))
        meanings = {"linguist": "someone who studies languages", "polyglot": "someone who speaks MANY languages",
                    "translator": "someone who converts between languages"}
        fam = VGroup(*[VGroup(pill(w, MUTED, size=LABEL), text(m, LABEL, INK)).arrange(RIGHT, buff=0.35)
                       for w, m in meanings.items()]).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        related = text("all related to “two languages”", LABEL, MUTED)
        only = VGroup(pill("bilingual", GOOD, size=LABEL), text("matches EVERY part of the definition", LABEL, GOOD))\
            .arrange(RIGHT, buff=0.35)
        body = VGroup(fam, related, only).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        fit_within(body, SAFE_W, SAFE_H - fam_head.height - 1.6)
        body.next_to(fam_head, DOWN, buff=0.5)
        self.no_overlap(fam_head, fam, related, only)
        self.validator.check_in_frame(VGroup(fam_head, body))
        n = self.narrate(
            id="concept_02",
            text="What makes these questions tricky is that the options are usually from the same family. For two "
                 "languages, you'll see linguist, someone who studies languages; polyglot, someone who speaks many "
                 "languages; and translator, someone who converts between languages. They're all related. Only one "
                 "matches every part of the definition.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head, rows)))
        self.at_word(n, "family")
        self.play(FadeIn(fam_head, shift=DOWN * 0.2))
        for r, spoken in zip(fam, ["linguist", "polyglot", "translator"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.at_word(n, "related")
        self.play(FadeIn(related, shift=UP * 0.1))
        self.at_word(n, "every")
        self.play(FadeIn(only, shift=UP * 0.1))
        self.wait_for_narration(n)

        # Conditions.
        cond_head = pill("read the definition as a set of CONDITIONS", FOCUS, size=LABEL)
        cond_head.move_to(UP * (CARD_TOP - cond_head.height / 2))
        conds = VGroup(*[VGroup(pill(name, c, size=LABEL), text(q_, LABEL, INK)).arrange(RIGHT, buff=0.35)
                         for name, c, q_ in [("CATEGORY", WORD, "who or what?  a person, a place, a state, an action"),
                                             ("CORE", RATIO, "what is the core idea?"),
                                             ("QUALIFIER", SECOND, "two, many, all, self, without?")]])
        conds.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        every = pill("the answer must satisfy ALL of them", GOOD, size=LABEL)
        cbody = VGroup(conds, every).arrange(DOWN, buff=0.6)
        fit_width(cbody, SAFE_W)
        cbody.next_to(cond_head, DOWN, buff=0.6)
        self.no_overlap(cond_head, conds, every)
        self.validator.check_in_frame(VGroup(cond_head, cbody))
        n = self.narrate(
            id="concept_03",
            text="So read the definition as a set of conditions. Who or what is it: a person, a place, a state, an action? "
                 "What is the core idea? Is there a qualifier: two, many, all, self, without? The answer must satisfy all "
                 "of them.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(fam_head, body)))
        self.at_word(n, "conditions")
        self.play(FadeIn(cond_head, shift=DOWN * 0.2))
        for r, spoken in zip(conds, ["Who", "core", "qualifier"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.at_word(n, "satisfy")
        self.play(FadeIn(every, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        regular = pill("a regular item in C-CAT and placement papers", BAD, size=LABEL)
        vocab = VGroup(*[pill(w, WORD, size=LABEL) for w in ["unanimous", "anonymous", "eligible", "obsolete"]])\
            .arrange(RIGHT, buff=0.4)
        label = text("the precise vocabulary of professional writing", SMALL, MUTED)
        point = pill("precision is the point", GOOD, size=BODY)
        group = VGroup(regular, VGroup(vocab, label).arrange(DOWN, buff=0.2), point).arrange(DOWN, buff=0.7)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="One-word substitution is a regular item in C-CAT and placement papers, and its words are the precise "
                 "vocabulary of professional writing: unanimous, anonymous, eligible, obsolete. Precision is the point.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "regular")
        self.play(FadeIn(regular, shift=DOWN * 0.1))
        self.at_word(n, "vocabulary")
        self.play(FadeIn(label, shift=UP * 0.1))
        for v, spoken in zip(vocab, ["unanimous", "anonymous", "eligible", "obsolete"]):
            self.at_word(n, spoken)
            self.play(FadeIn(v, shift=UP * 0.1), run_time=0.3)
        self.at_word(n, "Precision")
        self.play(FadeIn(point, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        filters = VGroup(*[VGroup(pill(name, c, size=LABEL), text("=  " + v, LABEL, INK)).arrange(RIGHT, buff=0.3)
                           for (name, c), v in zip([("Category", WORD), ("Topic", RATIO), ("Count", SECOND)],
                                                   ["Person", "Languages (speaks)", "Two"])])
        filters.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        panel = self.card(VGroup(text("FILTERS", SMALL, MUTED, BOLD), filters).arrange(DOWN, buff=0.3, aligned_edge=LEFT))
        results = VGroup(*[pill(w, INK, size=LABEL, fill_opacity=0.06) for w in FAMILY]).arrange(DOWN, buff=0.3)
        res = VGroup(text("RESULTS", SMALL, MUTED, BOLD), results).arrange(DOWN, buff=0.3)
        top = VGroup(panel, res).arrange(RIGHT, buff=1.2, aligned_edge=UP)
        same = pill("a definition is a set of filters", FOCUS, size=LABEL)
        block = VGroup(top, same).arrange(DOWN, buff=0.5)
        fit_within(block, SAFE_W, SAFE_H - 1.4)
        block.move_to(UP * 0.3)
        self.no_overlap(panel, res)
        self.no_overlap(top, same)
        self.validator.check_in_frame(block)
        words = list(FAMILY)
        removed_by = {name: [results[i] for i, w in enumerate(words)
                             if (first_fail(w, HOOK_DEFINITION) or (None,))[0] == name] for name in CONDITIONS}
        survivor = results[words.index("bilingual")]

        n = self.narrate(
            id="analogy_01",
            text="Think of an online shopping filter. Category, topic, quantity. Each filter removes results, and only the "
                 "product that passes every filter remains. A definition is a set of filters.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "shopping")
        self.play(FadeIn(panel[0]), FadeIn(panel[1][0]), FadeIn(res, shift=LEFT * 0.2))
        for f, spoken in zip(filters, ["Category", "topic", "quantity"]):
            self.at_word(n, spoken)
            self.play(FadeIn(f, shift=RIGHT * 0.2), run_time=0.35)
        self.at_word(n, "removes")
        self.play(*[m.animate.set_opacity(0.25) for m in removed_by["CORE"]], Indicate(filters[1][0], color=RATIO))
        self.play(*[m.animate.set_opacity(0.25) for m in removed_by["QUALIFIER"]], Indicate(filters[2][0], color=SECOND))
        self.at_word(n, "remains")
        self.play(Indicate(survivor, color=GOOD, scale_factor=1.15))
        self.at_word(n, "definition")
        self.play(FadeIn(same, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_atheist(self):
        self.scene_start("S05_ex_atheist", title="Worked Example 1")
        self.play(self.pin(self.condition_pin()))

        head, chips, answer, miss = self.condition_example(
            "One who does not believe in God", ("a person", "belief in God", "does NOT"), "atheist", "agnostic",
            "someone unsure whether God exists")

        n = self.narrate(
            id="ex1_01",
            text="One who does not believe in God. Category: a person. Core idea: belief in God. Qualifier: does not. "
                 "That's an atheist. Not an agnostic: someone unsure whether God exists.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "believe")
        self.play(FadeIn(head, shift=DOWN * 0.1))
        for chip, (spoken, i) in zip(chips, [("Category", 0), ("Core", 1), ("Qualifier", 2)]):
            self.at_word(n, spoken)
            self.play(FadeIn(chip, shift=RIGHT * 0.2), self.pin_step(i, color=COND_COL[CONDITIONS[i]]), run_time=0.5)
        self.at_word(n, "atheist")
        self.play(FadeIn(answer, scale=1.1), self.pin_step(3, color=GOOD))
        self.at_word(n, "agnostic")
        self.play(FadeIn(miss, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_atheist")

    def example_bibliography(self):
        self.scene_start("S06_ex_bibliography", title="Worked Example 2")

        head, chips, answer, miss = self.condition_example(
            "A list of books referred to", ("a list (a thing)", "books referred to", None), "bibliography", "biography",
            "a life story")

        n = self.narrate(
            id="ex2_01",
            text="A list of books referred to. Category: a list, a thing. Core idea: books referred to. That's a "
                 "bibliography. Not a biography: a life story.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "list", occurrence=1)
        self.play(FadeIn(head, shift=DOWN * 0.1))
        for chip, (spoken, i) in zip(chips, [("Category", 0), ("Core", 1)]):
            self.at_word(n, spoken)
            self.play(FadeIn(chip, shift=RIGHT * 0.2), self.pin_step(i, color=COND_COL[CONDITIONS[i]]), run_time=0.5)
        self.at_word(n, "bibliography")
        self.play(FadeIn(answer, scale=1.1), self.pin_step(3, color=GOOD))
        self.at_word(n, "biography")
        self.play(FadeIn(miss, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_bibliography")

    def example_acrophobia(self):
        self.scene_start("S07_ex_acrophobia", title="Worked Example 3")

        head, chips, answer, miss = self.condition_example(
            "Fear of heights", ("a state: a fear", "heights", None), "acrophobia", "claustrophobia",
            "fear of closed spaces")

        n = self.narrate(
            id="ex3_01",
            text="Fear of heights. Category: a state, a fear. Core idea: heights. That's acrophobia. Not claustrophobia: "
                 "the fear of closed spaces.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Fear", occurrence=1)
        self.play(FadeIn(head, shift=DOWN * 0.1))
        for chip, (spoken, i) in zip(chips, [("Category", 0), ("Core", 1)]):
            self.at_word(n, spoken)
            self.play(FadeIn(chip, shift=RIGHT * 0.2), self.pin_step(i, color=COND_COL[CONDITIONS[i]]), run_time=0.5)
        self.at_word(n, "acrophobia")
        self.play(FadeIn(answer, scale=1.1), self.pin_step(3, color=GOOD))
        self.at_word(n, "claustrophobia")
        self.play(FadeIn(miss, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_acrophobia")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        rules = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Read the definition as conditions: category, core idea, qualifier", WORD),
                             ("The answer must satisfy ALL conditions", GOOD),
                             ("Options from the same family are the main trap", BAD),
                             ("Use roots to decode unknown options", RATIO)])])
        rules.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(rules).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Four rules. First, read the definition as conditions: category, core idea, qualifier. Second, the answer "
                 "must satisfy all conditions. Third, options from the same family are the main trap. And fourth, use "
                 "roots to decode unknown options.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        for r, spoken in zip(rules, ["First", "Second", "Third", "fourth"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_rules")

    # ============================================== 9. PROCESS ==========

    def process(self):
        self.scene_start("S09_process", title="The Process")

        strip = process_strip(BODY)
        fit_width(strip, SAFE_W)
        strip.move_to(UP * (CARD_TOP - strip.height / 2))
        details = VGroup(*[VGroup(pill(name, col, size=SMALL), fitted_text(s_, SAFE_W - 3.4, LABEL, INK))
                           .arrange(RIGHT, buff=0.3) for (name, col), s_ in zip(STEP_COLS.items(), [
                               "split the definition: category, core idea, qualifier",
                               "name the word, or at least its root",
                               "remove options that fail any condition",
                               "read the word back as the definition"])])
        details.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(details)
        board.next_to(strip, DOWN, buff=0.5)
        self.no_overlap(strip, board)
        self.validator.check_in_frame(VGroup(strip, board))

        n = self.narrate(
            id="process_01",
            text="The process. Read: split the definition into category, core idea and qualifier. Predict: name the word, "
                 "or at least its root. Eliminate: remove options that fail any condition. And confirm: read the word "
                 "back as the definition.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(strip, shift=DOWN * 0.2), FadeIn(board[0]))
        for d, name, spoken in zip(details, STEP_COLS, ["Read", "Predict", "Eliminate", "confirm"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(Indicate(step_chip(strip, name)), FadeIn(d, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_process")

    # ========================================== 10. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S10_hook_solved", title="Hook, Solved")
        self.play(self.pin(self.condition_pin()))

        cx, w = self.free_area()
        job = self.job_card()
        chips = self.condition_chips(("a person", "speaks languages fluently", "TWO")).arrange(RIGHT, buff=0.35)
        predict = pill("bi- + lingual", STEP_COLS["PREDICT"], size=SMALL)
        read_row = VGroup(chips, predict).arrange(RIGHT, buff=0.4)
        fit_width(read_row, w - 0.6)
        read_row.next_to(job, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        q = self.hook_question(word_size=LABEL)
        fit_height(q.group, read_row.get_bottom()[1] - 0.3 - (BOTTOM_Y + 0.6))
        q.group.next_to(read_row, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        fixed = self.job_card(fill="bilingual")
        self.no_overlap(job, read_row, q.group)
        self.no_overlap(job, self.pinned)
        self.no_overlap(read_row, self.pinned)
        self.validator.check_in_frame(VGroup(job, read_row, q.group))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read. Category: a person. Core: speaks languages fluently. Qualifier: two. Predict: "
                 "bi, plus lingual.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "solve")
        self.play(FadeIn(job), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(job[1][1], color=WORD, scale_factor=1.03))
        for chip, (spoken, i) in zip(chips, [("Category", 0), ("Core", 1), ("Qualifier", 2)]):
            self.at_word(n, spoken)
            self.play(FadeIn(chip, shift=UP * 0.1), self.pin_step(i, color=COND_COL[CONDITIONS[i]]), run_time=0.5)
        self.at_word(n, "Predict")
        self.play(FadeIn(predict, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. A linguist studies languages. A polyglot speaks many, which fails the two condition. A "
                 "translator is a job, not a speaking ability.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(Indicate(q.rows, color=BAD, scale_factor=1.02))
        for letter, spoken in [("a", "linguist"), ("b", "polyglot"), ("c", "translator")]:
            self.at_word(n, spoken)
            self.play(*q.strike(letter)[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: a bilingual person speaks two languages fluently. That's the answer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(ReplacementTransform(job, fixed), self.pin_step(3, color=GOOD))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_hook_solved")

    # ========================================== 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S11_patterns", title="Exam Patterns and Solving Models")
        self.play(self.unpin())

        table = self.table_rows(["Pattern", "Solving model"], [
            ["Phrase → word", "split into conditions; the answer must pass all of them"],
            ["Underlined phrase in a sentence", "replace it; the word must also fit the grammar"],
            ["Unknown options", "decode roots; eliminate those that break a condition"],
        ], [4.8, 7.0], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. Phrase to word: split into conditions, and the answer must pass all of them. An "
                 "underlined phrase in a sentence: replace it, and the word must also fit the grammar. And unknown "
                 "options: decode the roots, and eliminate those that break a condition.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Phrase", "underlined", "unknown"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_patterns")

    # ======================================== 12. COMMON MISTAKES ==========

    def common_mistakes(self):
        self.scene_start("S12_mistakes", title="Common Mistakes")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "Right family, fails the qualifier: polyglot for “two”", card_w),
             self.verdict_card(True, "Check EVERY condition", card_w)),
            (self.verdict_card(False, "Mixing person, study and place", card_w),
             self.verdict_card(True, "geologist: person;  geology: study", card_w)),
            (self.verdict_card(False, "Guessing without decoding roots", card_w),
             self.verdict_card(True, "Decode the roots first", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is choosing a word from the right family that fails the qualifier, like "
                 "polyglot for two languages. The second is mixing up person, study and place, like geologist and "
                 "geology. The third is guessing without decoding roots.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        for pr, spoken in zip(pairs, ["first", "second", "third"]):
            self.at_word(n, spoken)
            self.play(FadeIn(pr[0], shift=RIGHT * 0.3), FadeIn(pr[1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_mistakes")

    # ============================================== 13. PRACTICE ==========

    PRACTICE = [
        ("A person who cannot read or write", ["illegible", "ignorant", "illiterate", "innocent"], "c",
         "(a) illegible describes handwriting, not a person"),
        ("A speech made without preparation", ["verbatim", "extempore", "monologue", "eulogy"], "b",
         "(a) verbatim means word for word"),
        ("One who is unsure whether God exists", ["agnostic", "atheist", "theist", "heretic"], "a",
         "(b) an atheist denies God; an agnostic is unsure"),
    ]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        head = pill("One word for the phrase?", GOOD, size=LABEL)
        lines = VGroup(*[VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL), text(f"“{phrase}”", LABEL, WORD))
                                .arrange(RIGHT, buff=0.35),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, INK))
                         .arrange(DOWN, buff=0.2, aligned_edge=LEFT)
                         for i, (phrase, opts, *_r) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        board = self.card(VGroup(head, lines).arrange(DOWN, buff=0.4, aligned_edge=LEFT), color=FOCUS)
        fit_within(board, SAFE_W, SAFE_H - 1.2)
        board.move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn. One: a person who cannot read or write. Illegible, ignorant, illiterate, or innocent? Two: a "
                 "speech made without preparation. Verbatim, extempore, monologue, or eulogy? Three: one who is unsure "
                 "whether God exists. Agnostic, atheist, theist, or heretic?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]), FadeIn(head))
        for ln, (spoken, first_option) in zip(lines, [("cannot", "Illegible"), ("speech", "Verbatim"),
                                                     ("unsure", "Agnostic")]):
            self.at_word(n, spoken)
            self.play(FadeIn(ln[0], shift=UP * 0.15), run_time=0.4)
            self.at_word(n, first_option)
            self.play(FadeIn(ln[1], shift=LEFT * 0.15), run_time=0.4)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S13_practice")

    # =============================================== 14. ANSWERS ==========

    def answers(self):
        self.scene_start("S14_answers", title="Answers")

        rows = VGroup(*[VGroup(VGroup(text(f"“{phrase}”", LABEL, INK), text("→", LABEL, MUTED),
                                      pill(f"({key}) {opts['abcd'.index(key)]}", GOOD, size=LABEL))
                               .arrange(RIGHT, buff=0.3), text(why, SMALL, BAD)).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
                        for phrase, opts, key, why in self.PRACTICE])
        rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - 1.2)
        rows.move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: illiterate. Illegible describes handwriting, not a person. Two: extempore. Verbatim means word for "
                 "word. Three: agnostic. An atheist denies God; an agnostic is unsure.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, why) in zip(rows, [("illiterate", "handwriting"), ("extempore", "Verbatim"),
                                           ("agnostic", "denies")]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(r[0], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, why)
            self.play(FadeIn(r[1], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S15_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 1", [
            ["One-word substitution", "a precise word for a phrase"],
            ["Conditions", "category + core idea + qualifier: pass all three"],
            ["Main trap", "same-family words that fail one condition"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. One-word substitution means a precise word for a phrase. Read the conditions: category, core "
                 "idea and qualifier, and pass all three. And the main trap: same-family words that fail one condition.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["precise", "conditions", "trap"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        drawers = VGroup(*[pill(d, c, size=BODY) for d, c in [("people", WORD), ("actions", BAD), ("places", RATIO),
                                                             ("states", SECOND)]]).arrange(RIGHT, buff=0.5)
        freq = pill("the high-frequency substitutes", GOOD, size=LABEL)
        nxt = pill("Next:  Common Substitutions", FOCUS, size=LABEL)
        VGroup(freq, drawers, nxt).arrange(DOWN, buff=0.7).move_to(UP * 0.2)
        self.no_overlap(freq, drawers, nxt)
        self.validator.check_in_frame(VGroup(freq, drawers, nxt))

        n = self.narrate(
            id="next_01",
            text="Video two gives you the high-frequency substitutes, grouped as people, actions, places and states.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.at_word(n, "substitutes")
        self.play(FadeIn(freq, shift=UP * 0.1))
        for d, spoken in zip(drawers, ["people", "actions", "places", "states"]):
            self.at_word(n, spoken)
            self.play(FadeIn(d, shift=UP * 0.1), run_time=0.3)
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")
