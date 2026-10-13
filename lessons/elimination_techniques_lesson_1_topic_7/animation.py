"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - English
Module : Module 3 - Verbal Ability
Lesson : Lesson 13 - Cloze Test (Fill in the Blanks)
Topic  : Video 7 of 8 - Elimination Techniques (Exam-level, about 5 min)

Source script:
  07 - Elimination Techniques.pdf
  Prose narrated closely; headings become scenes. Blanks are read aloud as
  "blank one", "blank two". Answers checked: hook (b) loyal; worked (2)
  Therefore, (1) inconclusive; practice (c) distrusted, (a) However.

  SCRIPT ISSUE (flagged, minimal fix in narration): Hook, Solved says the
  grammar filter ("a (1) user" needs a consonant-sound adjective) lets all four
  options pass. "Occasional" starts with a vowel sound ("an occasional user"),
  so grammar already removes (c). The narration says so; (c) is eliminated at
  the grammar step, and (d) and (a) at the logic step. Answer unchanged: (b).

Golden-reference pattern: one ``LMSScene`` class, narration as the timeline,
one method per section, zone constants and ``fitted_text`` for all text.

House rules:
  * a visual beat for every meaningful sentence and key word;
  * pinned ELIMINATION ORDER panel (left: grammar, passage logic, precision,
    dependent blanks, skip and return) from The Concept to the recap; each rule
    is added as it is taught and lights up when used;
  * drawn 3D: the three filter layers, the dependent-blank link, the Sudoku
    grid;
  * passages are real cloze cards: blanks are filled in place.

Section map:
  S00 You are here   S01 Hook (customer email)   S02 Objectives   S03 Continuity
  S04 The Concept    S05 Why You Need It   S06 The Analogy (Sudoku)
  S07 Worked Example  S08 Rules  S09 The Process  S10 Hook, Solved
  S11 Exam Patterns  S12 Common Mistakes  S13 Practice  S14 Answers
  S15 Recap and Next
"""

import math
import re

import numpy as np
from manim import *

from src.animation import LMSScene

# ============================================================== style ====

BG = "#0B1020"
INK = "#E6EAF2"
MUTED = "#8B95A7"
PANEL = "#151C2E"
CELL = "#1B2440"
FOCUS = "#FFD54F"      # "look here" / prediction / main idea
GOOD = "#66BB6A"       # correct / confirmed
BAD = "#EF5350"        # trap / eliminated
TURN = "#FF8A65"       # turn words ("However", "But", "Yet")
HINT = "#4FC3F7"       # locating / the passage's evidence
ACCENT = "#BA68C8"     # secondary accent
SOFT = "#F48FB1"       # tertiary accent

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

CARD_TOP = FRAME_H / 2 - SAFE - 0.2           # top edge of a heading card
FLOOR_Y = -FRAME_H / 2 + SAFE + 0.15          # lowest y any content may reach
DEPTH_DIR = np.array([0.5, 0.32, 0.0])        # screen direction of "into the page"

# Pinned reference panel (left) and the stage it leaves free (right).
PANEL_W = 3.6
PANEL_X = -FRAME_W / 2 + SAFE + PANEL_W / 2
PANEL_Y = 0.5
STAGE_LEFT = PANEL_X + PANEL_W / 2 + 0.4
STAGE_RIGHT = FRAME_W / 2 - SAFE
STAGE_W = STAGE_RIGHT - STAGE_LEFT
STAGE_X = (STAGE_LEFT + STAGE_RIGHT) / 2

STEPS = ["READ", "PREDICT", "ELIMINATE", "CONFIRM"]


# ======================================================= text helpers ====

def text(s, size=BODY, color=INK, weight=NORMAL):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight, disable_ligatures=True)


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


def fitted_text(s, max_width, size=BODY, color=INK, weight=NORMAL, max_lines=3):
    """Readable text no wider than ``max_width``.

    Order of preference: as written > slightly smaller (to 85 %) > wrapped
    over more lines > wrapped and smaller (never below MIN_FONT). If none of
    that fits, fail loudly.
    """
    floor = max(MIN_FONT, 0.85 * size)
    for lines in range(1, max_lines + 1):
        body = s if lines == 1 else wrap_lines(s, lines)
        mob = text(body, size, color, weight)
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


def tick_row(s, width, color=GOOD, mark="✓", size=BODY, max_lines=3):
    """A checklist row: mark + fitted text."""
    return VGroup(text(mark, size + 4, color, BOLD),
                  fitted_text(s, width, size, INK, max_lines=max_lines)).arrange(RIGHT, buff=0.3)


def person(color=MUTED, scale=1.0):
    head = Circle(radius=0.2, stroke_color=color, stroke_width=4)
    body = Arc(radius=0.36, start_angle=0, angle=PI, stroke_color=color, stroke_width=4)
    body.next_to(head, DOWN, buff=0.06)
    return VGroup(head, body).scale(scale)


# ================================================== 3D-look helpers ====

def tint(color, amount, towards=BLACK):
    """``color`` moved ``amount`` of the way towards ``towards``."""
    return interpolate_color(ManimColor(color), ManimColor(towards), amount)


class Slab(VGroup):
    """A box drawn with depth: front face, lit top, shaded right side and a
    soft shadow. Labels go on ``front`` so text stays flat and readable."""

    def __init__(self, width, height, color, depth=0.28, fill=PANEL):
        super().__init__()
        d = DEPTH_DIR * depth
        self.front = Rectangle(width=width, height=height, stroke_color=color, stroke_width=2.5,
                               fill_color=fill, fill_opacity=1)
        ul, ur, dr = self.front.get_corner(UL), self.front.get_corner(UR), self.front.get_corner(DR)
        self.top = Polygon(ul, ur, ur + d, ul + d, stroke_color=color, stroke_width=2,
                           fill_color=tint(color, 0.55), fill_opacity=1)
        self.side = Polygon(ur, dr, dr + d, ur + d, stroke_color=color, stroke_width=2,
                            fill_color=tint(color, 0.75), fill_opacity=1)
        self.shadow = Ellipse(width=width + depth * 1.6, height=0.14 + depth * 0.5, stroke_width=0,
                              fill_color=BLACK, fill_opacity=0.45)
        self.shadow.move_to(self.front.get_bottom() + d * 0.5 + DOWN * 0.06)
        self.add(self.shadow, self.side, self.top, self.front)


def slab_tile(label, color, width, height, size=BODY, depth=0.28):
    """A raised tile with a fitted label on its front face."""
    slab = Slab(width, height, color, depth)
    words = fitted_text(label, width - 0.4, size, color, BOLD, max_lines=2).move_to(slab.front)
    g = VGroup(slab, words)
    g.slab, g.words = slab, words
    return g


def glyphs(mob, s, word, occurrence=1):
    """The glyphs of ``word`` inside ``mob``, a Text built from string ``s``.

    Text has no glyphs for spaces or line breaks, so character positions are
    mapped to glyph positions by skipping whitespace.
    """
    idx = -1
    for _ in range(occurrence):
        idx = s.index(word, idx + 1)
    start = len([c for c in s[:idx] if not c.isspace()])
    count = len([c for c in word if not c.isspace()])
    return mob[start:start + count]

# ===================================================== this video ====

CRUMB_MODULE = "Verbal Ability"
CRUMB_TOPIC = "Cloze Test"
LESSON_TAG = "Lesson 13 of 14"
VIDEO_COUNT = 8

GRAM = HINT
LOGIC = ACCENT
PREC = FOCUS
DEP = TURN
SKIP = SOFT

ORDER = [("1  Grammar", GRAM), ("2  Passage logic", LOGIC), ("3  Precision", PREC),
         ("Dependent: certain one first", DEP), ("Unclear: skip and return", SKIP)]

HOOK_PASSAGE = ["I have been a (1) ____ user of your app for five years.",
                "Recently, though, the frequent crashes have made me consider switching."]
HOOK_OPTIONS = ["(a) reluctant", "(b) loyal", "(c) occasional", "(d) former"]

SUDOKU = [[1, 2, 3, 4], [3, 4, 1, 2], [2, 1, 4, 3], [4, 3, 2, 1]]
EASY = [(0, 3), (1, 0), (2, 2)]
HARD = (3, 1)


class ClozeEliminationVideo(LMSScene):
    lesson_title = "Elimination Techniques"

    def construct(self):
        self.camera.background_color = BG
        self.pinned = []
        self.panel = None

        self.you_are_here()
        self.hook()
        self.objectives()
        self.continuity()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.worked_examples()
        self.rules()
        self.process()
        self.hook_solved()
        self.exam_patterns()
        self.common_mistakes()
        self.practice()
        self.answers()
        self.recap()

    # ---------------------------------------------------- scene helpers --

    def clear_stage(self, run_time=0.6):
        """Scene transition: fade out everything except pinned mobjects."""
        keep = set()
        for p in self.pinned:
            keep.update(p.get_family())
        others = [m for m in self.mobjects if m not in keep]
        if others:
            self.play(FadeOut(Group(*others)), run_time=run_time)

    def card(self, content, width=None, height=None, color=MUTED, pad=0.3):
        """Container-aware card (grows to content, or fits content to a fixed width)."""
        if width is not None:
            fit_width(content, width - 2 * pad)
        w = width if width is not None else content.width + 2 * pad
        h = max(height or 0, content.height + 2 * pad)
        box = RoundedRectangle(corner_radius=0.18, width=w, height=h, stroke_color=color,
                               stroke_width=2.5, fill_color=PANEL, fill_opacity=1)
        box.move_to(content)
        self.validator.check_fit(content, box, margin=0.1)
        return VGroup(box, content)

    def stage(self):
        """(centre x, width) of the free area: full frame, or right of the pinned panel."""
        if self.panel is not None and self.panel in self.pinned:
            return STAGE_X, STAGE_W
        return 0.0, SAFE_W

    def heading(self, s, color=FOCUS):
        """A heading card under the top edge of the free area."""
        x, w = self.stage()
        t = fitted_text(s, w - 1.0, BODY, INK, BOLD, max_lines=2)
        c = self.card(t, color=color)
        return c.move_to(RIGHT * x + UP * (CARD_TOP - c.height / 2))

    def caption(self, s, color=INK):
        """A keyword bar on the floor row of the free area."""
        x, w = self.stage()
        t = fitted_text(s, w - 1.0, BODY, color, max_lines=2)
        bar = self.card(t, width=w - 0.2)
        return bar.move_to(RIGHT * x + UP * (FLOOR_Y + bar.height / 2))

    def step_tracker(self, labels=STEPS):
        x, w = self.stage()
        tracker = VGroup(*[pill(f"{i + 1}  {label}", MUTED, SMALL, 0.05)
                           for i, label in enumerate(labels)]).arrange(RIGHT, buff=0.25)
        tracker.move_to(RIGHT * x + UP * (FLOOR_Y + tracker.height / 2))
        return tracker

    def focus_step(self, tracker, index):
        """Light step ``index``, mark earlier steps done, dim later ones."""
        anims = []
        for i, (box, label) in enumerate(tracker):
            color = FOCUS if i == index else GOOD if i < index else MUTED
            opacity = 0.2 if i == index else 0.05
            anims += [box.animate.set_stroke(color).set_fill(color, opacity), label.animate.set_color(color)]
        return AnimationGroup(*anims)

    def countdown(self, seconds, centre):
        """Thinking-time ring that empties over ``seconds`` (for pause_after)."""
        tracker = ValueTracker(1.0)
        track = Circle(radius=0.38, stroke_color=MUTED, stroke_width=3).move_to(centre)
        ring = always_redraw(lambda: Arc(radius=0.38, start_angle=PI / 2, angle=max(TAU * tracker.get_value(), 1e-3),
                                         arc_center=centre, stroke_color=FOCUS, stroke_width=8))
        self.play(FadeIn(track), run_time=0.3)
        self.add(ring)
        self.play(tracker.animate.set_value(0.0), run_time=max(0.5, seconds - 0.3), rate_func=linear)
        self.remove(ring)
        self.play(FadeOut(track), run_time=0.3)

    # ------------------------------------------------ pinned side panel --

    def build_panel(self, title, items, color=MUTED):
        """A docked checklist on the left: ``items`` = [(label, colour)]."""
        rows = VGroup()
        for name, c in items:
            chip = Square(0.26, stroke_width=0, fill_color=c, fill_opacity=0.9)
            label = fitted_text(name, PANEL_W - 1.2, LABEL, c, BOLD, max_lines=2)
            row = VGroup(chip, label).arrange(RIGHT, buff=0.25)
            row.label, row.color = label, c
            rows.add(row)
        rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        content = VGroup(text(title, SMALL, MUTED, BOLD), rows).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        panel = self.card(content, width=PANEL_W, color=color).move_to(RIGHT * PANEL_X + UP * PANEL_Y)
        panel.rows = rows
        return panel

    def dock(self, sources=()):
        """Bring the panel in (``sources`` become its rows) and pin it."""
        anims = [FadeIn(self.panel[0]), FadeIn(self.panel[1][0])]
        if sources:
            anims += [ReplacementTransform(s, r) for s, r in zip(sources, self.panel.rows)]
        else:
            anims.append(LaggedStart(*[FadeIn(r, shift=LEFT * 0.3) for r in self.panel.rows], lag_ratio=0.15))
        self.play(*anims, run_time=1.2)
        self.pinned.append(self.panel)
        self.validator.check_in_frame(self.panel)

    def undock(self):
        """Release the panel (before the recap)."""
        self.pinned.clear()
        self.play(FadeOut(self.panel), run_time=0.6)
        self.panel = None

    def light(self, *ks):
        """Light panel rows ``ks``; dim the others."""
        anims = []
        for i, row in enumerate(self.panel.rows):
            if i in ks:
                row.label.set_color(row.color)
                anims.append(Indicate(row, color=row.color, scale_factor=1.12))
            else:
                anims.append(row.label.animate.set_color(MUTED))
        return AnimationGroup(*anims)

    def all_lit(self):
        return AnimationGroup(*[row.label.animate.set_color(row.color) for row in self.panel.rows])

    # ------------------------------------------------- content builders --

    def intro_parts(self, title_s, video, level, before, nxt, color=FOCUS):
        """Breadcrumb, title, facts and the before/next path for the intro."""
        crumb = VGroup(pill("English", MUTED, SMALL, 0.05), text("›", LABEL, MUTED),
                       pill(CRUMB_MODULE, MUTED, SMALL, 0.05), text("›", LABEL, MUTED),
                       pill(CRUMB_TOPIC, SOFT, SMALL)).arrange(RIGHT, buff=0.2)
        crumb.move_to(UP * 2.7)
        title = fitted_text(title_s, SAFE_W - 1.0, TITLE + 20, INK, BOLD, max_lines=2).move_to(UP * 1.3)
        facts = VGroup(pill(LESSON_TAG, MUTED, SMALL, 0.05), pill(video if isinstance(video, str) else f"Video {video} of {VIDEO_COUNT}", color, SMALL),
                       pill(level, GOOD, SMALL)).arrange(RIGHT, buff=0.3)
        facts.next_to(title, DOWN, buff=0.45)
        path = VGroup(pill(f"Before: {before}", MUTED, SMALL, 0.05), text("→", LABEL, MUTED),
                      pill("Prerequisite" if isinstance(video, str) else f"Video {video}", color, SMALL), text("→", LABEL, MUTED),
                      pill(f"Next: {nxt}", GOOD, SMALL)).arrange(RIGHT, buff=0.25)
        if path.width > SAFE_W - 0.6:                       # too wide in one row: stack it
            tail = VGroup(*path[1:]).arrange(RIGHT, buff=0.25)
            VGroup(path[0], tail).arrange(DOWN, buff=0.2)
        path.next_to(facts, DOWN, buff=0.5)
        return crumb, title, facts, path

    def passage_card(self, sentences, header, color=MUTED, width=None, size=SMALL + 2, max_lines=3):
        """A passage: optional header line, one fitted block per sentence (``card.sentences``)."""
        x, w = self.stage()
        width = width or (w - 0.2)
        sents = VGroup(*[fitted_text(s, width - 0.6, size, INK, max_lines=max_lines) for s in sentences])
        sents.arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        parts = [sents]
        hdr = None
        if header:
            hdr = text(header, SMALL, MUTED, BOLD)
            parts.insert(0, hdr)
        content = VGroup(*parts).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        c = self.card(content, width=width, color=color)
        c.header, c.sentences = hdr, sents
        return c

    def option_cards(self, options, width, size=SMALL, height=0.9):
        """Answer options as cards in a 2 x 2 grid (long options wrap up to 4 lines)."""
        cards = [self.card(fitted_text(o, width / 2 - 0.75, size, INK, max_lines=4), width=width / 2 - 0.15,
                           height=height, color=MUTED) for o in options]
        grid = VGroup(VGroup(*cards[:2]).arrange(RIGHT, buff=0.3), VGroup(*cards[2:]).arrange(RIGHT, buff=0.3))
        grid.arrange(DOWN, buff=0.2)
        grid.cards = cards
        return grid

    def board(self, rows_spec, color=FOCUS, size=BODY):
        """A numbered list card: ``rows_spec`` = [(text, colour)] (``board.rows``)."""
        x, w = self.stage()
        width = w - 0.2
        rows = VGroup(*[VGroup(pill(str(i + 1), c, LABEL), fitted_text(s, width - 1.6, size, INK, max_lines=2))
                        .arrange(RIGHT, buff=0.35) for i, (s, c) in enumerate(rows_spec)])
        rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        b = self.card(rows, width=width, color=color)
        b.rows = rows
        return b

    def stairs(self, steps):
        """The process as a staircase of raised slabs: ``steps`` = [(text, colour)]."""
        x, w = self.stage()
        width = w - 0.2
        st = VGroup()
        for i, (s, c) in enumerate(steps):
            tile = slab_tile(str(i + 1), c, 0.9, 0.6 + 0.25 * i, LABEL, depth=0.2)
            note = fitted_text(s, width - 1.9, BODY, INK, max_lines=2)
            st.add(VGroup(tile, note).arrange(RIGHT, buff=0.4, aligned_edge=DOWN))
        st.arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        return st

    def pattern_cards(self, specs):
        """Exam patterns: ``specs`` = [(pattern, solving model, colour)]."""
        x, w = self.stage()
        rows = VGroup(*[self.card(VGroup(fitted_text(p, w - 0.8, LABEL, c, BOLD, max_lines=2),
                                         fitted_text(m, w - 0.8, BODY, INK, max_lines=2))
                                  .arrange(DOWN, buff=0.12, aligned_edge=LEFT), width=w - 0.2, color=c)
                        for p, m, c in specs]).arrange(DOWN, buff=0.2)
        return rows

    def mistake_cards(self, items):
        x, w = self.stage()
        return VGroup(*[self.card(tick_row(s, w - 1.6, BAD, "✗"), width=w - 0.2, color=BAD)
                        for s in items]).arrange(DOWN, buff=0.3)

    def question_card(self, title, options, color):
        x, w = self.stage()
        width = w - 0.2
        body = VGroup(fitted_text(title, width - 0.6, SMALL, color, BOLD, max_lines=2),
                      fitted_text(options, width - 0.6, SMALL, INK, max_lines=4)).arrange(DOWN, buff=0.1,
                                                                                         aligned_edge=LEFT)
        return self.card(body, width=width, color=color)

    def answer_card(self, title, answer, why, color):
        x, w = self.stage()
        width = w - 0.2
        body = VGroup(fitted_text(title, width - 0.6, SMALL, color, BOLD, max_lines=2),
                      tick_row(answer, width - 1.4, GOOD, "✓", SMALL, max_lines=2),
                      fitted_text(why, width - 0.6, SMALL, MUTED, max_lines=2)).arrange(DOWN, buff=0.12,
                                                                                       aligned_edge=LEFT)
        return self.card(body, width=width, color=GOOD)

    def recap_table(self, specs):
        """The recap card: ``specs`` = [(name, rule, colour)], full width."""
        rows = VGroup()
        for name, rule, c in specs:
            rows.add(VGroup(text(name, BODY, c, BOLD), fitted_text(rule, SAFE_W - 5.6, BODY, INK, max_lines=2)))
        rows.arrange(DOWN, buff=0.35)
        x_left = -FRAME_W / 2 + SAFE + 0.5
        for r in rows:
            r[0].set_x(x_left + r[0].width / 2)
            r[1].set_x(x_left + 3.9 + r[1].width / 2)
        t = self.card(rows, width=SAFE_W - 0.2, color=GOOD)
        t.rows = rows
        return t

    def reason_into(self, card, label, color=BAD):
        """Animation: an option card turns ``color`` and its text becomes ``label``."""
        why = fitted_text(label, card[0].width - 0.5, SMALL, color, BOLD, max_lines=4).move_to(card[0])
        return AnimationGroup(card[0].animate.set_stroke(color, 3), ReplacementTransform(card[1], why))

    # ------------------------------------------------- shared scenes --

    def hook_question(self, nid, narration, ask_s, options, anchors, below, x=0.0, width=None, pause=5.0):
        """Shared tail of every hook: question pill, four options, thinking time.

        ``narration`` is the full spoken text for this beat (question + options).
        """
        width = width or (SAFE_W - 0.2)
        ask = pill(ask_s, FOCUS, SMALL)
        fit_width(ask, width - 1.2)
        ask.next_to(below, DOWN, buff=0.25).align_to(below, LEFT)
        grid = self.option_cards(options, width)
        grid.next_to(ask, DOWN, buff=0.2).set_x(x)
        self.validator.check_in_frame(VGroup(below, ask, grid))
        n = self.narrate(id=nid, text=narration, voice="default", subtitle=True, pause_after=pause)
        self.at_word(n, anchors[0])
        self.play(FadeIn(ask, shift=UP * 0.15))
        for c, spoken in zip(grid.cards, anchors[1:]):
            self.at_word(n, spoken)
            self.play(FadeIn(c, shift=UP * 0.15), run_time=0.45)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after, RIGHT * (FRAME_W / 2 - SAFE - 0.5) + UP * ask.get_y())
        return ask, grid

    # ---------------------------------------------- pinned panel (compact) --

    def compact_panel(self, title, items, color=MUTED):
        """A docked checklist on the left with one-line rows (fits up to seven rows)."""
        rows = VGroup()
        for name, c in items:
            chip = Square(0.22, stroke_width=0, fill_color=c, fill_opacity=0.9)
            label = fitted_text(name, PANEL_W - 1.1, SMALL, c, BOLD, max_lines=2)
            row = VGroup(chip, label).arrange(RIGHT, buff=0.22)
            row.label, row.color = label, c
            rows.add(row)
        rows.arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        content = VGroup(text(title, SMALL, MUTED, BOLD), rows).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        panel = self.card(content, width=PANEL_W, color=color)
        panel.move_to(RIGHT * PANEL_X + UP * (CARD_TOP - panel.height / 2))
        panel.rows = rows
        return panel

    def open_panel(self, title, items, color=FOCUS):
        """Dock the empty panel frame and pin it; rows are added later with ``add_row``."""
        self.panel = self.compact_panel(title, items, color)
        self.play(FadeIn(self.panel[0]), FadeIn(self.panel[1][0]), run_time=0.8)
        self.pinned.append(self.panel)
        self.validator.check_in_frame(self.panel)

    def add_row(self, k, source=None):
        """Panel row ``k`` grows out of ``source`` (or slides in)."""
        row = self.panel.rows[k]
        if source is None:
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.6)
        else:
            self.play(TransformFromCopy(source, row), run_time=0.9)

    def stage_label(self, s, color=GOOD):
        """A small label pill at the top-left of the free area (for dense scenes)."""
        x, w = self.stage()
        p = pill(s, color, LABEL)
        return p.move_to(RIGHT * (x - w / 2 + p.width / 2) + UP * (CARD_TOP - p.height / 2))

    # ------------------------------------------------------ cloze passage --

    def cloze_card(self, sentences, header=None, color=MUTED, width=None, size=SMALL + 2):
        """A passage card. Blanks are written into the sentences as '(1) ____'.

        ``card.blank(k)`` / ``card.word(w)`` give glyphs; ``self.fill`` re-sets a
        sentence with the blank filled in.
        """
        x, w = self.stage()
        width = width or (w - 0.2)
        inner = width - 0.6
        sents = VGroup(*[fitted_text(s, inner, size, INK, max_lines=3) for s in sentences])
        sents.arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        parts = [sents]
        if header:
            parts.insert(0, text(header, SMALL, MUTED, BOLD))
        content = VGroup(*parts).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        c = self.card(content, width=width, color=color)
        c.sents, c.srcs, c.size, c.inner, c.marks = sents, list(sentences), size, inner, []
        for i, s in enumerate(sentences):
            for tag in re.findall(r"\(\d\) ____", s):
                glyphs(sents[i], s, tag).set_color(FOCUS)
        return c

    @staticmethod
    def _span(mob, s, start, length):
        """Glyphs for characters s[start:start + length] of Text ``mob`` (whitespace has no glyph)."""
        a = len([ch for ch in s[:start] if not ch.isspace()])
        b = len([ch for ch in s[start:start + length] if not ch.isspace()])
        return mob[a:a + b]

    @staticmethod
    def _find(s, word, occurrence=1):
        """Start index of ``word`` as a whole word (occurrence-th), or -1."""
        hits = [m.start() for m in re.finditer(r"(?<![A-Za-z])" + re.escape(word) + r"(?![A-Za-z])", s)]
        return hits[occurrence - 1] if len(hits) >= occurrence else -1

    def _locate(self, c, word, occurrence=1):
        seen = 0
        for i, s in enumerate(c.srcs):
            hits = len(re.findall(r"(?<![A-Za-z])" + re.escape(word) + r"(?![A-Za-z])", s))
            if seen + hits >= occurrence:
                at = self._find(s, word, occurrence - seen)
                return i, self._span(c.sents[i], s, at, len(word))
            seen += hits
        raise ValueError(f"{word!r} not in passage")

    def blank(self, c, k):
        return self._locate(c, f"({k}) ____")[1]

    def mark(self, c, word, color, occurrence=1):
        """Animation: colour a clue word in the passage (kept through later fills)."""
        i, g = self._locate(c, word, occurrence)
        c.marks.append((word, color))
        return AnimationGroup(g.animate.set_color(color), Circumscribe(g, color=color, buff=0.04))

    def fill(self, c, k, word, color=GOOD, *extra):
        """Play: blank ``k`` becomes ``word``; the sentence is re-set in place."""
        tag = f"({k}) ____"
        i = next(j for j, s in enumerate(c.srcs) if tag in s)
        at = c.srcs[i].index(tag)
        new_s = c.srcs[i].replace(tag, word)
        old = c.sents[i]
        new = fitted_text(new_s, c.inner, c.size, INK, max_lines=3)
        new.move_to(old.get_corner(UL), aligned_edge=UL)
        for m in re.finditer(r"\(\d\) ____", new_s):
            self._span(new, new_s, m.start(), len(m.group())).set_color(FOCUS)
        for w_, col in c.marks:
            pos = self._find(new_s, w_)
            if pos >= 0:
                self._span(new, new_s, pos, len(w_)).set_color(col)
        self._span(new, new_s, at, len(word)).set_color(color)
        c.marks.append((word, color))
        c.srcs[i] = new_s
        self.play(ReplacementTransform(old, new), *extra, run_time=0.8)
        c.sents.submobjects[i] = new

    def run_beats(self, n, c, beats, notes):
        """Play cloze beats against narration ``n``.

        Each beat is (anchor, kind, *args); anchor is a word or (word, occurrence).
        kinds: "mark" (word, colour[, occ]), "fill" (k, word[, colour]),
        "note" (index into ``notes``), "light" (*panel rows).
        """
        for anchor, kind, *args in beats:
            if anchor:
                w, occ = anchor if isinstance(anchor, tuple) else (anchor, 1)
                self.at_word(n, w, occurrence=occ)
            if kind == "mark":
                self.play(self.mark(c, *args))
            elif kind == "fill":
                self.fill(c, *args)
            elif kind == "note":
                self.play(FadeIn(notes[args[0]], shift=UP * 0.12))
            elif kind == "light":
                self.play(self.light(*args))

    def notes_under(self, c, specs, buff=0.25):
        """Note pills (text, colour) stacked under card ``c``, fitted to the free width."""
        x, w = self.stage()
        notes = VGroup()
        for s, col in specs:
            p = pill(s, col, SMALL)
            fit_width(p, w - 0.3)
            notes.add(p)
        notes.arrange(DOWN, buff=0.18).next_to(c, DOWN, buff=buff).set_x(x)
        return notes

    # ------------------------------------------------------ shared scenes --

    def std_intro(self, title_s, video_tag, level, before, nxt, narr1, anchors1, narr2):
        """You-are-here scene. ``anchors1`` = [facts word, title word]; ``narr2`` says 'follows' ... 'leads'."""
        self.scene_start("S00_intro", title="You Are Here")
        crumb, title, facts, path = self.intro_parts(title_s, video_tag, level, before, nxt)
        self.validator.check_in_frame(VGroup(crumb, title, facts, path))
        n = self.narrate(id="intro_01", text=narr1, voice="default", subtitle=True)
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, anchors1[0])
        self.play(LaggedStart(*[FadeIn(f, shift=UP * 0.15) for f in facts], lag_ratio=0.2))
        self.at_word(n, anchors1[1])
        self.play(Write(title), run_time=1.0)
        self.wait_for_narration(n)
        n = self.narrate(id="intro_02", text=narr2, voice="default", subtitle=True)
        self.at_word(n, "follows")
        self.play(FadeIn(path[0], shift=RIGHT * 0.2), FadeIn(path[1]), FadeIn(path[2]))
        self.at_word(n, "leads")
        self.play(FadeIn(path[3]), FadeIn(path[4], shift=LEFT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()
        self.scene_end("S00_intro")

    def std_list(self, sid, title, heading_s, color, kind, items, nid, narration, anchors, lights=None):
        """A heading plus a list revealed item by item.

        kind: "board" ([(text, colour)]), "stairs" ([(text, colour)], up to four),
        "mistakes" ([text]), "patterns" ([(pattern, model, colour)]).
        """
        self.scene_start(sid, title=title)
        x, w = self.stage()
        heading = self.heading(heading_s, color)
        if kind == "board":
            g = self.board(items, color)
            rows, frame = g.rows, [g[0]]
        elif kind == "stairs":
            g = self.stairs(items)
            rows, frame = g, []
        elif kind == "mistakes":
            g = self.mistake_cards(items)
            rows, frame = g, []
        else:
            g = self.pattern_cards(items)
            rows, frame = g, []
        g.next_to(heading, DOWN, buff=0.4).set_x(x)
        self.validator.check_in_frame(VGroup(heading, g))
        n = self.narrate(id=nid, text=narration, voice="default", subtitle=True)
        self.play(FadeIn(heading, shift=DOWN * 0.3), *[FadeIn(f) for f in frame])
        for k, (r, a) in enumerate(zip(rows, anchors)):
            w_, occ = a if isinstance(a, tuple) else (a, 1)
            self.at_word(n, w_, occurrence=occ)
            anims = [FadeIn(r, shift=RIGHT * 0.2 if kind == "board" else UP * 0.2)]
            if lights and self.panel is not None and lights[k] is not None:
                anims.append(self.light(*lights[k]))
            self.play(*anims, run_time=0.5)
        self.wait_for_narration(n)
        self.clear_stage()
        self.scene_end(sid)

    def std_table(self, sid, title, heading_s, color, specs, nid, narration, anchors, lights=None, banner=None):
        """A two-column rules table ([(left, right, colour)]), optional banner card on top."""
        self.scene_start(sid, title=title)
        x, w = self.stage()
        left_x = x - w / 2 + 0.15
        heading = self.heading(heading_s, color)
        top = heading
        bc = None
        if banner:
            bc = self.card(fitted_text(banner, w - 0.8, LABEL, color, BOLD, max_lines=2), width=w - 0.2, color=color)
            bc.next_to(heading, DOWN, buff=0.3).set_x(x)
            top = bc
        rows = VGroup(*[VGroup(fitted_text(a, 3.3, LABEL, c, BOLD, max_lines=2),
                               fitted_text(b, w - 4.1, LABEL, INK, max_lines=2)) for a, b, c in specs])
        rows.arrange(DOWN, buff=0.26).next_to(top, DOWN, buff=0.35)
        for r in rows:
            r[0].set_x(left_x + r[0].width / 2)
            r[1].set_x(left_x + 3.7 + r[1].width / 2)
        self.validator.check_in_frame(VGroup(heading, rows, *([bc] if bc else [])))
        n = self.narrate(id=nid, text=narration, voice="default", subtitle=True)
        self.play(FadeIn(heading, shift=DOWN * 0.3), *([FadeIn(bc, shift=DOWN * 0.2)] if bc else []))
        for k, (r, a) in enumerate(zip(rows, anchors)):
            w_, occ = a if isinstance(a, tuple) else (a, 1)
            self.at_word(n, w_, occurrence=occ)
            anims = [FadeIn(r, shift=RIGHT * 0.2)]
            if lights and self.panel is not None and lights[k] is not None:
                anims.append(self.light(*lights[k]))
            self.play(*anims, run_time=0.45)
        self.wait_for_narration(n)
        self.clear_stage()
        self.scene_end(sid)

    def std_worked(self, examples):
        """Worked examples, one per screen.

        ``examples`` = [(label, sentences, notes [(text, colour)], nid, narration, beats)].
        """
        self.scene_start("S07_worked", title="Worked Examples")
        for label_s, sentences, note_specs, nid, narration, beats in examples:
            label = self.stage_label(label_s, GOOD)
            c = self.cloze_card(sentences)
            c.next_to(label, DOWN, buff=0.35).set_x(self.stage()[0])
            notes = self.notes_under(c, note_specs, buff=0.4)
            self.validator.check_in_frame(VGroup(label, c, notes))
            n = self.narrate(id=nid, text=narration, voice="default", subtitle=True)
            self.play(FadeIn(label, shift=DOWN * 0.2), FadeIn(c, shift=UP * 0.2))
            self.run_beats(n, c, beats, notes)
            self.wait_for_narration(n)
            self.clear_stage()
        self.scene_end("S07_worked")

    def std_hook_solved(self, sentences, options, read, predict, eliminate, confirm, steps=STEPS):
        """READ / PREDICT / ELIMINATE / CONFIRM on a passage excerpt.

        read      = (nid, narration, beats)           - beats as in ``run_beats``
        predict   = (nid, narration, anchor, label, rows_to_light)
        eliminate = (nid, narration, [(anchor, option index, reason)])
        confirm   = (nid, narration, fill_anchor, k, word, answer index)
        """
        self.scene_start("S10_hook_solved", title="Hook, Solved")
        x, w = self.stage()
        label = self.stage_label("Hook, solved", FOCUS)
        tracker = self.step_tracker(steps)
        fit_width(tracker, w - 0.2).set_x(x)
        c = self.cloze_card(sentences)
        c.next_to(label, DOWN, buff=0.25).set_x(x)
        pred = pill(predict[3], FOCUS, SMALL)
        fit_width(pred, w - 0.3).next_to(c, DOWN, buff=0.25).set_x(x)
        grid = self.option_cards(options, w - 0.2, height=0.8)
        grid.next_to(pred, DOWN, buff=0.25).set_x(x)
        self.validator.check_in_frame(VGroup(label, c, pred, grid, tracker))

        nid, narration, beats = read
        n = self.narrate(id=nid, text=narration, voice="default", subtitle=True)
        self.play(FadeIn(label, shift=DOWN * 0.2), FadeIn(tracker, shift=UP * 0.2), self.focus_step(tracker, 0))
        self.play(FadeIn(c, shift=UP * 0.2))
        self.run_beats(n, c, beats, VGroup())
        self.wait_for_narration(n)

        nid, narration, anchor, _, lit = predict
        n = self.narrate(id=nid, text=narration, voice="default", subtitle=True)
        self.play(self.focus_step(tracker, 1))
        self.at_word(n, anchor)
        anims = [FadeIn(pred, shift=UP * 0.12)]
        if lit and self.panel is not None:
            anims.append(self.light(*lit))
        self.play(*anims)
        self.wait_for_narration(n)

        nid, narration, cuts = eliminate
        n = self.narrate(id=nid, text=narration, voice="default", subtitle=True)
        self.play(self.focus_step(tracker, 2), FadeIn(grid, shift=UP * 0.2))
        for anchor, idx, reason in cuts:
            w_, occ = anchor if isinstance(anchor, tuple) else (anchor, 1)
            self.at_word(n, w_, occurrence=occ)
            self.play(self.reason_into(grid.cards[idx], reason), run_time=0.6)
        self.wait_for_narration(n)

        nid, narration, fill_anchor, k, word, ans, *more = confirm
        n = self.narrate(id=nid, text=narration, voice="default", subtitle=True)
        self.play(self.focus_step(tracker, 3))
        self.at_word(n, fill_anchor)
        self.fill(c, k, word, GOOD, grid.cards[ans][0].animate.set_stroke(GOOD, 4))
        self.play(Circumscribe(grid.cards[ans], color=GOOD))
        for anchor, kk, ww in (more[0] if more else []):      # other blanks settled on the way
            self.at_word(n, anchor)
            self.fill(c, kk, ww, HINT)
        self.wait_for_narration(n)
        self.clear_stage()
        self.scene_end("S10_hook_solved")

    def std_practice(self, sentences, questions, narrs, anchors, pause=10.0):
        """Passage + one options card per blank; thinking time after the last question.

        ``narrs`` = [passage narration, question 1 narration, ...]; ``anchors`` likewise.
        """
        self.scene_start("S13_practice", title="Practice Questions")
        x, w = self.stage()
        label = self.stage_label("Practice", GOOD)
        c = self.cloze_card(sentences, header="Passage")
        c.next_to(label, DOWN, buff=0.25).set_x(x)
        qs = VGroup(*[self.card(fitted_text(q, w - 0.8, SMALL + 2, INK, max_lines=2), width=w - 0.2, color=MUTED,
                                pad=0.2) for q in questions]).arrange(DOWN, buff=0.18)
        qs.next_to(c, DOWN, buff=0.3).set_x(x)
        self.validator.check_in_frame(VGroup(label, c, qs))
        n = self.narrate(id="practice_01", text=narrs[0], voice="default", subtitle=True)
        self.play(FadeIn(label, shift=DOWN * 0.2), *([self.all_lit()] if self.panel is not None else []))
        self.at_word(n, anchors[0])
        self.play(FadeIn(c, shift=UP * 0.2))
        self.wait_for_narration(n)
        for k, (q, line, a) in enumerate(zip(qs, narrs[1:], anchors[1:])):
            last = k == len(qs) - 1
            n = self.narrate(id=f"practice_{k + 2:02d}", text=line, voice="default", subtitle=True,
                             pause_after=pause if last else 0.0)
            self.at_word(n, a)
            self.play(FadeIn(q, shift=UP * 0.15), Indicate(self.blank(c, k + 1), color=FOCUS))
            if last:
                self.wait_for_narration(n, include_pause=False)
                self.countdown(n.pause_after, RIGHT * (x + w / 2 - 0.5) + UP * label.get_y())
            else:
                self.wait_for_narration(n)
        self.practice_block = (label, c, qs)
        self.scene_end("S13_practice")

    def std_answers(self, answers):
        """``answers`` = [(k, word, answer line, nid, narration, anchor, rows to light)]."""
        self.scene_start("S14_answers", title="Answers")
        x, w = self.stage()
        label, c, qs = self.practice_block
        new_label = pill("Answers", GOOD, LABEL).move_to(label).align_to(label, LEFT)
        self.play(FadeTransform(label, new_label))
        for q, (k, word, line_s, nid, narration, anchor, lit) in zip(qs, answers):
            a = self.card(tick_row(line_s, w - 1.6, GOOD, "✓", SMALL + 2, max_lines=2), width=w - 0.2, color=GOOD,
                          pad=0.2).move_to(q)
            n = self.narrate(id=nid, text=narration, voice="default", subtitle=True)
            self.at_word(n, anchor)
            extra = [ReplacementTransform(q, a)]
            if lit and self.panel is not None:
                extra.append(self.light(*lit))
            self.fill(c, k, word, GOOD, *extra)
            self.wait_for_narration(n)
        self.clear_stage()
        self.scene_end("S14_answers")

    def std_recap(self, heading_s, specs, nid, narration, anchors):
        """Undock the panel and show the recap card ([(name, rule, colour)])."""
        self.scene_start("S15_recap", title="Recap and Next")
        if self.panel is not None:
            self.undock()
        heading = self.heading(heading_s, GOOD)
        table = self.recap_table(specs)
        table.next_to(heading, DOWN, buff=0.35).set_x(0)
        self.validator.check_in_frame(VGroup(heading, table))
        n = self.narrate(id=nid, text=narration, voice="default", subtitle=True)
        self.play(FadeIn(heading, shift=DOWN * 0.3), FadeIn(table[0]))
        for r, a in zip(table.rows, anchors):
            w_, occ = a if isinstance(a, tuple) else (a, 1)
            self.at_word(n, w_, occurrence=occ)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)
        self.play(FadeOut(table))
        self.recap_heading = heading

    def std_next(self, narration, items):
        """Closing: ``items`` = [(anchor, pill text, colour)] revealed in a column."""
        pills = VGroup(*[pill(s, c, BODY) for _, s, c in items]).arrange(DOWN, buff=0.4)
        for p in pills:
            fit_width(p, SAFE_W - 0.6)
        pills.next_to(self.recap_heading, DOWN, buff=0.6).set_x(0)
        self.validator.check_in_frame(VGroup(self.recap_heading, pills))
        n = self.narrate(id="next_01", text=narration, voice="default", subtitle=True)
        for p, (a, _, _) in zip(pills, items):
            self.at_word(n, a)
            self.play(FadeIn(p, shift=UP * 0.15))
        self.wait_for_narration(n)
        self.clear_stage(run_time=1.0)
        self.scene_end("S15_recap")

    # ============================================== 0. YOU ARE HERE ======

    def you_are_here(self):
        self.std_intro(
            "Elimination Techniques", 7, "Exam-level · about 5 min", "Connectors and Transition Words", "Exam Practice",
            "This is Lesson thirteen, Video seven of eight: Elimination Techniques, a five-minute exam-level video.",
            ["eight", "Elimination"],
            "It follows Connectors and Transition Words, and leads into Exam Practice.")

    # ================================================= 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        c = self.cloze_card(HOOK_PASSAGE, header="Customer email", color=HINT)
        c.move_to(UP * (CARD_TOP - c.height / 2))
        self.validator.check_in_frame(c)
        n = self.narrate(
            id="hook_01",
            text="A customer writes: I have been a blank one user of your app for five years. Recently, though, the "
                 "frequent crashes have made me consider switching.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "writes")
        self.play(FadeIn(c, shift=UP * 0.3))
        self.at_word(n, "one")
        self.play(Indicate(self.blank(c, 1), color=FOCUS))
        self.wait_for_narration(n)

        ask, grid = self.hook_question(
            "hook_02", "Which option fits? (a) reluctant, (b) loyal, (c) occasional, or (d) former.",
            "Which option fits?", HOOK_OPTIONS, ["Which", "reluctant", "loyal", "occasional", "former"], c)

        n = self.narrate(
            id="hook_03",
            text="Two options look plausible at first. The passage removes one of them.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plausible")
        self.play(grid.cards[1][0].animate.set_stroke(FOCUS, 4), grid.cards[2][0].animate.set_stroke(FOCUS, 4))
        self.at_word(n, "removes")
        self.play(grid.cards[2].animate.set_opacity(0.35), self.mark(c, "though", DEP))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_hook")

    # =========================================== 2. OBJECTIVES ==========

    def objectives(self):
        self.std_list(
            "S02_objectives", "Objectives", "In this video", GOOD, "board",
            [("Eliminate cloze options in a fixed order: grammar, passage logic, precision", GRAM),
             ("Handle blanks that depend on each other", DEP)],
            "obj_01",
            "In this video, you'll learn to eliminate cloze options in a fixed order: grammar, passage logic, precision. "
            "And to handle blanks that depend on each other.",
            ["eliminate", "handle"])

    # =========================================== 3. CONTINUITY ==========

    def continuity(self):
        self.scene_start("S03_continuity", title="Continuity")

        heading = self.heading("From blank types to an order", HINT)
        tiles = VGroup(*[slab_tile(s, c, 3.6, 0.85, LABEL, depth=0.18) for s, c in
                         [("Video 4: grammar blanks", GRAM), ("Video 5: vocabulary blanks", PREC),
                          ("Video 6: connector blanks", DEP)]]).arrange(RIGHT, buff=0.4)
        fit_width(tiles, SAFE_W - 0.3).next_to(heading, DOWN, buff=0.6)
        order = pill("today: the order of elimination", GOOD, BODY).next_to(tiles, DOWN, buff=0.6)
        b1 = pill("(2) connector", DEP, BODY)
        b2 = pill("(1) adjective", PREC, BODY)
        dep = VGroup(b1, b2).arrange(RIGHT, buff=2.2).next_to(order, DOWN, buff=0.7)
        link = Arrow(b1.get_right(), b2.get_left(), buff=0.1, color=DEP, stroke_width=4)
        dep_tag = text("one blank depends on another", SMALL, DEP, BOLD).next_to(link, UP, buff=0.1)
        self.validator.check_in_frame(VGroup(heading, tiles, order, dep, dep_tag))

        n = self.narrate(
            id="cont_01",
            text="Videos four to six covered grammar, vocabulary and connector blanks. Today is about the order of "
                 "elimination, and what to do when one blank depends on another.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(heading, shift=DOWN * 0.3))
        self.at_word(n, "grammar")
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in tiles], lag_ratio=0.2))
        self.at_word(n, "order")
        self.play(FadeIn(order, shift=UP * 0.1))
        self.at_word(n, "depends")
        self.play(FadeIn(b1), GrowArrow(link), FadeIn(b2), FadeIn(dep_tag))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_continuity")

    # ============================================= 4. THE CONCEPT ==========

    def concept(self):
        self.scene_start("S04_concept", title="The Concept")
        self.open_panel("Elimination order", ORDER)

        head = self.heading("Three filters on every blank", GRAM)
        specs = [("1  Grammar", GRAM, ["article", "number", "verb form", "part of speech"]),
                 ("2  Passage logic", LOGIC, ["timeline", "tone", "turns"]),
                 ("3  Precision", PREC, ["meaning", "strength", "collocation"])]
        layers = VGroup()
        for name, c, subs in specs:
            tile = slab_tile(name, c, 2.9, 0.75, LABEL, depth=0.2)
            ps = VGroup(*[pill(s, c, SMALL, 0.06) for s in subs]).arrange(RIGHT, buff=0.15)
            fit_width(ps, STAGE_W - 3.6)
            layers.add(VGroup(tile, ps).arrange(RIGHT, buff=0.4))
        layers.arrange(DOWN, buff=0.45, aligned_edge=LEFT).next_to(head, DOWN, buff=0.6).set_x(STAGE_X)
        self.validator.check_in_frame(VGroup(head, layers))
        n = self.narrate(
            id="c_01",
            text="Run three filters on every blank.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.3))
        self.at_word(n, "three")
        self.play(LaggedStart(*[FadeIn(layer[0], shift=DOWN * 0.2) for layer in layers], lag_ratio=0.2))
        self.wait_for_narration(n)

        lines = [("c_02", "First, grammar. Does the option fit the sentence's structure: article, number, verb form, part "
                          "of speech?", "structure"),
                 ("c_03", "Second, passage logic. Does it fit the timeline, tone and turns of the passage?", "timeline"),
                 ("c_04", "Third, precision: meaning, strength and collocation.", "meaning")]
        for k, (layer, (nid, line, spoken)) in enumerate(zip(layers, lines)):
            n = self.narrate(id=nid, text=line, voice="default", subtitle=True)
            self.play(Indicate(layer[0], color=specs[k][1], scale_factor=1.06))
            self.at_word(n, spoken)
            self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.1) for p in layer[1]], lag_ratio=0.12))
            self.wait_for_narration(n)
            self.add_row(k, layer[0])
        self.clear_stage()

        # Dependent blanks.
        head = self.heading("Dependent blanks", DEP)
        conn = slab_tile("(2) connector", DEP, 3.2, 0.9, BODY)
        adj = slab_tile("(1) adjective", PREC, 3.2, 0.9, BODY)
        pair = VGroup(conn, adj).arrange(RIGHT, buff=1.6).next_to(head, DOWN, buff=0.8).set_x(STAGE_X)
        link = Arrow(conn.get_right(), adj.get_left(), buff=0.1, color=DEP, stroke_width=5)
        sets = text("sets the direction", SMALL, DEP, BOLD).next_to(link, UP, buff=0.1)
        certain = pill("more certain → solve first", GOOD, SMALL).next_to(conn, DOWN, buff=0.3)
        then = pill("then use it", PREC, SMALL).next_to(adj, DOWN, buff=0.3)
        self.validator.check_in_frame(VGroup(head, pair, sets, certain, then))
        n = self.narrate(
            id="c_05",
            text="Dependent blanks. Sometimes one blank's answer affects another: a connector blank changes the direction "
                 "of the next sentence's adjective. Solve the more certain blank first, then use it to decide the other.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.3))
        self.at_word(n, "connector")
        self.play(FadeIn(conn, shift=UP * 0.2))
        self.at_word(n, "direction")
        self.play(GrowArrow(link), FadeIn(sets), FadeIn(adj, shift=UP * 0.2))
        self.at_word(n, "certain")
        self.play(FadeIn(certain, shift=UP * 0.1))
        self.at_word(n, "decide")
        self.play(FadeIn(then, shift=UP * 0.1))
        self.wait_for_narration(n)
        self.add_row(3, certain)
        self.clear_stage()

        # Skip and return.
        head = self.heading("Skip and return", SKIP)
        chips = VGroup(*[pill(f"({k})", MUTED, BODY, 0.05) for k in range(1, 6)]).arrange(RIGHT, buff=0.7)
        chips.next_to(head, DOWN, buff=1.4).set_x(STAGE_X)
        hop = CurvedArrow(chips[1].get_top() + UP * 0.05, chips[2].get_top() + UP * 0.05, angle=-PI / 2, color=SKIP,
                          stroke_width=4)
        back = CurvedArrow(chips[4].get_bottom() + DOWN * 0.05, chips[1].get_bottom() + DOWN * 0.05, angle=-PI / 3,
                           color=GOOD, stroke_width=4)
        skip_t = text("unclear after three filters → move on", SMALL, SKIP, BOLD).next_to(hop, UP, buff=0.15)
        back_t = text("later blanks often reveal it", SMALL, GOOD, BOLD).next_to(back, DOWN, buff=0.15)
        self.validator.check_in_frame(VGroup(head, chips, skip_t, back_t))
        n = self.narrate(
            id="c_06",
            text="Skip and return. If a blank isn't clear after the three filters, move on. Later blanks often reveal the "
                 "answer.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.3), LaggedStart(*[FadeIn(ch) for ch in chips], lag_ratio=0.1))
        self.at_word(n, "clear")
        self.play(chips[1].animate.set_opacity(0.4), Create(hop), FadeIn(skip_t))
        self.at_word(n, "Later")
        self.play(*[chips[k].animate.set_color(GOOD) for k in (0, 2, 3, 4)])
        self.at_word(n, "reveal")
        self.play(Create(back), FadeIn(back_t), chips[1].animate.set_opacity(1).set_color(GOOD))
        self.wait_for_narration(n)
        self.add_row(4, chips[1])

        self.clear_stage()
        self.scene_end("S04_concept")

    # ========================================== 5. WHY YOU NEED IT =========

    def why_you_need_it(self):
        self.scene_start("S05_why", title="Why You Need It")

        heading = self.heading("Many blanks, limited time", BAD)
        chips = VGroup(*[pill(f"({k})", MUTED, SMALL, 0.05) for k in range(1, 9)]).arrange(RIGHT, buff=0.25)
        fit_width(chips, STAGE_W - 1.6).next_to(heading, DOWN, buff=0.6).set_x(STAGE_X - 0.6)
        ring = VGroup(Circle(radius=0.45, stroke_color=BAD, stroke_width=5), text("time", SMALL, BAD, BOLD))
        ring[1].move_to(ring[0])
        ring.next_to(chips, RIGHT, buff=0.4)
        keep = VGroup(slab_tile("a fixed elimination order", GRAM, 3.8, 0.9, LABEL),
                      slab_tile("a skip rule", SKIP, 3.0, 0.9, LABEL)).arrange(RIGHT, buff=0.5)
        keep.next_to(chips, DOWN, buff=0.8).set_x(STAGE_X)
        result = VGroup(pill("moving", GOOD, BODY), pill("accurate", GOOD, BODY)).arrange(RIGHT, buff=0.5)
        result.next_to(keep, DOWN, buff=0.6).set_x(STAGE_X)
        self.validator.check_in_frame(VGroup(heading, chips, ring, keep, result))

        n = self.narrate(
            id="why_01",
            text="A cloze passage has many blanks and limited time. A fixed elimination order and a skip rule keep you "
                 "moving and accurate.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(heading, shift=DOWN * 0.3))
        self.at_word(n, "many")
        self.play(LaggedStart(*[FadeIn(ch) for ch in chips], lag_ratio=0.08))
        self.at_word(n, "limited")
        self.play(Create(ring[0]), FadeIn(ring[1]))
        self.at_word(n, "fixed")
        self.play(FadeIn(keep[0], shift=UP * 0.2), self.light(0, 1, 2))
        self.at_word(n, "skip")
        self.play(FadeIn(keep[1], shift=UP * 0.2), self.light(4))
        self.at_word(n, "moving")
        self.play(FadeIn(result, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_why")

    # ============================================= 6. THE ANALOGY ==========
    # 3D: a raised Sudoku grid; certain cells first unlock the hard one.

    def analogy(self):
        self.scene_start("S06_analogy", title="The Analogy")

        heading = self.heading("Cloze is like Sudoku", FOCUS)

        # Keep the Sudoku board and explanatory notes inside the stage as one
        # controlled composition.  The long note pills must be fitted before
        # they are positioned; otherwise their natural width pushes the stack
        # beyond the right safe boundary.
        size = 0.72
        base = Slab(4 * size + 0.3, 4 * size + 0.3, MUTED, depth=0.28, fill=CELL)
        base.next_to(heading, DOWN, buff=0.4)

        origin = base.front.get_corner(UL) + RIGHT * (0.15 + size / 2) + DOWN * (0.15 + size / 2)
        base_anchor = base.get_center().copy()
        cells, digits = {}, {}
        grid = VGroup()
        for r in range(4):
            for c in range(4):
                sq = Square(size, stroke_color=MUTED, stroke_width=2).move_to(
                    origin + RIGHT * c * size + DOWN * r * size
                )
                cells[(r, c)] = sq
                grid.add(sq)
                digits[(r, c)] = text(str(SUDOKU[r][c]), LABEL, INK, BOLD).move_to(sq)

        givens = VGroup(*[digits[k] for k in digits if k not in EASY and k != HARD])
        easy = VGroup(*[digits[k].set_color(GOOD) for k in EASY])
        hard_box = cells[HARD]
        hard = digits[HARD].set_color(FOCUS)
        q = text("?", LABEL, FOCUS, BOLD).move_to(hard_box)

        note_items = [
            pill("certain cells first", GOOD, SMALL),
            pill("they unlock the harder ones", FOCUS, SMALL),
            pill("never stare at one hard cell", BAD, SMALL),
        ]

        # Reserve enough width for the board + gap, then fit every note to the
        # remaining width.  This specifically prevents notes[1]/notes[2] from
        # crossing the frame while keeping the text readable.
        note_width = max(2.8, STAGE_W - base.width - 0.95)
        for p in note_items:
            fit_width(p, note_width)

        notes = VGroup(*note_items).arrange(
            DOWN, buff=0.35, aligned_edge=LEFT
        )

        composition = VGroup(base, notes).arrange(
            RIGHT, buff=0.55, aligned_edge=UP
        )
        fit_width(composition, STAGE_W - 0.3)
        composition.next_to(heading, DOWN, buff=0.4).set_x(STAGE_X)

        # Re-anchor the board/grid after moving the Slab as part of the
        # composition.  The cells/digits were built from the original base
        # position, so shift them by the same amount as the base.
        board_shift = base.get_center() - base_anchor
        grid.shift(board_shift)
        for mob in digits.values():
            mob.shift(board_shift)

        self.validator.check_in_frame(VGroup(heading, base, grid, notes))

        n = self.narrate(
            id="an_01",
            text="Solving a cloze test is like Sudoku. Fill the certain cells first; they unlock the harder ones. You never "
                 "stare at one hard cell while easy ones are waiting.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(heading, shift=DOWN * 0.3))
        self.at_word(n, "Sudoku")
        self.play(FadeIn(base, shift=UP * 0.2), Create(grid), FadeIn(givens))
        self.play(FadeIn(q), hard_box.animate.set_stroke(FOCUS, 4))
        self.at_word(n, "certain")
        self.play(LaggedStart(*[FadeIn(e, scale=1.3) for e in easy], lag_ratio=0.2), FadeIn(notes[0]), self.light(3))
        self.at_word(n, "unlock")
        self.play(ReplacementTransform(q, hard), FadeIn(notes[1]))
        self.at_word(n, "stare")
        self.play(FadeIn(notes[2]), self.light(4))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_analogy")

    # ======================================= 7. WORKED EXAMPLES ==========

    def worked_examples(self):
        self.std_worked([(
            "Worked example",
            ["The results were (1) ____.", "(2) ____, the team decided to repeat the experiment."],
            [("(2) connector: repeating suggests a problem → Therefore", DEP),
             ("that makes (1) negative → inconclusive", BAD)],
            "we_01",
            "The results were blank one. Blank two, the team decided to repeat the experiment. Blank two is a connector: "
            "the team repeated the experiment, which suggests a problem, so: therefore. That makes blank one negative: "
            "inconclusive.",
            [("connector", "mark", "repeat the experiment", DEP), ("connector", "light", 3), ("problem", "note", 0),
             ("therefore", "fill", 2, "Therefore", DEP), ("negative", "note", 1),
             ("inconclusive", "fill", 1, "inconclusive", BAD)])])

    # ================================================== 8. RULES ==========

    def rules(self):
        self.std_table(
            "S08_rules", "Rules", "Rules", FOCUS,
            [("Dependent blanks", "Solve the more certain one first.", DEP),
             ("Unclear after three filters", "Skip and return.", SKIP)],
            "rules_01",
            "The rules. Grammar, then passage logic, then precision. For dependent blanks, solve the more certain one "
            "first. And if a blank is unclear after the three filters: skip, and return.",
            ["dependent", "unclear"], [(3,), (4,)], banner="Grammar → Passage logic → Precision")

    # ================================================ 9. THE PROCESS ======

    def process(self):
        self.std_list(
            "S09_process", "The Process", "The process", GOOD, "board",
            [("Skim the whole passage", HINT), ("Solve grammar blanks first", GRAM),
             ("Solve connector blanks (they fix directions)", DEP),
             ("Solve vocabulary blanks with grammar, logic and precision", PREC), ("Return to skipped blanks", SKIP)],
            "process_01",
            "The process. Skim the whole passage. Solve the grammar blanks first. Then the connector blanks; they fix the "
            "directions. Then the vocabulary blanks, with grammar, logic and precision. And return to any skipped blanks.",
            ["Skim", "grammar", "connector", "vocabulary", "return"], [None, (0,), (3,), (0, 1, 2), (4,)])

    # =============================================== 10. HOOK, SOLVED ======

    def hook_solved(self):
        self.std_hook_solved(
            HOOK_PASSAGE, HOOK_OPTIONS,
            ("hs_01", "Back to the hook. Read: five years of use; though; frequent crashes; considering switching.",
             [("five", "mark", "for five years", LOGIC), ("though", "mark", "though", DEP),
              ("crashes", "mark", "frequent crashes", BAD), ("switching", "mark", "consider switching", BAD)]),
            ("hs_02", "Predict: long, committed use, contrasted with present frustration. So: loyal.", "loyal",
             "long, committed use vs. present frustration → loyal", (1,)),
            ("hs_03", "Eliminate. Grammar: a, blank one, user, needs a consonant-sound adjective, so occasional already "
                      "fails; it would need an. Logic: (d) former clashes with consider switching: they haven't left yet. "
                      "And (a) reluctant clashes with five years of use.",
             [("occasional", 2, '✗  (c) grammar: "an occasional"'), ("former", 3, "✗  (d) logic: they haven't left yet"),
              ("reluctant", 0, "✗  (a) logic: five years of use")]),
            ("hs_04", "Confirm: I have been a loyal user of your app for five years. The answer is (b).",
             "loyal", 1, "loyal", 1))

    # ========================================= 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.std_list(
            "S11_patterns", "Exam Patterns and Solving Models", "Exam patterns", FOCUS, "patterns",
            [("Hard vocabulary blank", "Grammar → logic → precision.", PREC),
             ("Connector + adjective pair", "Connector first.", DEP),
             ("Blank still unclear", "Skip; return after the others.", SKIP)],
            "patterns_01",
            "Three exam patterns. A hard vocabulary blank: grammar, then logic, then precision. A connector and adjective "
            "pair: the connector first. And a blank that's still unclear: skip it, and return after the others.",
            ["hard", "pair", "unclear"], [(0, 1, 2), (3,), (4,)])

    # ======================================== 12. COMMON MISTAKES =========

    def common_mistakes(self):
        self.std_list(
            "S12_mistakes", "Common Mistakes", "Three common mistakes", BAD, "mistakes",
            ["Getting stuck on one blank", "Solving blanks strictly in order",
             'Ignoring "though", "yet" and "but" inside sentences'],
            "mistakes_01",
            "Three common mistakes. Getting stuck on one blank. Solving blanks strictly in order. And ignoring though, yet "
            "and but inside sentences.",
            ["Getting", "Solving", "ignoring"], [(4,), (3,), (1,)])

    # ================================================ 13. PRACTICE ==========

    def practice(self):
        self.std_practice(
            ["The new manager was (1) ____ at first.", "(2) ____, within a month, she had won over the entire team."],
            ["Blank (1):   (a) welcomed   (b) celebrated   (c) distrusted   (d) admired",
             "Blank (2):   (a) However   (b) Moreover   (c) Therefore   (d) Similarly"],
            ["Now try this passage. The new manager was blank one at first. Blank two, within a month, she had won over "
             "the entire team.",
             "Blank one: (a) welcomed, (b) celebrated, (c) distrusted, or (d) admired.",
             "Blank two: (a) However, (b) Moreover, (c) Therefore, or (d) Similarly."],
            ["manager", "welcomed", "However"])

    # ================================================= 14. ANSWERS ==========

    def answers(self):
        self.std_answers([
            (1, "distrusted", '(c) distrusted: "won over" later implies the team was against her', "answers_01",
             "Blank one: (c), distrusted. Won over, later in the passage, implies the team was against her at first.",
             "against", (1, 3)),
            (2, "However", "(a) However: a turn from distrust to acceptance", "answers_02",
             "Blank two: (a), however. A turn from distrust to acceptance.", "turn", (3,))])

    # ============================================== 15. RECAP AND NEXT ====

    def recap(self):
        self.std_recap(
            "Recap card: Video 7",
            [("Filters", "Grammar → passage logic → precision", GRAM),
             ("Order", "Grammar blanks → connectors → vocabulary → skipped", LOGIC),
             ("Dependent blanks", "Solve the more certain one first.", DEP)],
            "recap_01",
            "To recap. The filters: grammar, then passage logic, then precision. The order: grammar blanks, then "
            "connectors, then vocabulary, then the ones you skipped. And dependent blanks: solve the more certain one "
            "first.",
            ["filters", "order", "dependent"])
        self.std_next(
            "Video eight runs the full method on an exam-level passage.",
            [("eight", "Next: Video 8 · Exam Practice", GOOD),
             ("exam-level", "the full method on an exam-level passage", FOCUS)])
