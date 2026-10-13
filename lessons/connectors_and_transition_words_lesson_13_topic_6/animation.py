"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - English
Module : Module 3 - Verbal Ability
Lesson : Lesson 13 - Cloze Test (Fill in the Blanks)
Topic  : Video 6 of 8 - Connectors and Transition Words (Core, about 5 min)

Source script:
  06 - Connectors and Transition Words.pdf
  Prose narrated closely; headings become scenes. Blanks are read aloud as
  "blank one", "blank two". Answers checked: hook (b) However; worked
  Moreover, As a result, For example; practice (d) Moreover, (c) However.

Golden-reference pattern: one ``LMSScene`` class, narration as the timeline,
one method per section, zone constants and ``fitted_text`` for all text.

House rules:
  * a visual beat for every meaningful sentence and key word;
  * pinned CONNECTOR FAMILIES panel (left: contrast, result, addition,
    example, time) from The Concept to the recap; each family is added as it
    is taught and lights up when used;
  * drawn 3D: the sentence strips and their joint, the family tiles, the
    passage chain, the relay track;
  * passages are real cloze cards: blanks are filled in place.

Section map:
  S00 You are here   S01 Hook (annual report)   S02 Objectives   S03 Continuity
  S04 The Concept    S05 Why You Need It   S06 The Analogy (relay baton)
  S07 Worked Examples  S08 Rules  S09 The Process  S10 Hook, Solved
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

CONTRAST = TURN
RESULT = GOOD
ADD = HINT
EXAMPLE = ACCENT
TIME = FOCUS

FAMILIES = [("Contrast: however, yet", CONTRAST), ("Result: therefore, thus", RESULT),
            ("Addition: moreover, also", ADD), ("Example: for example", EXAMPLE), ("Time: then, later, meanwhile", TIME)]

FAMILY_ROWS = [("Contrast", "goes against the previous one", ["however", "nevertheless", "on the other hand", "yet"],
                CONTRAST),
               ("Result", "follows from the previous one", ["therefore", "as a result", "consequently", "thus"], RESULT),
               ("Addition", "adds a similar point", ["moreover", "furthermore", "in addition", "also"], ADD),
               ("Example", "illustrates the previous one", ["for example", "for instance"], EXAMPLE),
               ("Time", "comes later or at the same time", ["then", "later", "eventually", "meanwhile"], TIME)]

HOOK_PASSAGE = ["The company's revenue grew by 20 percent this year.",
                "(1) ____, its profits fell because of rising raw-material costs."]
HOOK_OPTIONS = ["(a) Therefore", "(b) However", "(c) Moreover", "(d) For example"]


class ConnectorBlanksVideo(LMSScene):
    lesson_title = "Connectors and Transition Words"

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
            "Connectors and Transition Words", 6, "Core · about 5 min", "Vocabulary-Based Blanks", "Elimination Techniques",
            "This is Lesson thirteen, Video six of eight: Connectors and Transition Words, a five-minute core video.",
            ["eight", "Connectors"],
            "It follows Vocabulary-Based Blanks, and leads into Elimination Techniques.")

    # ================================================= 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        c = self.cloze_card(HOOK_PASSAGE, header="Annual report", color=HINT)
        c.move_to(UP * (CARD_TOP - c.height / 2))
        self.validator.check_in_frame(c)
        n = self.narrate(
            id="hook_01",
            text="An annual report says: The company's revenue grew by twenty percent this year. Blank one, its profits "
                 "fell because of rising raw-material costs.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "report")
        self.play(FadeIn(c, shift=UP * 0.3))
        self.at_word(n, "one")
        self.play(Indicate(self.blank(c, 1), color=FOCUS))
        self.wait_for_narration(n)

        self.hook_question(
            "hook_02", "Which option fits? (a) Therefore, (b) However, (c) Moreover, or (d) For example.",
            "Which option fits?", HOOK_OPTIONS, ["Which", "Therefore", "However", "Moreover", "example"], c)

        self.clear_stage()
        self.scene_end("S01_hook")

    # =========================================== 2. OBJECTIVES ==========

    def objectives(self):
        self.std_list(
            "S02_objectives", "Objectives", "In this video", GOOD, "board",
            [("Choose connectors that link sentences in a passage", TIME),
             ("Identify the relationship between two sentences quickly", CONTRAST)],
            "obj_01",
            "In this video, you'll learn to choose connectors that link sentences in a passage, and to identify the "
            "relationship between two sentences quickly.",
            ["choose", "identify"])

    # =========================================== 3. CONTINUITY ==========

    def continuity(self):
        self.scene_start("S03_continuity", title="Continuity")

        heading = self.heading("Connectors, a third time", HINT)
        l11 = slab_tile("Lesson 11 · Video 6: ordering sentences", MUTED, 4.6, 0.8, LABEL, depth=0.18)
        l12 = slab_tile("Lesson 12 · Video 6: within a sentence", MUTED, 4.6, 0.8, LABEL, depth=0.18)
        left = VGroup(l11, l12).arrange(DOWN, buff=0.3).next_to(heading, DOWN, buff=0.6).to_edge(LEFT, buff=SAFE + 0.2)
        s1 = slab_tile("sentence 1", MUTED, 4.0, 0.7, LABEL, depth=0.18)
        joint = pill("connector", TIME, LABEL)
        s2 = slab_tile("sentence 2", MUTED, 4.0, 0.7, LABEL, depth=0.18)
        right = VGroup(s1, joint, s2).arrange(DOWN, buff=0.2).next_to(heading, DOWN, buff=0.5)
        right.to_edge(RIGHT, buff=SAFE + 0.5)
        here = text("Here: it links two sentences", SMALL, TIME, BOLD).next_to(right, DOWN, buff=0.25)
        self.validator.check_in_frame(VGroup(heading, left, right, here))

        n = self.narrate(
            id="cont_01",
            text="Lesson eleven, Video six used connectors to order sentences. Lesson twelve, Video six chose connectors "
                 "within a sentence. Here, the connector links two sentences in a passage.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(heading, shift=DOWN * 0.3))
        self.at_word(n, "eleven")
        self.play(FadeIn(l11, shift=UP * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(l12, shift=UP * 0.2))
        self.at_word(n, "links")
        self.play(FadeIn(s1, shift=DOWN * 0.2), FadeIn(s2, shift=UP * 0.2))
        self.play(FadeIn(joint, scale=1.2), FadeIn(here))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_continuity")

    # ============================================= 4. THE CONCEPT ==========

    def concept(self):
        self.scene_start("S04_concept", title="The Concept")
        self.open_panel("Connector families", FAMILIES)

        head = self.heading("One question", TIME)
        s1 = slab_tile("previous sentence", MUTED, 5.0, 0.7, LABEL, depth=0.18)
        s2 = slab_tile("(1) ____ , new sentence …", FOCUS, 5.0, 0.7, LABEL, depth=0.18)
        pair = VGroup(s1, s2).arrange(DOWN, buff=0.5).next_to(head, DOWN, buff=0.6).set_x(STAGE_X - 1.0)
        link = CurvedArrow(s2.get_right() + RIGHT * 0.1, s1.get_right() + RIGHT * 0.1, angle=PI / 2, color=TIME,
                           stroke_width=4)
        q = self.card(fitted_text("How does this sentence relate to the previous one?", STAGE_W - 0.8, BODY, TIME, BOLD,
                                  max_lines=2), width=STAGE_W - 0.2, color=TIME)
        q.next_to(pair, DOWN, buff=0.5).set_x(STAGE_X)
        self.validator.check_in_frame(VGroup(head, pair, q))
        n = self.narrate(
            id="c_01",
            text="A connector blank at the start of a sentence asks one question: how does this sentence relate to the "
                 "previous one?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.3), FadeIn(s1, shift=UP * 0.2))
        self.at_word(n, "start")
        self.play(FadeIn(s2, shift=UP * 0.2))
        self.at_word(n, "relate")
        self.play(Create(link), FadeIn(q, shift=UP * 0.15))
        self.wait_for_narration(n)
        self.clear_stage()

        # The five families.
        head = self.heading("Five relationships", ACCENT)
        rows = VGroup()
        for name, what, words, c in FAMILY_ROWS:
            tile = slab_tile(name, c, 1.9, 0.62, LABEL, depth=0.15)
            body = VGroup(text(what, SMALL, MUTED, BOLD),
                          VGroup(*[pill(w, c, SMALL, 0.06) for w in words]).arrange(RIGHT, buff=0.12))
            body.arrange(DOWN, buff=0.08, aligned_edge=LEFT)
            fit_width(body, STAGE_W - 2.5)
            rows.add(VGroup(tile, body).arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, buff=0.2, aligned_edge=LEFT).next_to(head, DOWN, buff=0.3).set_x(STAGE_X)
        self.validator.check_in_frame(VGroup(head, rows))
        n = self.narrate(
            id="c_02",
            text="Contrast: the new sentence goes against the previous one: however, nevertheless, on the other hand, yet. "
                 "Result: the new sentence follows from the previous one: therefore, as a result, consequently, thus. "
                 "Addition: the new sentence adds a similar point: moreover, furthermore, in addition, also.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.3))
        for k, spoken in enumerate(["Contrast", "Result", "Addition"]):
            self.at_word(n, spoken)
            self.play(FadeIn(rows[k], shift=RIGHT * 0.2), run_time=0.5)
            self.add_row(k, rows[k][0])
        self.wait_for_narration(n)
        n = self.narrate(
            id="c_03",
            text="Example: the new sentence illustrates the previous one: for example, for instance. Time: the new sentence "
                 "comes later, or at the same time: then, later, eventually, meanwhile.",
            voice="default",
            subtitle=True,
        )
        for k, spoken in [(3, "Example"), (4, "Time")]:
            self.at_word(n, spoken)
            self.play(FadeIn(rows[k], shift=RIGHT * 0.2), run_time=0.5)
            self.add_row(k, rows[k][0])
        self.wait_for_narration(n)
        self.clear_stage()

        # Three-word summaries.
        head = self.heading("The trick: three words each", FOCUS)
        up = VGroup(slab_tile("revenue up", GOOD, 3.2, 1.0, BODY), Arrow(DOWN * 0.4, UP * 0.4, color=GOOD, buff=0))
        down = VGroup(slab_tile("profits down", BAD, 3.2, 1.0, BODY), Arrow(UP * 0.4, DOWN * 0.4, color=BAD, buff=0))
        for g in (up, down):
            g[1].next_to(g[0], RIGHT, buff=0.2)
        summ = VGroup(up, down).arrange(RIGHT, buff=0.9).next_to(head, DOWN, buff=0.8).set_x(STAGE_X)
        verdict = pill("relationship: contrast", CONTRAST, BODY).next_to(summ, DOWN, buff=0.7).set_x(STAGE_X)
        self.validator.check_in_frame(VGroup(head, summ, verdict))
        n = self.narrate(
            id="c_04",
            text="Summarise both sentences in three words each: revenue up, profits down. The relationship becomes obvious: "
                 "contrast.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.3))
        self.at_word(n, "revenue")
        self.play(FadeIn(up, shift=UP * 0.2))
        self.at_word(n, "profits")
        self.play(FadeIn(down, shift=DOWN * 0.2))
        self.at_word(n, "contrast")
        self.play(FadeIn(verdict, scale=1.1), self.light(0))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_concept")

    # ========================================== 5. WHY YOU NEED IT =========

    def why_you_need_it(self):
        self.scene_start("S05_why", title="Why You Need It")

        heading = self.heading("Connectors carry the logic", BAD)
        strips = VGroup(*[slab_tile(f"sentence {k}", MUTED, 4.2, 0.55, SMALL, depth=0.15) for k in range(1, 5)])
        joints = VGroup(*[pill(w, c, SMALL) for w, c in [("however", CONTRAST), ("therefore", RESULT),
                                                          ("moreover", ADD)]])
        chain = VGroup()
        for k in range(4):
            chain.add(strips[k])
            if k < 3:
                chain.add(joints[k])
        chain.arrange(DOWN, buff=0.1).next_to(heading, DOWN, buff=0.35).set_x(STAGE_X - 1.2)
        freq = pill("among the most frequent blanks", ADD, SMALL).next_to(chain, RIGHT, buff=0.4).shift(UP * 0.9)
        wrong = pill("one wrong → the whole passage misreads", BAD, SMALL).next_to(chain, RIGHT, buff=0.4).shift(DOWN * 0.6)
        fit_width(freq, STAGE_RIGHT - chain.get_right()[0] - 0.5)
        fit_width(wrong, STAGE_RIGHT - chain.get_right()[0] - 0.5)
        freq.next_to(chain, RIGHT, buff=0.4).shift(UP * 0.9)
        wrong.next_to(chain, RIGHT, buff=0.4).shift(DOWN * 0.6)
        self.validator.check_in_frame(VGroup(heading, chain, freq, wrong))

        n = self.narrate(
            id="why_01",
            text="Connector blanks are among the most frequent in cloze passages, and they carry the passage's logic. Get "
                 "them wrong and the whole passage reads incorrectly.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(heading, shift=DOWN * 0.3))
        self.at_word(n, "frequent")
        self.play(FadeIn(strips, shift=UP * 0.15), FadeIn(freq, shift=LEFT * 0.1))
        self.at_word(n, "logic")
        self.play(LaggedStart(*[FadeIn(j, scale=1.2) for j in joints], lag_ratio=0.2), self.all_lit())
        self.at_word(n, "wrong")
        self.play(joints[1].animate.set_color(BAD), Wiggle(joints[1]))
        self.at_word(n, "incorrectly")
        self.play(strips.animate.set_opacity(0.35), FadeIn(wrong, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_why")

    # ============================================= 6. THE ANALOGY ==========
    # 3D: a relay track; the handover decides the direction.

    def analogy(self):
        self.scene_start("S06_analogy", title="The Analogy")

        heading = self.heading("The baton handover", FOCUS)
        track = Slab(STAGE_W - 1.0, 0.5, MUTED, depth=0.3, fill=CELL).next_to(heading, DOWN, buff=1.6).set_x(STAGE_X)
        x_mid = track.front.get_x()
        r1 = person(MUTED, 0.9).next_to(track.front, UP, buff=0.05).set_x(x_mid - 0.7)
        r2 = person(FOCUS, 0.9).next_to(track.front, UP, buff=0.05).set_x(x_mid + 0.7)
        baton = RoundedRectangle(corner_radius=0.04, width=0.45, height=0.12, stroke_width=0, fill_color=FOCUS,
                                 fill_opacity=1).move_to(r1.get_right() + RIGHT * 0.15)
        y_lab = track.front.get_bottom()[1] - 0.6
        same = VGroup(Arrow(LEFT * 0.6, RIGHT * 0.6, color=ADD, buff=0), text("Moreover: same direction", SMALL, ADD, BOLD))
        same.arrange(DOWN, buff=0.1)
        back = VGroup(CurvedArrow(RIGHT * 0.5, LEFT * 0.5, angle=-PI, color=CONTRAST),
                      text("However: turns back", SMALL, CONTRAST, BOLD)).arrange(DOWN, buff=0.1)
        finish = VGroup(pill("FINISH: a result", RESULT, SMALL), text("Therefore", SMALL, RESULT, BOLD))
        finish.arrange(DOWN, buff=0.1)
        outcomes = VGroup(same, back, finish).arrange(RIGHT, buff=0.6)
        fit_width(outcomes, STAGE_W - 0.4).move_to(RIGHT * STAGE_X + UP * (y_lab - outcomes.height / 2))
        self.validator.check_in_frame(VGroup(heading, track, r1, r2, outcomes))

        n = self.narrate(
            id="an_01",
            text="A connector is the baton handover between two runners. Moreover keeps running in the same direction. "
                 "However turns back. Therefore runs to the finish line of a result.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(heading, shift=DOWN * 0.3), FadeIn(track, shift=UP * 0.2))
        self.at_word(n, "baton")
        self.play(FadeIn(r1), FadeIn(r2), FadeIn(baton))
        self.play(baton.animate.move_to(r2.get_left() + LEFT * 0.15))
        self.at_word(n, "Moreover")
        self.play(FadeIn(same, shift=RIGHT * 0.2), self.light(2))
        self.at_word(n, "However")
        self.play(FadeIn(back, shift=LEFT * 0.2), self.light(0))
        self.at_word(n, "Therefore")
        self.play(FadeIn(finish, shift=UP * 0.2), self.light(1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_analogy")

    # ======================================= 7. WORKED EXAMPLES ==========

    def worked_examples(self):
        self.std_worked([
            ("Worked example 1", ["The software is free.", "(1) ____, it works offline."],
             [("two advantages → Moreover", ADD)],
             "we_01",
             "The software is free. Blank one, it works offline. Two advantages, so: moreover.",
             [("advantages", "mark", "free", ADD), ("advantages", "mark", "works offline", ADD),
              ("advantages", "note", 0), ("moreover", "fill", 1, "Moreover"), ("moreover", "light", 2)]),
            ("Worked example 2", ["The roads were flooded.", "(2) ____, schools were closed."],
             [("cause → effect → As a result", RESULT)],
             "we_02",
             "The roads were flooded. Blank two, schools were closed. Cause, then effect, so: as a result.",
             [("Cause", "mark", "flooded", RESULT), ("effect", "mark", "schools were closed", RESULT),
              ("effect", "note", 0), ("result", "fill", 2, "As a result"), ("result", "light", 1)]),
            ("Worked example 3",
             ["Many fruits are rich in vitamin C.", "(3) ____, an orange provides a full day's requirement."],
             [("a general claim, then one case → For example", EXAMPLE)],
             "we_03",
             "Many fruits are rich in vitamin C. Blank three, an orange provides a full day's requirement. A general claim, "
             "then one case that illustrates it, so: for example.",
             [("claim", "mark", "Many fruits", EXAMPLE), ("illustrates", "mark", "an orange", EXAMPLE),
              ("illustrates", "note", 0), (("example", 1), "fill", 3, "For example"), (("example", 1), "light", 3)])])

    # ================================================== 8. RULES ==========

    def rules(self):
        self.std_table(
            "S08_rules", "Rules", "Relationship → connectors", FOCUS,
            [("Contrast", "however, nevertheless, on the other hand, yet", CONTRAST),
             ("Result", "therefore, as a result, consequently, thus", RESULT),
             ("Addition", "moreover, furthermore, in addition", ADD), ("Example", "for example, for instance", EXAMPLE),
             ("Time", "then, later, eventually, meanwhile", TIME)],
            "rules_01",
            "The connector families. Contrast: however, nevertheless, on the other hand, yet. Result: therefore, as a "
            "result, consequently, thus. Addition: moreover, furthermore, in addition. Example: for example, for instance. "
            "And time: then, later, eventually, meanwhile.",
            ["Contrast", "Result", "Addition", "Example", "time"], [(0,), (1,), (2,), (3,), (4,)])

    # ================================================ 9. THE PROCESS ======

    def process(self):
        self.std_list(
            "S09_process", "The Process", "The process", GOOD, "stairs",
            [("Summarise the previous sentence in three words.", MUTED),
             ("Summarise the blank's sentence in three words.", FOCUS), ("Name the relationship.", ACCENT),
             ("Choose the matching connector.", GOOD)],
            "process_01",
            "The process. Summarise the previous sentence in three words. Summarise the blank's sentence in three words. "
            "Name the relationship. And choose the matching connector.",
            ["previous", "blank's", "Name", "choose"], [None, None, (0, 1, 2, 3, 4), None])

    # =============================================== 10. HOOK, SOLVED ======

    def hook_solved(self):
        self.std_hook_solved(
            HOOK_PASSAGE, HOOK_OPTIONS,
            ("hs_01", "Back to the hook. Read: revenue grew twenty percent. Blank one, profits fell.",
             [("grew", "mark", "revenue grew", GOOD), ("fell", "mark", "profits fell", BAD)]),
            ("hs_02", "Predict: revenue up, profits down. That's contrast.", "contrast",
             '"revenue up" / "profits down" → contrast', (0,)),
            ("hs_03", "Eliminate: (a) therefore makes the fall a result of growth. (c) moreover adds a similar point. (d) "
                      "for example illustrates.",
             [("therefore", 0, "✗  (a) makes the fall a result"), ("moreover", 2, "✗  (c) adds a similar point"),
              ("illustrates", 3, "✗  (d) illustrates")]),
            ("hs_04", "Confirm: However, its profits fell because of rising raw-material costs. The answer is (b).",
             "However", 1, "However", 1))

    # ========================================= 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.std_list(
            "S11_patterns", "Exam Patterns and Solving Models", "Exam patterns", FOCUS, "patterns",
            [("Connector at the start of a sentence", "Three-word summaries → relationship.", TIME),
             ("Two contrast options", "Check grammar: however (sentence) vs although (clause).", CONTRAST),
             ("Several connector blanks", "Keep the whole passage's logic consistent.", ADD)],
            "patterns_01",
            "Three exam patterns. A connector at the start of a sentence: three-word summaries give you the relationship. "
            "Two contrast options: check the grammar. However starts a sentence; although needs a clause. And several "
            "connector blanks: keep the whole passage's logic consistent.",
            ["start", "two", "several"], [(0, 1, 2, 3, 4), (0,), None])

    # ======================================== 12. COMMON MISTAKES =========

    def common_mistakes(self):
        self.std_list(
            "S12_mistakes", "Common Mistakes", "Three common mistakes", BAD, "mistakes",
            ['Choosing "therefore" for any link', "Confusing addition with result",
             'Using "although" at the start of a standalone sentence without a second clause'],
            "mistakes_01",
            "Three common mistakes. Choosing therefore for any link. Confusing addition with result. And using although "
            "at the start of a standalone sentence, without a second clause.",
            ["Choosing", "Confusing", "using"], [(1,), (1, 2), (0,)])

    # ================================================ 13. PRACTICE ==========

    def practice(self):
        self.std_practice(
            ["Electric cars produce no exhaust fumes.", "(1) ____, they are cheaper to run.",
             "(2) ____, their high upfront cost still keeps many buyers away."],
            ["Blank (1):   (a) However   (b) Therefore   (c) For example   (d) Moreover",
             "Blank (2):   (a) Moreover   (b) As a result   (c) However   (d) For instance"],
            ["Now try this passage. Electric cars produce no exhaust fumes. Blank one, they are cheaper to run. Blank two, "
             "their high upfront cost still keeps many buyers away.",
             "Blank one: (a) However, (b) Therefore, (c) For example, or (d) Moreover.",
             "Blank two: (a) Moreover, (b) As a result, (c) However, or (d) For instance."],
            ["Electric", "However", "Moreover"])

    # ================================================= 14. ANSWERS ==========

    def answers(self):
        self.std_answers([
            (1, "Moreover", "(d) Moreover: a second advantage", "answers_01",
             "Blank one: (d), moreover. It's a second advantage.", "second", (2,)),
            (2, "However", "(c) However: a drawback after advantages", "answers_02",
             "Blank two: (c), however. A drawback after the advantages.", "drawback", (0,))])

    # ============================================== 15. RECAP AND NEXT ====

    def recap(self):
        self.std_recap(
            "Recap card: Video 6",
            [("Question", "How does this sentence relate to the previous one?", TIME),
             ("Trick", "Three-word summary of each sentence.", HINT),
             ("Families", "contrast · result · addition · example · time", ACCENT)],
            "recap_01",
            "To recap. The question: how does this sentence relate to the previous one? The trick: a three-word summary "
            "of each sentence. And the families: contrast, result, addition, example and time.",
            ["question", "trick", "families"])
        self.std_next(
            "Video seven puts grammar, vocabulary and connectors together into an elimination order for the whole passage.",
            [("grammar", "grammar · vocabulary · connectors", FOCUS),
             ("elimination", "Next: Video 7 · Elimination Techniques", GOOD)])
