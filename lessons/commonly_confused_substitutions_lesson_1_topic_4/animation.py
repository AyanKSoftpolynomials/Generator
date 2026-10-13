"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 4 - One-Word Substitution
Video  : 04 - Commonly Confused Substitutions (Video 4 of 6)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 4 - One-Word Substitution\\04 - Commonly Confused Substitutions.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

The eight confusable groups live in GROUPS (words, separating ideas, kind of difference); group_of / idea_of look a word up, and the rules table, worked examples, hook strike reasons and answers are built from them.
The "what separates them?" card (scope, direction, level) stays pinned top-right through the worked examples and Hook, Solved; the idea in use lights up.
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

BLANK = "______"
KINDS = ["SCOPE", "DIRECTION", "LEVEL"]
KIND_COL = dict(zip(KINDS, [WORD, RATIO, SECOND]))

# The script's Rules table: (words in the group, their separating ideas, kind of difference if the script names one).
GROUPS = [
    (("endemic", "epidemic", "pandemic"), ("local and constant", "regional outbreak", "global"), "SCOPE"),
    (("emigrant", "immigrant"), ("leaves (exits)", "comes in"), "DIRECTION"),
    (("omnipresent", "omniscient", "omnipotent"), ("everywhere", "knows all", "all-powerful"), "SCOPE"),
    (("amateur", "novice"), ("not paid", "beginner"), "LEVEL"),
    (("atheist", "agnostic"), ("denies God", "unsure"), "LEVEL"),
    (("biography", "autobiography"), ("life written by another", "by oneself"), None),
    (("illegible", "ineligible"), ("can't be read", "not qualified"), None),
    (("philanthropist", "misanthrope", "misogynist"), ("loves mankind", "hates mankind", "hates women"), "DIRECTION"),
]


def group_of(word):
    for words, ideas, kind in GROUPS:
        if word in words:
            return words, ideas, kind
    raise KeyError(word)


def idea_of(word):
    words, ideas, _ = group_of(word)
    return ideas[words.index(word)]


assert idea_of("pandemic") == "global" and idea_of("immigrant") == "comes in" and group_of("amateur")[2] == "LEVEL"


class CommonlyConfusedSubstitutionsVideo(LMSScene):
    lesson_title = "Commonly Confused Substitutions"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_emigrant()
        self.example_omnipotent()
        self.example_amateur()
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

    def idea_pin(self):
        return self.steps_pin("what separates them?", [("SCOPE: how far, how many", WORD),
                                                       ("DIRECTION: in or out", RATIO),
                                                       ("LEVEL: unpaid? beginner?", SECOND)])

    def light_kind(self, kind):
        return self.pin_step(KINDS.index(kind), color=KIND_COL[kind])

    def ticker_card(self, fill=None):
        head = text("HEALTH NEWS  ·  ticker", SMALL, RATIO, BOLD)
        s_ = f"“The outbreak has been declared a {fill or BLANK} as cases spread across five continents.”"
        cx, w = self.free_area()
        line = fitted_text(s_, min(w - 1.4, SAFE_W - 1.8), LABEL, INK, NORMAL, max_lines=2,
                           t2c={fill or BLANK: GOOD if fill else FOCUS, "five continents": WORD})
        card = self.card(VGroup(head, line).arrange(DOWN, buff=0.2, aligned_edge=LEFT), width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def confusable_example(self, definition, answer, clue):
        """Definition, the confusable group, the separating idea (lit on the pin) and the answer."""
        words, ideas, kind = group_of(answer)
        cx, w = self.free_area()
        head = fitted_text(f"“{definition}”", w - 0.8, BODY, INK, NORMAL, max_lines=2)
        group = VGroup(*[VGroup(pill(wd, MUTED, size=LABEL), text(idea, SMALL, MUTED)).arrange(DOWN, buff=0.1)
                         for wd, idea in zip(words, ideas)]).arrange(RIGHT, buff=0.35, aligned_edge=UP)
        fit_width(group, w - 0.8)
        idea = VGroup(pill(kind, KIND_COL[kind], size=SMALL), text(clue, LABEL, INK)).arrange(RIGHT, buff=0.25)
        ans = VGroup(text("→", BODY, MUTED), pill(answer, GOOD, size=BODY)).arrange(RIGHT, buff=0.3)
        block = VGroup(head, group, idea, ans).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_height(block, SAFE_H - 1.6)
        self.place_free(block, y=0.1)
        self.no_overlap(head, group, idea, ans)
        self.validator.check_in_frame(block)
        return kind, head, group, idea, ans

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 4 · One-Word Substitution", "Video 4")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        alike = pill("Video 3:  look-alikes like  illegible / ineligible", MUTED, size=LABEL)
        full = pill("today: the full set of confusable groups", BAD, size=LABEL)
        ideas = VGroup(pill("SCOPE", WORD, size=BODY), pill("DIRECTION", RATIO, size=BODY)).arrange(RIGHT, buff=0.6)
        VGroup(alike, full, ideas).arrange(DOWN, buff=0.6).move_to(DOWN * 0.1)
        self.no_overlap(crumb, alike, full, ideas)
        self.validator.check_in_frame(VGroup(crumb, alike, full, ideas))

        n = self.narrate(
            id="intro_01",
            text="Video three showed look-alikes like illegible and ineligible. Today we cover the full set of confusable "
                 "groups, and the two ideas that separate most of them: scope and direction.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "look-alikes")
        self.play(FadeIn(alike, shift=UP * 0.1))
        self.at_word(n, "full")
        self.play(FadeIn(full, shift=UP * 0.1))
        self.at_word(n, "scope")
        self.play(FadeIn(ideas[0], shift=UP * 0.1))
        self.at_word(n, "direction")
        self.play(FadeIn(ideas[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Commonly Confused Substitutions", SAFE_W, 68, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=BAD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Separate the substitute pairs and triplets that exams set as traps", BAD),
                 ("Use scope and direction to tell them apart", GOOD)]
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
            id="intro_02",
            text="This video is commonly confused substitutions. By the end, you'll separate the substitute pairs and "
                 "triplets that exams set as traps, and use scope and direction to tell them apart.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(alike, full, ideas), shift=UP * 0.3))
        self.at_word(n, "commonly")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["separate", "scope"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word=f"declared a {BLANK}", options=["epidemic", "endemic", "sporadic", "pandemic"], key="d",
                traps={"a": "scope: " + idea_of("epidemic"), "b": "scope: " + idea_of("endemic"),
                       "c": "scattered and occasional"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        assert idea_of(h["options"]["abcd".index(h["key"])]) == "global"
        ticker = self.ticker_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.8)
        fit_width(opts, SAFE_W)
        ask = pill("which word is correct?", FOCUS, size=LABEL)
        ask.next_to(ticker, DOWN, buff=0.6)
        opts.next_to(ask, DOWN, buff=0.7)
        self.no_overlap(ticker, ask, opts)
        self.validator.check_in_frame(VGroup(ticker, ask, opts))

        n = self.narrate(
            id="hook_01",
            text="A health news ticker says: The outbreak has been declared a, blank, as cases spread across five "
                 "continents.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ticker")
        self.play(FadeIn(ticker[0]), FadeIn(ticker[1][0]))
        self.at_word(n, "outbreak")
        self.play(FadeIn(ticker[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Which word is correct: epidemic, endemic, sporadic, or pandemic?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "Which")
        self.play(FadeIn(ask, shift=UP * 0.1))
        for row, spoken in zip(opts, ["epidemic", "endemic", "sporadic", "pandemic"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        heads = VGroup(*[VGroup(pill(k, KIND_COL[k], size=BODY), text(sub, SMALL, MUTED)).arrange(DOWN, buff=0.12)
                         for k, sub in zip(KINDS, ["how far, or how many", "in or out, for or against",
                                                   "what kind of person"])]).arrange(RIGHT, buff=0.7, aligned_edge=UP)
        fit_width(heads, SAFE_W)
        heads.move_to(UP * (CARD_TOP - heads.height / 2))
        self.validator.check_in_frame(heads)

        def below(mob):
            fit_within(mob, SAFE_W, SAFE_H - heads.height - 1.6)
            mob.next_to(heads, DOWN, buff=0.6)
            self.no_overlap(heads, mob)
            self.validator.check_in_frame(VGroup(heads, mob))
            return mob

        def rows_for(words, extra=None):
            return VGroup(*[VGroup(pill(w, WORD, size=LABEL), text((extra or {}).get(w, idea_of(w)), LABEL, INK))
                            .arrange(RIGHT, buff=0.35) for w in words]).arrange(DOWN, buff=0.28, aligned_edge=LEFT)

        n = self.narrate(
            id="concept_01",
            text="Most confusable substitutes differ in scope, how far or how many, or in direction: in or out, for or "
                 "against.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "scope")
        self.play(FadeIn(heads[0], shift=DOWN * 0.2))
        self.at_word(n, "direction")
        self.play(FadeIn(heads[1], shift=DOWN * 0.2))
        self.wait_for_narration(n)

        # Scope.
        scope = below(VGroup(rows_for(["endemic", "epidemic", "pandemic"],
                                      {"endemic": "always present in one region",
                                       "epidemic": "a sudden spread in a community or region",
                                       "pandemic": "across countries or continents"}),
                             rows_for(["omnipresent", "omniscient", "omnipotent"],
                                      {"omnipresent": "everywhere", "omniscient": "knows everything"}))
                      .arrange(RIGHT, buff=0.9, aligned_edge=UP))
        n = self.narrate(
            id="concept_02",
            text="Scope. Endemic: always present in one region. Epidemic: a sudden spread in a community or region. "
                 "Pandemic: across countries or continents. The omni words work the same way: omnipresent, everywhere; "
                 "omniscient, knows everything; omnipotent, all-powerful.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Scope")
        self.play(Indicate(heads[0][0], color=WORD, scale_factor=1.1))
        for r, spoken in zip(list(scope[0]) + list(scope[1]), ["Endemic", "Epidemic", "Pandemic", "omnipresent",
                                                               "omniscient", "omnipotent"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        # Direction.
        direction = below(rows_for(["emigrant", "immigrant", "philanthropist", "misanthrope"],
                                   {"emigrant": "leaves a country:  E for Exits", "immigrant": "comes in:  I for In"}))
        n = self.narrate(
            id="concept_03",
            text="Direction. An emigrant leaves a country: E for exits. An immigrant comes in: I for in. A philanthropist "
                 "loves mankind; a misanthrope hates mankind.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(scope))
        self.at_word(n, "Direction")
        self.play(Indicate(heads[1][0], color=RATIO, scale_factor=1.1))
        for r, spoken in zip(direction, ["emigrant", "immigrant", "philanthropist", "misanthrope"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        # Level.
        level = below(rows_for(["amateur", "novice", "atheist", "agnostic"],
                               {"amateur": "does it for pleasure, not money", "novice": "a beginner"}))
        n = self.narrate(
            id="concept_04",
            text="Level. An amateur does it for pleasure, not money; a novice is a beginner. An atheist denies God; an "
                 "agnostic is unsure.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(direction))
        self.at_word(n, "Level")
        self.play(FadeIn(heads[2], shift=DOWN * 0.2))
        for r, spoken in zip(level, ["amateur", "novice", "atheist", "agnostic"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        built = pill("the options are almost always built from the confusable group itself", BAD, size=LABEL)
        opts = VGroup(*[pill(f"({l}) {w}", MUTED, size=SMALL) for l, w in zip("abc", GROUPS[0][0])])\
            .arrange(RIGHT, buff=0.3)
        fast = pill("know the separating idea  →  the question takes seconds", GOOD, size=LABEL)
        group = VGroup(built, opts, fast).arrange(DOWN, buff=0.6)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(built, opts, fast)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="Exam options for these questions are almost always built from the confusable group itself. If you know "
                 "the separating idea, the question takes seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "built")
        self.play(FadeIn(built, shift=DOWN * 0.1))
        self.at_word(n, "group")
        self.play(LaggedStart(*[FadeIn(o, shift=UP * 0.1) for o in opts], lag_ratio=0.25))
        self.at_word(n, "separating")
        self.play(FadeIn(fast, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        xs = [-4.2, 0.0, 4.2]
        track = Line(RIGHT * xs[0] + DOWN * 0.4, RIGHT * xs[2] + DOWN * 0.4, color=MUTED, stroke_width=6)
        knob = Dot(track.get_start(), radius=0.16, color=FOCUS)
        views = VGroup(*[Circle(radius=r, color=c, stroke_width=4, fill_color=c, fill_opacity=0.15)
                         .move_to(RIGHT * x + UP * 1.5) for x, r, c in zip(xs, [0.35, 0.7, 1.05], [GOOD, RATIO, BAD])])
        names = VGroup(*[text(t, SMALL, MUTED).next_to(v, UP, buff=0.12)
                         for v, t in zip(views, ["street view", "city", "globe"])])
        stops = VGroup(*[VGroup(pill(w, c, size=LABEL), text(note, SMALL, INK)).arrange(DOWN, buff=0.12)
                         .move_to(RIGHT * x + DOWN * 1.4)
                         for x, w, c, note in zip(xs, GROUPS[0][0], [GOOD, RATIO, BAD],
                                                  ["always present locally", "a sudden local outbreak",
                                                   "across the globe"])])
        zoom = pill("the words differ in how far you've zoomed out", FOCUS, size=SMALL)
        zoom.next_to(stops, DOWN, buff=0.35)
        self.no_overlap(*stops)
        self.no_overlap(VGroup(views, names), VGroup(stops), zoom)
        self.validator.check_in_frame(VGroup(views, names, track, stops, zoom))

        n = self.narrate(
            id="analogy_01",
            text="Picture a map zoom slider. Endemic is the street view: always present locally. Epidemic is the city: a "
                 "sudden local outbreak. Pandemic is the globe. The words differ in how far you've zoomed out.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "slider")
        self.play(Create(track), FadeIn(knob))
        for spoken, i in [("Endemic", 0), ("Epidemic", 1), ("Pandemic", 2)]:
            self.at_word(n, spoken)
            self.play(knob.animate.set_x(xs[i]), FadeIn(views[i], scale=0.8), FadeIn(names[i]),
                      FadeIn(stops[i], shift=UP * 0.1), run_time=0.6)
        self.at_word(n, "zoomed")
        self.play(FadeIn(zoom, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_emigrant(self):
        self.scene_start("S05_ex_emigrant", title="Worked Example 1")
        self.play(self.pin(self.idea_pin()))

        kind, head, group, idea, ans = self.confusable_example(
            "One who leaves his country to settle in another", "emigrant", "leaves = OUT:  E for Exits")

        n = self.narrate(
            id="ex1_01",
            text="One who leaves his country to settle in another. The options would be emigrant and immigrant. The "
                 "separating idea is direction: leaves means out. E for exits: emigrant.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "leaves", occurrence=1)
        self.play(FadeIn(head, shift=DOWN * 0.1))
        self.at_word(n, "options")
        self.play(LaggedStart(*[FadeIn(g, shift=UP * 0.1) for g in group], lag_ratio=0.3))
        self.at_word(n, "direction")
        self.play(FadeIn(idea, shift=RIGHT * 0.2), self.light_kind(kind))
        self.at_word(n, "emigrant", occurrence=2)
        self.play(FadeIn(ans, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_emigrant")

    def example_omnipotent(self):
        self.scene_start("S06_ex_omnipotent", title="Worked Example 2")

        kind, head, group, idea, ans = self.confusable_example(
            "One who is all-powerful", "omnipotent", "decode the second half:  potent = powerful")

        n = self.narrate(
            id="ex2_01",
            text="One who is all-powerful. The options would be omnipresent, omniscient and omnipotent. The separating "
                 "idea is scope: decode the second half. Potent means powerful: omnipotent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "all-powerful")
        self.play(FadeIn(head, shift=DOWN * 0.1))
        self.at_word(n, "options")
        self.play(LaggedStart(*[FadeIn(g, shift=UP * 0.1) for g in group], lag_ratio=0.3))
        self.at_word(n, "scope")
        self.play(FadeIn(idea, shift=RIGHT * 0.2), self.light_kind(kind))
        self.at_word(n, "omnipotent", occurrence=2)
        self.play(FadeIn(ans, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_omnipotent")

    def example_amateur(self):
        self.scene_start("S07_ex_amateur", title="Worked Example 3")

        kind, head, group, idea, ans = self.confusable_example(
            "One who plays a sport for pleasure, not money", "amateur", "unpaid, not “beginner”")

        n = self.narrate(
            id="ex3_01",
            text="One who plays a sport for pleasure, not money. The options would be amateur and novice. The separating "
                 "idea is level: unpaid, not beginner. So: amateur, not novice.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sport")
        self.play(FadeIn(head, shift=DOWN * 0.1))
        self.at_word(n, "options")
        self.play(LaggedStart(*[FadeIn(g, shift=UP * 0.1) for g in group], lag_ratio=0.3))
        self.at_word(n, "level")
        self.play(FadeIn(idea, shift=RIGHT * 0.2), self.light_kind(kind))
        self.at_word(n, "amateur", occurrence=2)
        self.play(FadeIn(ans, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_amateur")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        table = self.table_rows(["Group", "Separating idea"],
                                [[" / ".join(words), " / ".join(ideas)] for words, ideas, _k in GROUPS], [5.6, 6.4],
                                size=LABEL)
        for row in table[1:]:
            row[0].set_color(WORD)
        board = self.card(table, width=SAFE_W - 0.2)
        fit_height(board, SAFE_H - 1.0)
        board.move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Eight groups to keep apart. Endemic, epidemic, pandemic: local and constant, a regional outbreak, global. "
                 "Emigrant and immigrant: leaves, and comes in. Omnipresent, omniscient, omnipotent: everywhere, knows "
                 "all, all-powerful. Amateur and novice: not paid, and a beginner.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eight")
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:5], ["Endemic", "Emigrant", "Omnipresent", "Amateur"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        n = self.narrate(
            id="rules_02",
            text="Atheist and agnostic: denies God, and unsure. Biography and autobiography: a life written by another, "
                 "and by oneself. Illegible and ineligible: can't be read, and not qualified. Philanthropist, "
                 "misanthrope, misogynist: loves mankind, hates mankind, hates women.",
            voice="default",
            subtitle=True,
        )
        for row, spoken in zip(table[5:], ["Atheist", "Biography", "Illegible", "Philanthropist"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_rules")

    # ============================================== 9. PROCESS ==========

    def process(self):
        self.scene_start("S09_process", title="The Process")

        steps = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Identify the group the options belong to", WORD),
                             ("Recall the separating idea: scope, direction or level", RATIO),
                             ("Match the definition's qualifier to it", SECOND),
                             ("Confirm", GOOD)])])
        steps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="process_01",
            text="The process. First, identify the group the options belong to. Second, recall the separating idea: scope, "
                 "direction or level. Third, match the definition's qualifier to it. And fourth, confirm.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        for r, spoken in zip(steps, ["First", "Second", "Third", "fourth"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_process")

    # ========================================== 10. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S10_hook_solved", title="Hook, Solved")
        self.play(self.pin(self.idea_pin()))

        h = self.HOOK
        cx, w = self.free_area()
        ticker = self.ticker_card()
        notes = VGroup(VGroup(pill("SCOPE", WORD, size=SMALL), text("five continents = " + idea_of("pandemic"), LABEL, INK))
                       .arrange(RIGHT, buff=0.2), pill("pan- = all  →  pandemic", STEP_COLS["PREDICT"], size=SMALL))\
            .arrange(RIGHT, buff=0.4)
        fit_width(notes, w - 0.6)
        notes.next_to(ticker, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=LABEL)
        fit_height(q.group, notes.get_bottom()[1] - 0.3 - (BOTTOM_Y + 0.6))
        q.group.next_to(notes, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        fixed = self.ticker_card(fill="pandemic")
        self.no_overlap(ticker, notes, q.group)
        self.no_overlap(ticker, self.pinned)
        self.no_overlap(notes, self.pinned)
        self.validator.check_in_frame(VGroup(ticker, notes, q.group))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: an outbreak spreading across five continents. The qualifier is scope: "
                 "global. Predict: pan means all, so pandemic.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(ticker), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(ticker[1][1], color=WORD, scale_factor=1.02))
        self.at_word(n, "scope")
        self.play(FadeIn(notes[0], shift=UP * 0.1), self.light_kind("SCOPE"))
        self.at_word(n, "Predict")
        self.play(FadeIn(notes[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. An epidemic is regional. Endemic means constant in one area. Sporadic means scattered and "
                 "occasional.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(Indicate(q.rows, color=BAD, scale_factor=1.02))
        for letter, spoken in [("a", "epidemic"), ("b", "Endemic"), ("c", "Sporadic")]:
            self.at_word(n, spoken)
            self.play(*q.strike(letter)[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: the outbreak has been declared a pandemic. That's the answer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(ReplacementTransform(ticker, fixed))
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
            ["Options from one group", "find the separating idea; match the qualifier"],
            ["Direction words", "e- = out,  im- = in"],
            ["omni- triplet", "decode the second half: present, science (knowledge), potent"],
        ], [4.6, 7.2], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. Options from one group: find the separating idea, and match the qualifier. "
                 "Direction words: E means out, and im means in. And the omni triplet: decode the second half: present, "
                 "science for knowledge, and potent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Options", "Direction", "omni"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_patterns")

    # ======================================== 12. COMMON MISTAKES ==========

    def common_mistakes(self):
        self.scene_start("S12_mistakes", title="Common Mistakes")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "“epidemic” for a global outbreak", card_w),
             self.verdict_card(True, "global = pandemic", card_w)),
            (self.verdict_card(False, "Swapping emigrant and immigrant", card_w),
             self.verdict_card(True, "E exits;  I comes In", card_w)),
            (self.verdict_card(False, "amateur = beginner", card_w),
             self.verdict_card(True, "amateur: unpaid;  novice: beginner", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is using epidemic for a global outbreak. The second is swapping "
                 "emigrant and immigrant. The third is treating amateur as beginner.",
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
        ("A person who comes into a country to settle", ["emigrant", "migrant", "immigrant", "refugee"], "c",
         "in = immigrant"),
        ("One who knows everything", ["omnipresent", "omniscient", "omnipotent", "omnivorous"], "b",
         "scient = knowledge"),
        ("The life story of a person written by himself", ["autobiography", "biography", "memoir", "diary"], "a",
         "auto = self"),
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
            text="Your turn. One: a person who comes into a country to settle. Emigrant, migrant, immigrant, or refugee? "
                 "Two: one who knows everything. Omnipresent, omniscient, omnipotent, or omnivorous? Three: the life story "
                 "of a person, written by himself. Autobiography, biography, memoir, or diary?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]), FadeIn(head))
        for ln, (spoken, first_option) in zip(lines, [("comes", "Emigrant"), ("knows", "Omnipresent"),
                                                     ("story", "Autobiography")]):
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

        rows = VGroup()
        for phrase, opts, key, decode in self.PRACTICE:
            word = opts["abcd".index(key)]
            group_of(word)                                    # every answer belongs to a Rules group
            rows.add(VGroup(text(f"“{phrase}”", LABEL, INK), text("→", LABEL, MUTED),
                            pill(f"({key}) {word}", GOOD, size=LABEL), pill(decode, RATIO, size=SMALL))
                     .arrange(RIGHT, buff=0.3))
        narrower = text("(c) a memoir is related, but narrower", SMALL, BAD)
        rows.arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        block = VGroup(rows, narrower).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        fit_within(block, SAFE_W, SAFE_H - 1.2)
        block.move_to(UP * 0.3)
        self.validator.check_in_frame(block)

        n = self.narrate(
            id="answers_01",
            text="One: immigrant. In means immigrant. Two: omniscient. Scient means knowledge. Three: autobiography. Auto "
                 "means self. A memoir is related, but narrower.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, decode) in zip(rows, [("immigrant", "In"), ("omniscient", "Scient"), ("autobiography", "Auto")]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(r[:3], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, decode)
            self.play(FadeIn(r[3], shift=LEFT * 0.1), run_time=0.4)
        self.at_word(n, "memoir")
        self.play(FadeIn(narrower, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S15_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 4", [
            ["Scope", "endemic < epidemic < pandemic"],
            ["Direction", "emigrant (out) / immigrant (in)"],
            ["omni-", "present / scient (knows) / potent (power)"],
            ["Level", "amateur (unpaid) vs novice (beginner)"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Scope: endemic, then epidemic, then pandemic. Direction: an emigrant goes out, an immigrant "
                 "comes in. The omni words: present, scient for knows, potent for power. And level: an amateur is unpaid, "
                 "a novice is a beginner.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Scope", "Direction", "omni", "level"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        exam = pill("the high-frequency exam list", BAD, size=LABEL)
        decode = pill("with a decode for each word", RATIO, size=LABEL)
        nxt = pill("Next:  Exam-Oriented One-Word Substitutions", FOCUS, size=LABEL)
        VGroup(exam, decode, nxt).arrange(DOWN, buff=0.7).move_to(UP * 0.2)
        self.no_overlap(exam, decode, nxt)
        self.validator.check_in_frame(VGroup(exam, decode, nxt))

        n = self.narrate(
            id="next_01",
            text="Video five gives you the high-frequency exam list, with a decode for each.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.at_word(n, "exam")
        self.play(FadeIn(exam, shift=UP * 0.1))
        self.at_word(n, "decode")
        self.play(FadeIn(decode, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")
