"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - English
Module : Module 3 - Verbal Ability
Lesson : Lesson 13 - Cloze Test (Fill in the Blanks)
Topic  : Video 8 of 8 - Exam Practice: Cloze Test (Exam-level, about 7 min)

Source script:
  08 - Exam Practice.pdf
  Prose narrated closely; headings become scenes. Blanks are read aloud as
  "blank one", "blank two". Answers checked: hook (2) (a) therefore, with
  (1) and, (3) nearly; practice (d) growing, (c) and, (b) have.

Golden-reference pattern: one ``LMSScene`` class, narration as the timeline,
one method per section, zone constants and ``fitted_text`` for all text.

House rules:
  * a visual beat for every meaningful sentence and key word;
  * pinned S-G-C-V-R panel (left) from The Concept to the recap; each step is
    added as it is taught and lights up when used;
  * drawn 3D: the seven videos merging into one method, the S-G-C-V-R letter
    tiles, the inspector's parts and machine;
  * passages are real cloze cards: blanks are filled in place, and the hook's
    passage is re-read with every answer in place.

Section map:
  S00 You are here   S01 Hook (metro passage, 90 s)   S02 Objectives
  S03 Continuity     S04 The Concept (S-G-C-V-R)   S05 Why You Need It
  S06 The Analogy (inspector)   S07 Worked Example   S08 Rules   S09 The Process
  S10 Hook, Solved   S11 Exam Patterns   S12 Common Mistakes   S13 Practice
  S14 Answers   S15 Recap and Next
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

S_ = HINT              # skim
G_ = FOCUS             # grammar blanks
C_ = TURN              # connector blanks
V_ = ACCENT            # vocabulary blanks
R_ = GOOD              # re-read

METHOD = [("S · Skim", S_), ("G · Grammar blanks", G_), ("C · Connector blanks", C_), ("V · Vocabulary blanks", V_),
          ("R · Re-read", R_)]

STEPS_DETAIL = [("S", "Skim", "Read the whole passage through the blanks: topic, tone, structure, turns.", S_),
                ("G", "Grammar blanks", "Solve every blank whose options are grammar variants.", G_),
                ("C", "Connector blanks", "Name the relationship between sentences; fill connectors.", C_),
                ("V", "Vocabulary blanks", "Grammar → passage logic → precision.", V_),
                ("R", "Re-read", "Read the full passage with every answer in place. Does it flow, with a consistent "
                                 "tense, tone and logic?", R_)]

HOOK_PASSAGE = ["When the city's metro opened in 2019, few people used it.",
                "The stations were far from residential areas, (1) ____ the fares were high.",
                "The authorities (2) ____ introduced feeder buses and cut fares by a third.",
                "Ridership has (3) ____ tripled since then."]
HOOK_OPTIONS = ["(a) therefore", "(b) however", "(c) meanwhile", "(d) instead"]


class ClozeExamPracticeVideo(LMSScene):
    lesson_title = "Exam Practice: Cloze Test"

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
        """Breadcrumb, title, facts and a safe two-row before/next path."""
        crumb = VGroup(pill("English", MUTED, SMALL, 0.05), text("›", LABEL, MUTED),
                       pill(CRUMB_MODULE, MUTED, SMALL, 0.05), text("›", LABEL, MUTED),
                       pill(CRUMB_TOPIC, SOFT, SMALL)).arrange(RIGHT, buff=0.2)
        crumb.move_to(UP * 2.7)

        title = fitted_text(title_s, SAFE_W - 1.0, TITLE + 20, INK, BOLD, max_lines=2).move_to(UP * 1.3)

        facts = VGroup(
            pill(LESSON_TAG, MUTED, SMALL, 0.05),
            pill(video if isinstance(video, str) else f"Video {video} of {VIDEO_COUNT}", color, SMALL),
            pill(level, GOOD, SMALL),
        ).arrange(RIGHT, buff=0.3)
        facts.next_to(title, DOWN, buff=0.45)

        before_pill = pill(f"Before: {before}", MUTED, SMALL, 0.05)
        arrow1 = text("→", LABEL, MUTED)
        middle_pill = pill("Prerequisite" if isinstance(video, str) else f"Video {video}", color, SMALL)
        arrow2 = text("→", LABEL, MUTED)
        next_pill = pill(f"Next: {nxt}", GOOD, SMALL)

        # Long course-path labels must never be allowed to push the path outside
        # the camera. Fit each pill first, then arrange the path in two rows.
        fit_width(before_pill, SAFE_W - 0.8)
        fit_width(middle_pill, SAFE_W - 0.8)
        fit_width(next_pill, SAFE_W - 0.8)

        top_row = VGroup(before_pill, arrow1, middle_pill).arrange(RIGHT, buff=0.2)
        bottom_row = VGroup(arrow2, next_pill).arrange(RIGHT, buff=0.2)

        # Keep the five original children so std_intro can continue to animate
        # path[0] through path[4] independently.
        path = VGroup(before_pill, arrow1, middle_pill, arrow2, next_pill)
        top_row.move_to(ORIGIN)
        bottom_row.next_to(top_row, DOWN, buff=0.22).align_to(top_row, RIGHT)

        path.next_to(facts, DOWN, buff=0.5)
        path.set_x(0)
        fit_width(path, SAFE_W - 0.25)
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
            "Exam Practice: Cloze Test", 8, "Exam-level · about 7 min", "Elimination Techniques",
            "Lesson 13 Quiz, then Module 4 · Lesson 14: Reading Comprehension",
            "This is Lesson thirteen, Video eight of eight: Exam Practice for the Cloze Test, a seven-minute exam-level "
            "video.",
            ["eight", "Practice"],
            "It follows Elimination Techniques, and leads into the Lesson thirteen Quiz, then Module four: Reading "
            "Skills, Lesson fourteen, Reading Comprehension.")

    # ================================================= 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        c = self.cloze_card(HOOK_PASSAGE, header="You have 90 seconds · a three-blank passage", color=HINT)
        c.move_to(UP * (CARD_TOP - c.height / 2))
        timer = VGroup(Circle(radius=0.4, stroke_color=BAD, stroke_width=5), text("90 s", SMALL, BAD, BOLD))
        timer[1].move_to(timer[0])
        timer.move_to(c[0].get_corner(UR) + LEFT * 0.6 + DOWN * 0.55)
        self.validator.check_in_frame(VGroup(c, timer))
        n = self.narrate(
            id="hook_01",
            text="You have ninety seconds for a three-blank passage. When the city's metro opened in twenty nineteen, few "
                 "people used it. The stations were far from residential areas, blank one the fares were high. The "
                 "authorities blank two introduced feeder buses and cut fares by a third. Ridership has blank three "
                 "tripled since then.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ninety")
        self.play(FadeIn(c, shift=UP * 0.3), Create(timer[0]), FadeIn(timer[1]))
        for k, spoken in [(1, "one"), (2, "two"), (3, "three")]:
            self.at_word(n, spoken)
            self.play(Indicate(self.blank(c, k), color=FOCUS), run_time=0.5)
        self.wait_for_narration(n)

        self.hook_question(
            "hook_02", "Which option fits blank two? (a) therefore, (b) however, (c) meanwhile, or (d) instead.",
            "Which option fits blank (2)?", HOOK_OPTIONS, ["Which", "therefore", "however", "meanwhile", "instead"], c)

        self.clear_stage()
        self.scene_end("S01_hook")

    # =========================================== 2. OBJECTIVES ==========

    def objectives(self):
        self.std_list(
            "S02_objectives", "Objectives", "In this video", GOOD, "board",
            [("Solve a full cloze passage with one fixed method", G_),
             ("Finish each blank in about 30 to 40 seconds", R_)],
            "obj_01",
            "In this video, you'll learn to solve a full cloze passage with one fixed method, and to finish each blank in "
            "about thirty to forty seconds.",
            ["solve", "finish"])

    # =========================================== 3. CONTINUITY ==========
    # 3D: Videos 1-7 merge into one method slab.

    def continuity(self):
        self.scene_start("S03_continuity", title="Continuity")

        heading = self.heading("This video closes Module 3", HINT)

        tiles = VGroup(*[
            slab_tile(f"Video {k}", MUTED, 1.55, 0.75, LABEL, depth=0.15)
            for k in range(1, 8)
        ])
        tiles.arrange(RIGHT, buff=0.16)
        fit_width(tiles, SAFE_W - 0.7).next_to(heading, DOWN, buff=0.7).set_x(0)

        letters = VGroup(*[
            slab_tile(l, c, 1.0, 1.0, TITLE, depth=0.25)
            for l, _, _, c in STEPS_DETAIL
        ])
        letters.arrange(RIGHT, buff=0.18)
        fit_width(letters, SAFE_W - 0.9).next_to(tiles, DOWN, buff=1.0).set_x(0)

        one = text("one method", BODY, GOOD, BOLD).next_to(letters, DOWN, buff=0.3).set_x(0)

        continuity_group = VGroup(heading, tiles, letters, one)
        fit_width(continuity_group, SAFE_W - 0.3)
        continuity_group.set_x(0)
        self.validator.check_in_frame(continuity_group)

        n = self.narrate(
            id="cont_01",
            text="This video closes Module three. It combines everything from Videos one to seven into one method: "
                 "S-G-C-V-R.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "closes")
        self.play(FadeIn(heading, shift=DOWN * 0.3))
        self.at_word(n, "everything")
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.15) for t in tiles], lag_ratio=0.1))
        self.at_word(n, "S-G-C-V-R")
        self.play(*[t.copy().animate.move_to(letters).scale(0.3).set_opacity(0) for t in tiles],
                  LaggedStart(*[FadeIn(l, shift=UP * 0.2) for l in letters], lag_ratio=0.12), FadeIn(one))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_continuity")

    def concept(self):
        self.scene_start("S04_concept", title="The Concept")
        self.open_panel("The method", METHOD)

        head = self.heading("S-G-C-V-R", G_)
        letters = VGroup(*[
            slab_tile(l, c, 1.3, 1.1, TITLE, depth=0.25)
            for l, _, _, c in STEPS_DETAIL
        ])
        letters.arrange(RIGHT, buff=0.25)
        fit_width(letters, STAGE_W - 0.55)
        letters.next_to(head, DOWN, buff=0.5).set_x(STAGE_X)

        cards = []
        for _, name, detail, c in STEPS_DETAIL:
            body = VGroup(
                text(name, LABEL, c, BOLD),
                fitted_text(detail, STAGE_W - 1.0, BODY, INK, max_lines=3)
            )
            body.arrange(DOWN, buff=0.15, aligned_edge=LEFT)
            card = self.card(body, width=STAGE_W - 0.45, color=c)
            card.next_to(letters, DOWN, buff=0.6).set_x(STAGE_X)
            cards.append(card)

        concept_group = VGroup(head, letters, *cards)
        fit_width(concept_group, STAGE_W - 0.25)
        concept_group.set_x(STAGE_X)
        self.validator.check_in_frame(concept_group)

        self.play(
            FadeIn(head, shift=DOWN * 0.3),
            LaggedStart(*[FadeIn(l, shift=UP * 0.2) for l in letters], lag_ratio=0.1)
        )
        self.play(letters.animate.set_opacity(0.35))

        lines = [("c_01", "S, skim. Read the whole passage through the blanks: topic, tone, structure, turns.", "whole"),
                 ("c_02", "G, grammar blanks. Solve every blank whose options are grammar variants.", "variants"),
                 ("c_03", "C, connector blanks. Name the relationship between sentences, and fill the connectors.",
                  "relationship"),
                 ("c_04", "V, vocabulary blanks. Grammar, then passage logic, then precision.", "precision"),
                 ("c_05", "R, re-read. Read the full passage with every answer in place. Does it flow, with a consistent "
                          "tense, tone and logic?", "flow")]
        prev = None
        for k, (letter, card, (nid, line, spoken)) in enumerate(zip(letters, cards, lines)):
            n = self.narrate(id=nid, text=line, voice="default", subtitle=True)
            anims = [letter.animate.set_opacity(1), Indicate(letter, scale_factor=1.08)]
            if prev is not None:
                anims.append(FadeOut(prev))
            self.play(*anims)
            self.at_word(n, spoken)
            self.play(FadeIn(card, shift=UP * 0.15))
            self.wait_for_narration(n)
            self.add_row(k, letter)
            prev = card

        self.clear_stage()
        self.scene_end("S04_concept")

    def why_you_need_it(self):
        self.scene_start("S05_why", title="Why You Need It")

        heading = self.heading("Why a method", GOOD)
        chips = VGroup(*[pill(f"({k})", MUTED, SMALL, 0.05) for k in range(1, 11)]).arrange(RIGHT, buff=0.2)
        fit_width(chips, STAGE_W - 0.4).next_to(heading, DOWN, buff=0.6).set_x(STAGE_X)
        saves = pill("a method saves minutes", G_, BODY).next_to(chips, DOWN, buff=0.5).set_x(STAGE_X)
        trap = slab_tile("fits its sentence, not the story", BAD, 5.2, 0.9, LABEL).next_to(saves, DOWN, buff=0.6)
        trap.set_x(STAGE_X)
        catch = pill("R, the re-read, catches it", R_, BODY).next_to(trap, DOWN, buff=0.4).set_x(STAGE_X)
        self.validator.check_in_frame(VGroup(heading, chips, saves, trap, catch))

        n = self.narrate(
            id="why_01",
            text="With five to ten questions per passage, a method saves minutes, and the re-read catches the one blank "
                 "that fits its sentence but not the story.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(heading, shift=DOWN * 0.3))
        self.at_word(n, "five")
        self.play(LaggedStart(*[FadeIn(ch) for ch in chips], lag_ratio=0.06))
        self.at_word(n, "saves")
        self.play(FadeIn(saves, shift=UP * 0.1), self.all_lit())
        self.at_word(n, "fits")
        self.play(FadeIn(trap, shift=UP * 0.2), chips[6].animate.set_color(BAD))
        self.at_word(n, "story")
        self.play(FadeIn(catch, shift=UP * 0.1), self.light(4))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_why")

    # ============================================= 6. THE ANALOGY ==========
    # 3D: parts checked one by one, then the assembled machine switched on.

    def analogy(self):
        self.scene_start("S06_analogy", title="The Analogy")

        heading = self.heading("A quality inspector", FOCUS)

        parts = VGroup(*[
            slab_tile(s, MUTED, 1.7, 0.75, LABEL, depth=0.15)
            for s in ("part 1", "part 2", "part 3")
        ])
        parts.arrange(RIGHT, buff=0.2)
        fit_width(parts, STAGE_W - 2.0)
        parts.next_to(heading, DOWN, buff=0.6).set_x(STAGE_X - 0.65)

        inspector = person(FOCUS, 0.8).next_to(parts, RIGHT, buff=0.3)
        ticks = VGroup(*[
            text("✓", BODY, GOOD, BOLD).next_to(p, UP, buff=0.1)
            for p in parts
        ])

        machine = Slab(3.8, 1.3, R_, depth=0.28, fill=CELL)
        machine.next_to(parts, DOWN, buff=0.75).set_x(STAGE_X - 0.25)

        gear = VGroup(
            Circle(radius=0.42, stroke_color=R_, stroke_width=5),
            *[
                Line(ORIGIN, UP * 0.42, color=R_, stroke_width=4).rotate(
                    a, about_point=ORIGIN
                )
                for a in np.linspace(0, TAU, 6, endpoint=False)
            ]
        )
        gear.move_to(machine.front.get_center() + LEFT * 0.95)

        switch = pill("ON", R_, LABEL).move_to(machine.front.get_center() + RIGHT * 0.9)

        # Keep the "runs smoothly?" label above the machine instead of extending
        # the entire machine group past the right edge.
        smooth = pill("runs smoothly?", R_, SMALL).next_to(machine, UP, buff=0.25)
        smooth.align_to(machine, RIGHT)
        cap = pill("R = switching the machine on", R_, BODY).next_to(
            machine, DOWN, buff=0.35
        ).set_x(STAGE_X)

        analogy_group = VGroup(
            heading, parts, inspector, ticks, machine, gear, switch, smooth, cap
        )
        fit_width(analogy_group, STAGE_W - 0.3)
        analogy_group.set_x(STAGE_X)
        self.validator.check_in_frame(analogy_group)

        n = self.narrate(
            id="an_01",
            text="An inspector checks each part, then switches on the assembled machine to see if it runs smoothly. R is "
                 "switching the machine on.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(heading, shift=DOWN * 0.3))
        self.at_word(n, "inspector")
        self.play(FadeIn(inspector), LaggedStart(*[FadeIn(p, shift=UP * 0.15) for p in parts], lag_ratio=0.15))
        self.at_word(n, "part")
        self.play(LaggedStart(*[FadeIn(t, scale=1.3) for t in ticks], lag_ratio=0.2), self.light(1, 2, 3))
        self.at_word(n, "switches")
        self.play(FadeIn(machine, shift=UP * 0.2), FadeIn(gear), FadeIn(switch))
        self.at_word(n, "smoothly")
        self.play(Rotate(gear, angle=TAU, rate_func=linear), FadeIn(smooth), run_time=1.2)
        self.at_word(n, "R")
        self.play(FadeIn(cap, shift=UP * 0.1), self.light(4))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_analogy")

    def worked_examples(self):
        self.std_worked([(
            "Worked example: blanks (1) and (3) of the hook",
            ["The stations were far from residential areas, (1) ____ the fares were high.",
             "Ridership has (3) ____ tripled since then."],
            [("(1): a second problem → addition → and", C_), ("(3): an adverb of degree → nearly", V_)],
            "we_01",
            "Blank one, in the hook: far from residential areas, blank one, the fares were high. That's the addition of a "
            "second problem, so: and. Blank three: ridership has blank three tripled since then. That needs an adverb of "
            "degree: nearly.",
            [("addition", "mark", "far from residential areas", C_), ("addition", "light", 2), ("addition", "note", 0),
             ("and", "fill", 1, "and"), ("degree", "note", 1), ("degree", "light", 3),
             ("nearly", "fill", 3, "nearly")])])

    # ================================================== 8. RULES ==========

    def rules(self):
        self.std_table(
            "S08_rules", "Rules", "Rules: the method and its time", FOCUS,
            [("S", "15–20 s", S_), ("Each blank", "20–40 s", G_), ("R", "15 s", R_)],
            "rules_01",
            "The rules. S, G, C, V, R: skim, grammar, connectors, vocabulary, re-read. And the time: fifteen to twenty "
            "seconds to skim, twenty to forty seconds for each blank, and fifteen seconds for the re-read.",
            [("skim", 2), "each", ("re-read", 2)], [(0,), (1, 2, 3), (4,)],
            banner="S (skim) → G (grammar) → C (connectors) → V (vocabulary) → R (re-read)")

    # ================================================ 9. THE PROCESS ======

    def process(self):
        self.std_list(
            "S09_process", "The Process", "The process", GOOD, "stairs",
            [("Skim the passage.", S_), ("Solve blanks in the order G → C → V, not in number order.", G_),
             ("Skip any blank still unclear; return.", SOFT), ("Re-read the complete passage.", R_)],
            "process_01",
            "The process. Skim the passage. Solve the blanks in the order G, C, V, not in number order. Skip any blank "
            "that's still unclear, and return. And re-read the complete passage.",
            ["Skim", "order", "Skip", "re-read"], [(0,), (1, 2, 3), None, (4,)])

    # =============================================== 10. HOOK, SOLVED ======

    def hook_solved(self):
        self.std_hook_solved(
            HOOK_PASSAGE[1:], HOOK_OPTIONS,
            ("hs_01", "Back to the hook. S: low ridership, two problems, the authorities act, and ridership rises.",
             [("problems", "mark", "far from residential areas", BAD), ("act", "mark", "introduced feeder buses", S_),
              ("rises", "mark", "tripled", GOOD)]),
            ("hs_02", "C: blank two is the authorities' action, a response to the problems, so a result.", "result",
             "the authorities' action = a response to the problems → result", (2,)),
            ("hs_03", "Eliminate: (b) however signals contrast, but the action follows logically from the problems. (c) "
                      "meanwhile is about time. (d) instead implies replacing something.",
             [("however", 1, "✗  (b) contrast"), ("meanwhile", 2, "✗  (c) time"),
              ("instead", 3, "✗  (d) replacing something")]),
            ("hs_04", "Confirm: The authorities therefore introduced feeder buses and cut fares by a third. The answer is "
                      "(a). Then R, the re-read: far from residential areas, and the fares were high. The authorities "
                      "therefore introduced feeder buses. Ridership has nearly tripled since then. It flows.",
             "therefore", 2, "therefore", 0, [("residential", 1, "and"), ("nearly", 3, "nearly")]),
            steps=["S · SKIM", "C · PREDICT", "ELIMINATE", "CONFIRM · R"])

    # ========================================= 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.std_list(
            "S11_patterns", "Exam Patterns and Solving Models", "Exam patterns", FOCUS, "patterns",
            [("5–10 blanks, one passage", "S-G-C-V-R", G_), ("Blank unclear", "Skip; solve the others; return.", SOFT),
             ("Final check", "Re-read the whole passage.", R_)],
            "patterns_01",
            "Three exam patterns. Five to ten blanks in one passage: S-G-C-V-R. A blank that's unclear: skip it, solve the "
            "others, and return. And the final check: re-read the whole passage.",
            ["five", "unclear", "final"], [(0, 1, 2, 3, 4), None, (4,)])

    # ======================================== 12. COMMON MISTAKES =========

    def common_mistakes(self):
        self.std_list(
            "S12_mistakes", "Common Mistakes", "Three common mistakes", BAD, "mistakes",
            ["Solving strictly in number order", "Skipping the final re-read", "Spending more than 60 seconds on one blank"],
            "mistakes_01",
            "Three common mistakes. Solving strictly in number order. Skipping the final re-read. And spending more than "
            "sixty seconds on one blank.",
            ["Solving", "Skipping", "spending"], [(1, 2, 3), (4,), None])

    # ================================================ 13. PRACTICE ==========

    def practice(self):
        self.std_practice(
            ["Water scarcity is a (1) ____ problem in many Indian cities.",
             "Groundwater levels have fallen sharply, (2) ____ several lakes have dried up.",
             "Some cities (3) ____ begun recycling wastewater for industrial use."],
            ["Blank (1):   (a) solved   (b) minor   (c) imaginary   (d) growing",
             "Blank (2):   (a) but   (b) although   (c) and   (d) unless",
             "Blank (3):   (a) has   (b) have   (c) having   (d) is"],
            ["Now try this passage. Water scarcity is a blank one problem in many Indian cities. Groundwater levels have "
             "fallen sharply, blank two several lakes have dried up. Some cities blank three begun recycling wastewater "
             "for industrial use.",
             "Blank one: (a) solved, (b) minor, (c) imaginary, or (d) growing.",
             "Blank two: (a) but, (b) although, (c) and, or (d) unless.",
             "Blank three: (a) has, (b) have, (c) having, or (d) is."],
            ["Water", "solved", "although", "having"])

    # ================================================= 14. ANSWERS ==========

    def answers(self):
        self.std_answers([
            (1, "growing", "(d) growing: the evidence shows a worsening problem", "answers_01",
             "Blank one: (d), growing. The evidence shows a worsening problem.", "worsening", (3,)),
            (2, "and", "(c) and: two similar problems", "answers_02",
             "Blank two: (c), and. Two similar problems.", "similar", (2,)),
            (3, "have", '(b) have: "Some cities" is plural', "answers_03",
             "Blank three: (b), have. Some cities is plural.", "plural", (1,))])

    # ============================================== 15. RECAP AND NEXT ====

    def recap(self):
        self.std_recap(
            "Recap card: the Lesson 13 method",
            [("Method", "S → G → C → V → R", G_),
             ("Order", "Grammar, then connectors, then vocabulary; not number order.", V_),
             ("Re-read", "Always, with every answer in place.", R_)],
            "recap_01",
            "To recap the Lesson thirteen method. S, G, C, V, R. The order: grammar, then connectors, then vocabulary; not "
            "number order. And the re-read: always, with every answer in place.",
            ["S", "order", "re-read"])
        self.std_next(
            "Take the Lesson thirteen Quiz, and keep the Cheat Sheet. Module three is complete. Module four brings "
            "everything together in Lesson fourteen: Reading Comprehension.",
            [("Quiz", "Take the Lesson 13 Quiz", G_), ("Cheat", "Keep the Cheat Sheet", S_),
             ("complete", "Module 3: Verbal Ability  ✓ complete", GOOD),
             ("four", "Next: Module 4 · Lesson 14 · Reading Comprehension", V_)])
