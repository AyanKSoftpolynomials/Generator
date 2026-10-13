"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 1 - Synonyms
Video  : 01 - Introduction to Synonyms (Video 1 of 6)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 1 - Synonyms\\01 - Introduction to Synonyms.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``.

Opening: first video of the Vocabulary module. The module > lesson > video
trail is shown on screen (silent); the narration links back to the Why
English introduction (READ > PREDICT > ELIMINATE > CONFIRM) and the
prerequisite page (part of speech, connotation, register, word parts), then
the title and the objectives. No spoken course welcome.

Core visual: an ``OptionQuestion`` card (WORD + options a-d). Wrong options
are struck through with the reason tagged beside them; the key is boxed in
green. Every question's key and trap reasons are stored with the question and
checked when it is built.

Section map (script heading -> scene):
  S00 Intro (trail + continuity)     S09 The Process
  S01 Hook                           S10 Hook, Solved
  S02 The Concept                    S11 Exam Patterns and Solving Models
  S03 Why You Need It                S12 Common Mistakes
  S04 The Analogy                    S13 Practice Questions
  S05-S07 Worked Examples 1-3        S14 Answers
  S08 Rules                          S15 Recap Card / S16 Next
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

class IntroductionToSynonymsVideo(LMSScene):
    lesson_title = "Introduction to Synonyms"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_abundant()
        self.example_lucid()
        self.example_diligent()
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

    def run_question(self, q, pos_):
        """Place an OptionQuestion's group and return it (clear of the pinned panel)."""
        q.group.move_to(pos_)
        if getattr(self, "pinned", None) is not None:
            self.no_overlap(q.group, self.pinned)
        return q.group

    # ========================================= 0. LESSON INTRO ==========
    # First video of the Vocabulary module: silent trail, one line on where we
    # come from (the Why English introduction and the prerequisite page), the
    # title and the objectives. No spoken course welcome.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 1 · Synonyms", "Video 1")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        strip = process_strip().move_to(UP * 1.2)
        fit_width(strip, SAFE_W)
        tools = VGroup(*[pill(t, c, size=SMALL) for t, c in [("part of speech", WORD), ("connotation", "#F48FB1"),
                                                            ("register", RATIO), ("word parts", SECOND)]])
        tools.arrange(RIGHT, buff=0.35).move_to(DOWN * 0.6)
        fit_width(tools, SAFE_W)
        self.validator.check_in_frame(VGroup(crumb, strip, tools))

        # SEE (silent): the trail.  HEAR: where we come from.
        n = self.narrate(
            id="intro_01",
            text="In the Why English introduction, you learned a four-step method: read, predict, eliminate, confirm. "
                 "Synonyms are the first place we use it.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "read")
        self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.2) for p in strip], lag_ratio=0.15))
        self.at_word(n, "Synonyms")
        self.play(Circumscribe(strip, color=WORD))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="The prerequisite page gave you the tools: part of speech, connotation, register and word parts.",
            voice="default",
            subtitle=True,
        )
        for chip, spoken in zip(tools, ["part", "connotation", "register", "word"]):
            self.at_word(n, spoken)
            self.play(FadeIn(chip, shift=UP * 0.15), run_time=0.4)
        self.wait_for_narration(n)

        # HEAR: today's topic.  SEE: the title.
        title = fitted_text("Introduction to Synonyms", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=WORD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        n = self.narrate(
            id="intro_03",
            text="This is lesson one of the vocabulary module: an introduction to synonyms.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(strip, tools), shift=UP * 0.3))
        self.at_word(n, "introduction")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        goals = [
            ("Explain what a synonym is, and why “closest” rarely means “identical”", WORD),
            ("Use the four-step method on a basic synonym question", GOOD),
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
            id="intro_04",
            text="By the end of this video, you'll be able to explain what a synonym is, and why closest meaning rarely "
                 "means identical meaning, and you'll use the four-step method on a basic synonym question.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["explain", "use"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="candid", options=["angry", "confused", "polite", "frank"], key="d",
                traps={"a": "a feeling, not a way of speaking", "b": "unrelated",
                       "c": "candid speech is often NOT polite"})

    def email_card(self):
        head = VGroup(text("From: client", SMALL, MUTED), text("Subject: launch update", SMALL, MUTED))\
            .arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        line = text("“To be candid, the delays have hurt our launch.”", BODY, INK, t2c={"candid": WORD})
        body = VGroup(head, fit_width(line, SAFE_W - 2.0)).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        return self.card(body, color=MUTED)

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        email = self.email_card()
        email.move_to(UP * (CARD_TOP - email.height / 2))
        h = self.HOOK
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.8).move_to(DOWN * 0.6)
        ask = pill("How upset are they?", FOCUS, size=LABEL).move_to(DOWN * 2.1)
        self.validator.check_in_frame(VGroup(email, opts, ask))

        n = self.narrate(
            id="hook_01",
            text="Your manager forwards a client email and asks, how upset are they? The key line: to be candid, the "
                 "delays have hurt our launch. What does candid mean here?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "email")
        self.play(FadeIn(email, shift=DOWN * 0.2))
        self.at_word(n, "upset")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "mean")
        self.play(Indicate(email[1][1], color=WORD, scale_factor=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Angry, confused, polite, or frank? Your reading of that one word decides how your team replies. Choose, "
                 "and we'll check it with the process.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.play(FadeOut(ask))
        for row, spoken in zip(opts, ["Angry", "confused", "polite", "frank"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        definition = pill("synonym:  same or nearly the same meaning, in context", WORD, size=BODY)
        fit_width(definition, SAFE_W).move_to(UP * 2.4)
        easy = VGroup(pair_chip("big", "large", GOOD), pair_chip("begin", "commence", GOOD)).arrange(RIGHT, buff=0.8)
        easy.move_to(UP * 1.2)
        diffs_ = VGroup(pair_chip("warm", "hot", RATIO, "intensity"),
                        pair_chip("thrifty", "stingy", "#F48FB1", "feeling"),
                        pair_chip("buy", "purchase", SECOND, "formality"),
                        VGroup(pill("strong tea  ·  powerful tea ✗", FOCUS, size=LABEL),
                               text("usage", SMALL, MUTED)).arrange(DOWN, buff=0.12))
        diffs_.arrange_in_grid(rows=2, cols=2, buff=(0.8, 0.35)).move_to(DOWN * 0.5)
        fit_width(diffs_, SAFE_W)
        most = pill("exams ask for the word MOST NEARLY the same", GOOD, size=LABEL).move_to(DOWN * 2.35)
        self.validator.check_in_frame(VGroup(definition, easy, diffs_, most))

        n = self.narrate(
            id="concept_01",
            text="A synonym is a word with the same or nearly the same meaning as another word in a given context. Big and "
                 "large are synonyms. So are begin and commence.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "synonym")
        self.play(FadeIn(definition, shift=DOWN * 0.2))
        self.at_word(n, "Big")
        self.play(FadeIn(easy[0], shift=UP * 0.1))
        self.at_word(n, "begin")
        self.play(FadeIn(easy[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_02",
            text="Here's the catch that exams rely on: true, perfectly identical synonyms are rare. Most synonym pairs "
                 "overlap in their core meaning but differ in something else: intensity, like warm and hot. Feeling, like "
                 "thrifty and stingy. Formality, like buy and purchase. Or usage: we say strong tea, but not powerful "
                 "tea.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rare")
        self.play(Indicate(easy, color=FOCUS, scale_factor=1.05))
        for chip, spoken in zip(diffs_, ["intensity", "Feeling", "Formality", "usage"]):
            self.at_word(n, spoken)
            self.play(FadeIn(chip, shift=UP * 0.1), run_time=0.45)
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_03",
            text="That's why exam questions ask for the word most nearly the same in meaning. Your job is to find the "
                 "option that shares the core meaning, and matches the word closely on those other dimensions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "most")
        self.play(FadeIn(most, scale=1.05))
        self.at_word(n, "shares")
        self.play(Indicate(definition, color=WORD, scale_factor=1.04))
        self.at_word(n, "dimensions")
        self.play(Circumscribe(diffs_, color=GOOD))
        self.wait_for_narration(n)

        # HEAR: the core meaning is the anchor.  SEE: anchor card for candid.
        anchor = VGroup(pill("candid", WORD, size=TITLE), text("→", TITLE, MUTED),
                        pill("open and honest in speech", GOOD, size=BODY)).arrange(RIGHT, buff=0.4)
        fit_width(anchor, SAFE_W).move_to(ORIGIN)
        n = self.narrate(
            id="concept_04",
            text="The core meaning is the anchor. Candid means open and honest in speech. Anything that doesn't share "
                 "that anchor is out, however familiar it looks.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(definition, easy, diffs_, most)))
        self.at_word(n, "anchor", occurrence=1)
        self.play(FadeIn(anchor[0], scale=1.1))
        self.at_word(n, "open")
        self.play(FadeIn(anchor[1:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        marks = pill("Synonyms & antonyms: reliable C-CAT English marks", GOOD, size=LABEL).move_to(UP * 1.8)
        later = VGroup(*[pill(t, c, size=LABEL) for t, c in [("Sentence Completion", WORD), ("Cloze Test", RATIO),
                                                            ("Reading Comprehension", SECOND)]]).arrange(RIGHT, buff=0.4)
        fit_width(later, SAFE_W).move_to(UP * 0.2)
        work = pill("one misread word in an email changes the whole reply", FOCUS, size=LABEL).move_to(DOWN * 1.5)
        fit_width(work, SAFE_W)
        self.validator.check_in_frame(VGroup(marks, later, work))

        n = self.narrate(
            id="why_01",
            text="Synonyms and antonyms are among the most reliable English marks in C-CAT, and the vocabulary built here "
                 "returns in sentence completion, cloze tests and reading comprehension. At work, one misread word in an "
                 "email changes the whole reply.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reliable")
        self.play(FadeIn(marks, shift=DOWN * 0.2))
        self.at_word(n, "returns")
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.15) for c in later], lag_ratio=0.3))
        self.at_word(n, "misread")
        self.play(FadeIn(work, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        circles = meaning_circles(["candid", "frank", "polite"],
                                  [LEFT * 1.2 + UP * 0.3, LEFT * 0.4 + UP * 0.3, RIGHT * 1.8 + UP * 0.3],
                                  [1.35, 1.35, 1.0], [WORD, GOOD, RATIO])
        # candid / frank labels would sit on top of each other: nudge them apart.
        circles[0][1].shift(LEFT * 0.55 + UP * 0.6)
        circles[1][1].shift(RIGHT * 0.55 + DOWN * 0.6)
        overlap = pill("synonyms: almost complete overlap", GOOD, size=SMALL)
        edge = pill("distractor: only touches the edge", RATIO, size=SMALL)
        fit_width(VGroup(overlap, edge).arrange(RIGHT, buff=0.6), SAFE_W).move_to(DOWN * 1.9)
        d_cf = np.linalg.norm(circles[0][0].get_center() - circles[1][0].get_center())
        d_fp = np.linalg.norm(circles[1][0].get_center() - circles[2][0].get_center())
        assert d_cf < 0.9 and 1.35 + 1.0 - 0.3 < d_fp < 1.35 + 1.0   # big overlap vs. a thin touch
        self.no_overlap(circles, overlap, edge)
        self.validator.check_in_frame(VGroup(circles, overlap, edge))

        n = self.narrate(
            id="analogy_01",
            text="Picture each word's meaning as a circle. Synonyms are circles that overlap almost completely.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "circle")
        self.play(Create(circles[0][0]), FadeIn(circles[0][1]))
        self.at_word(n, "overlap")
        self.play(Create(circles[1][0]), FadeIn(circles[1][1]), FadeIn(overlap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Distractors are circles that touch the edge: words that often appear near the question word in real "
                 "sentences, but mean something else. Choose by overlap, not by closeness on the page.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Distractors")
        self.play(Create(circles[2][0]), FadeIn(circles[2][1]), FadeIn(edge, shift=UP * 0.1))
        self.at_word(n, "Choose")
        cap = self.caption("Choose by overlap, not by closeness on the page", GOOD)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_abundant(self):
        self.scene_start("S05_ex_abundant", title="Worked Example 1")
        self.play(self.pin(self.steps_pin("method", [("READ the word", STEP_COLS["READ"]), ("PREDICT in your own words", STEP_COLS["PREDICT"]),
                                     ("ELIMINATE the traps", STEP_COLS["ELIMINATE"]),
                                     ("CONFIRM in a sentence", STEP_COLS["CONFIRM"])])))

        q = OptionQuestion("ABUNDANT", ["rare", "plentiful", "useful", "heavy"], "b",
                           {"a": "opposite", "c": "unrelated", "d": "unrelated"})
        group = self.run_question(q, LEFT * 2.4 + UP * 0.2)
        core = pill("core: existing in large quantities", GOOD, size=LABEL).move_to(DOWN * 2.6)
        self.validator.check_in_frame(VGroup(group, core))

        n = self.narrate(
            id="ex1_01",
            text="Abundant: rare, plentiful, useful, or heavy? The core meaning is existing in large quantities. So the "
                 "answer is plentiful. Rare is the opposite, and useful and heavy are unrelated.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1), self.pin_step(0))
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "core")
        self.play(FadeIn(core, shift=UP * 0.1), self.pin_step(1))
        self.at_word(n, "answer")
        box, anims = q.confirm()
        self.play(*anims, self.pin_step(3))
        self.at_word(n, "opposite")
        marks_a, anims = q.strike("a")
        self.play(*anims, self.pin_step(2))
        self.at_word(n, "unrelated")
        marks_c, anims_c = q.strike("c")
        marks_d, anims_d = q.strike("d")
        self.play(*anims_c, *anims_d)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_abundant")

    def example_lucid(self):
        self.scene_start("S06_ex_lucid", title="Worked Example 2")

        q = OptionQuestion("LUCID", ["lucky", "clear", "bright-coloured", "liquid"], "b",
                           {"a": "sound-alike", "c": "related but different", "d": "sound-alike"})
        group = self.run_question(q, LEFT * 2.4 + UP * 0.2)
        core = pill("core: easy to understand", GOOD, size=LABEL).move_to(DOWN * 2.6)
        self.validator.check_in_frame(VGroup(group, core))

        n = self.narrate(
            id="ex2_01",
            text="Lucid: lucky, clear, bright-coloured, or liquid? The core meaning is easy to understand. The answer is "
                 "clear. Lucky and liquid are sound-alike traps.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1))
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "core")
        self.play(FadeIn(core, shift=UP * 0.1), self.pin_step(1))
        self.at_word(n, "answer")
        box, anims = q.confirm()
        self.play(*anims, self.pin_step(3))
        self.at_word(n, "Lucky", occurrence=2)
        ma, a1 = q.strike("a")
        md, a2 = q.strike("d")
        self.play(*a1, *a2, self.pin_step(2))
        self.at_word(n, "traps")
        mc, a3 = q.strike("c")
        self.play(*a3)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_lucid")

    def example_diligent(self):
        self.scene_start("S07_ex_diligent", title="Worked Example 3")

        q = OptionQuestion("DILIGENT", ["intelligent", "hard-working", "diligence", "delicate"], "b",
                           {"a": "sound-alike", "c": "noun, not adjective", "d": "sound-alike"})
        group = self.run_question(q, LEFT * 2.4 + UP * 0.2)
        pos_ = pill("diligent = adjective  (a diligent worker)", WORD, size=LABEL).move_to(DOWN * 2.6)
        self.validator.check_in_frame(VGroup(group, pos_))

        n = self.narrate(
            id="ex3_01",
            text="Diligent: intelligent, hard-working, diligence, or delicate? The answer is hard-working. Diligence looks "
                 "tempting, but it's a noun, and diligent is an adjective.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1))
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "answer")
        box, anims = q.confirm()
        self.play(*anims, self.pin_step(3))
        self.at_word(n, "noun")
        mc, a1 = q.strike("c")
        self.play(*a1, FadeIn(pos_, shift=UP * 0.1), self.pin_step(2))
        self.at_word(n, "adjective")
        ma, a2 = q.strike("a")
        md, a3 = q.strike("d")
        self.play(*a2, *a3)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_diligent")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        rules = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Find the core meaning first, in your own words", WORD),
                             ("The answer must be the same part of speech", SECOND),
                             ("Match connotation and degree where possible", "#F48FB1"),
                             ("Ignore options that only SOUND like the word, or appear NEAR it", TRAP)])])
        rules.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(rules).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Four rules. First, find the core meaning, in your own words. Second, the answer must be the same part of "
                 "speech. Third, match connotation and degree where possible. And fourth, ignore options that only sound "
                 "like the word, or appear near it in phrases.",
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

        strip = process_strip(BODY).move_to(UP * 2.3)
        fit_width(strip, SAFE_W)
        details = VGroup(*[VGroup(pill(name, col, size=SMALL), fitted_text(s_, SAFE_W - 3.4, LABEL, INK))
                           .arrange(RIGHT, buff=0.3) for (name, col), s_ in zip(STEP_COLS.items(), [
                               "Note the word and its part of speech; read any sentence",
                               "Say your own synonym before looking at the options",
                               "Remove opposites, sound-alikes, wrong parts of speech, “related but different”",
                               "Swap the answer into a sentence: does the meaning hold?"])])
        details.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(details).move_to(DOWN * 0.5)
        self.validator.check_in_frame(VGroup(strip, board))

        n = self.narrate(
            id="process_01",
            text="The process has four steps. Read: note the word and its part of speech, and if there's a sentence, read "
                 "it. Predict: say your own synonym before looking at the options.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(strip, shift=DOWN * 0.2), FadeIn(board[0]))
        self.at_word(n, "Read", occurrence=1)
        self.play(Indicate(step_chip(strip, "READ")), FadeIn(details[0], shift=RIGHT * 0.2))
        self.at_word(n, "Predict")
        self.play(Indicate(step_chip(strip, "PREDICT")), FadeIn(details[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="process_02",
            text="Eliminate: remove opposites, sound-alikes, wrong parts of speech, and related but different words. "
                 "Confirm: swap the answer into a sentence. Does the meaning hold?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(Indicate(step_chip(strip, "ELIMINATE")), FadeIn(details[2], shift=RIGHT * 0.2))
        self.at_word(n, "Confirm")
        self.play(Indicate(step_chip(strip, "CONFIRM")), FadeIn(details[3], shift=RIGHT * 0.2))
        self.at_word(n, "hold")
        self.play(Circumscribe(details[3], color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_process")

    # ========================================== 10. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S10_hook_solved", title="Hook, Solved")

        h = self.HOOK
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        group = self.run_question(q, LEFT * 2.6 + DOWN * 0.1)
        strip = process_strip(SMALL).move_to(UP * (CARD_TOP - 0.2))
        fit_width(strip, SAFE_W)
        predict = pill("predict: honest, open", STEP_COLS["PREDICT"], size=LABEL).next_to(q.word, RIGHT, buff=0.5)
        confirm = text("“To be frank, the delays have hurt our launch.”", LABEL, GOOD)
        fit_width(confirm, SAFE_W).move_to(DOWN * 2.8)
        self.validator.check_in_frame(VGroup(strip, group, predict, confirm))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: candid is an adjective, in to be candid. Predict: honest, open.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(strip), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(step_chip(strip, "READ")))
        self.at_word(n, "Predict")
        self.play(Indicate(step_chip(strip, "PREDICT")), FadeIn(predict, shift=LEFT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Angry: the client may be upset, but candid describes how they speak, not what they feel. "
                 "Polite: candid speech is often not polite. Confused: unrelated.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(Indicate(step_chip(strip, "ELIMINATE")))
        m1, a1 = q.strike("a")
        self.at_word(n, "Angry")
        self.play(*a1)
        m3, a3 = q.strike("c")
        self.at_word(n, "Polite")
        self.play(*a3)
        m2, a2 = q.strike("b")
        self.at_word(n, "Confused")
        self.play(*a2)
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: to be frank, the delays have hurt our launch. Same meaning. The answer is frank. So the client "
                 "is being direct, not hostile. Reply with facts and a plan, not an apology spiral.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(Indicate(step_chip(strip, "CONFIRM")), FadeIn(confirm, shift=UP * 0.1))
        self.at_word(n, "Same")
        self.play(Indicate(confirm, color=GOOD, scale_factor=1.03))
        self.at_word(n, "answer")
        box, anims = q.confirm()
        self.play(*anims)
        self.at_word(n, "direct")
        tip = pill("direct, not hostile  →  reply with facts and a plan", GOOD, size=LABEL)
        fit_width(tip, SAFE_W).move_to(confirm)
        self.play(FadeOut(confirm), FadeIn(tip, shift=UP * 0.1))
        self.at_word(n, "Reply")
        self.play(Circumscribe(tip, color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_hook_solved")

    # ========================================== 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S11_patterns", title="Exam Patterns and Solving Models")

        table = self.table_rows(["Pattern", "What it looks like", "Solving model"], [
            ["Single word", "WORD: four options", "predict → cut opposites & sound-alikes → confirm"],
            ["Word in a sentence", "“closest to the bold word”", "use the sentence's meaning, not the usual one"],
            ["Odd one out", "three synonyms, one intruder", "find the shared core; the intruder breaks it"],
        ], [2.6, 3.8, 5.4])
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="You'll meet three patterns. A single word with four options: predict, cut opposites and sound-alikes, "
                 "then confirm in a sentence.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        self.at_word(n, "single")
        self.play(FadeIn(table[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_02",
            text="A word in a sentence: use the sentence's meaning, not the word's most common meaning. And odd one out: "
                 "three synonyms and one intruder. Find the shared core, and the intruder breaks it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sentence")
        self.play(FadeIn(table[2], shift=RIGHT * 0.2))
        self.at_word(n, "odd")
        self.play(FadeIn(table[3], shift=RIGHT * 0.2))
        self.at_word(n, "intruder", occurrence=2)
        self.play(Indicate(table[3][2], color=GOOD, scale_factor=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_patterns")

    # ======================================== 12. COMMON MISTAKES ==========

    def common_mistakes(self):
        self.scene_start("S12_mistakes", title="Common Mistakes")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "Choosing the antonym", card_w),
             self.verdict_card(True, "It's there on purpose: check direction", card_w)),
            (self.verdict_card(False, "Choosing a sound-alike  (lucid → lucky)", card_w),
             self.verdict_card(True, "Match meaning, not sound", card_w)),
            (self.verdict_card(False, "Choosing a word seen NEAR it  (candid → camera)", card_w),
             self.verdict_card(True, "Choose by overlap of meaning", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is choosing the antonym. It's in the options on purpose, and a rushed "
                 "brain registers it as related.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        self.at_word(n, "antonym")
        self.play(FadeIn(pairs[0][0], shift=RIGHT * 0.3))
        self.at_word(n, "rushed")
        self.play(FadeIn(pairs[0][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mistakes_02",
            text="The second is choosing a sound-alike, like lucid and lucky. The third is choosing a word that often "
                 "appears near the question word, like candid and camera.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "second")
        self.play(FadeIn(pairs[1][0], shift=RIGHT * 0.3), FadeIn(pairs[1][1], shift=LEFT * 0.3))
        self.at_word(n, "third")
        self.play(FadeIn(pairs[2][0], shift=RIGHT * 0.3), FadeIn(pairs[2][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_mistakes")

    # ============================================== 13. PRACTICE ==========

    PRACTICE = [
        ("OBSOLETE", ["hidden", "broken", "outdated", "obvious"], "c",
         {"a": "unrelated", "b": "related but different", "d": "sound-alike"}, "no longer in use"),
        ("METICULOUS", ["careful", "careless", "nervous", "fast"], "a",
         {"b": "antonym", "c": "unrelated", "d": "unrelated"}, "very careful about detail"),
        ("CONCISE", ["exact", "brief", "confused", "complete"], "b",
         {"a": "partial overlap: misses “short”", "c": "unrelated", "d": "unrelated"}, "short and to the point"),
    ]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        lines = VGroup(*[VGroup(pill(str(i + 1), FOCUS, size=SMALL), pill(w, WORD, size=LABEL),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, INK))
                         .arrange(RIGHT, buff=0.35) for i, (w, opts, *_rest) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        board = self.card(lines, color=FOCUS).move_to(UP * 0.4)
        fit_width(board, SAFE_W)
        self.validator.check_in_frame(board)

        # SILENCE (pause_after): countdown ring while the learner thinks.
        n = self.narrate(
            id="practice_01",
            text="Your turn. One: obsolete. Hidden, broken, outdated, or obvious? Two: meticulous. Careful, careless, "
                 "nervous, or fast? Three: concise. Exact, brief, confused, or complete?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]))
        for ln, (spoken, first_option) in zip(lines, [("obsolete", "Hidden"), ("meticulous", "Careful"),
                                                     ("concise", "Exact")]):
            self.at_word(n, spoken)
            self.play(FadeIn(ln[:2], shift=UP * 0.15), run_time=0.4)
            self.at_word(n, first_option)
            self.play(FadeIn(ln[2], shift=LEFT * 0.15), run_time=0.4)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S13_practice")

    # =============================================== 14. ANSWERS ==========

    def answers(self):
        self.scene_start("S14_answers", title="Answers")

        rows = VGroup()
        for i, (w, opts, key, traps, core) in enumerate(self.PRACTICE):
            q = OptionQuestion(w, opts, key, traps)        # validates key / traps
            ans = opts["abcd".index(key)]
            rows.add(VGroup(pill(w, WORD, size=LABEL), text("→", LABEL, MUTED), pill(f"({key}) {ans}", GOOD, size=LABEL),
                            text(core, SMALL, INK)).arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to(UP * 0.9)
        fit_width(rows, SAFE_W)
        traps = VGroup(pill("obvious: sound-alike", TRAP, size=SMALL), pill("careless: antonym", TRAP, size=SMALL),
                       pill("exact: misses the “short” core", TRAP, size=SMALL)).arrange(RIGHT, buff=0.3)
        fit_width(traps, SAFE_W).move_to(DOWN * 1.6)
        self.validator.check_in_frame(VGroup(rows, traps))

        n = self.narrate(
            id="answers_01",
            text="One: outdated, meaning no longer in use. Obvious is a sound-alike trap. Two: careful, meaning very "
                 "careful about detail. Careless is the antonym. Three: brief, meaning short and to the point. Exact "
                 "overlaps partly, but misses the short core.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "outdated")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "Obvious")
        self.play(FadeIn(traps[0], shift=UP * 0.1))
        self.at_word(n, "Two")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "Careless")
        self.play(FadeIn(traps[1], shift=UP * 0.1))
        self.at_word(n, "Three")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "Exact")
        self.play(FadeIn(traps[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S15_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 1", [
            ["Synonym", "same or nearly the same meaning in context"],
            ["Anchor", "find the core meaning in your own words first"],
            ["Must match", "part of speech; ideally tone and degree too"],
            ["Traps", "antonyms, sound-alikes, words that appear nearby"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. A synonym has the same or nearly the same meaning in context. Anchor on the core meaning, in "
                 "your own words, first. The answer must match the part of speech, and ideally the tone and degree too. "
                 "And watch for the traps: antonyms, sound-alikes, and words that simply appear nearby.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["synonym", "Anchor", "match", "traps"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        both = VGroup(pill("option B", GOOD, size=BODY), pill("option C", GOOD, size=BODY)).arrange(RIGHT, buff=1.0)
        both.move_to(UP * 0.8)
        q = text("both look right … which is closer?", LABEL, MUTED).next_to(both, DOWN, buff=0.35)
        nxt = pill("Next:  Types of Synonyms", FOCUS, size=BODY).move_to(DOWN * 1.8)
        self.validator.check_in_frame(VGroup(both, q, nxt))

        n = self.narrate(
            id="next_01",
            text="Nearly the same hides several kinds of difference. Video two names them, so you can pick between two "
                 "options that both look right.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "hides")
        self.play(FadeIn(both, shift=UP * 0.2))
        self.at_word(n, "both")
        self.play(FadeIn(q))
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")
