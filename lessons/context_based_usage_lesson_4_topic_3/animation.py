"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 4 - One-Word Substitution
Video  : 03 - Context-Based Usage (Video 3 of 6)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 4 - One-Word Substitution\\03 - Context-Based Usage.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Each word's meaning and part of speech live in WORDS; the worked examples and Hook, Solved read the meaning from it.
The "two checks" card (meaning, grammar, re-read the sentence) stays pinned top-right through the worked examples and Hook, Solved.
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

# word -> (meaning, part of speech / what it describes)
WORDS = {
    "illegible": ("cannot be read", "adjective: describes writing"),
    "ineligible": ("not qualified", "adjective: describes a person"),
    "illiterate": ("cannot read or write", "adjective: describes a person"),
    "illogical": ("not reasonable", "adjective: describes an idea"),
    "unanimous": ("everyone agrees", "adjective"),
    "anonymous": ("name not known", "adjective"),
    "extempore": ("without preparation", "adjective"),
    "ambiguous": ("can be understood in two ways", "adjective"),
    "eligible": ("meets the conditions", "adjective"),
    "unanimously": ("with everyone agreeing", "adverb"),
}


class ContextBasedUsageVideo(LMSScene):
    lesson_title = "Context-Based Usage"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_unanimous()
        self.example_extempore()
        self.example_anonymous()
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

    def checks_pin(self):
        return self.steps_pin("two checks", [("MEANING: all the phrase says", WORD),
                                             ("GRAMMAR: noun? adjective?", RATIO),
                                             ("re-read the whole sentence", GOOD)])

    def app_card(self, fill=None):
        head = text("PHARMACY APP  ·  upload rejected", SMALL, RATIO, BOLD)
        s_ = f"“We couldn't process your prescription because the doctor's handwriting is {fill or BLANK}.”"
        cx, w = self.free_area()
        line = fitted_text(s_, min(w - 1.4, SAFE_W - 1.8), LABEL, INK, NORMAL, max_lines=2,
                           t2c={fill or BLANK: GOOD if fill else FOCUS})
        card = self.card(VGroup(head, line).arrange(DOWN, buff=0.2, aligned_edge=LEFT), width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def replace_example(self, original, phrase, grammar, rewritten, word):
        """Original sentence with its phrase, the two checks, and the sentence with the word in place."""
        cx, w = self.free_area()
        before = fitted_text(f"“{original}”", w - 0.8, LABEL, INK, NORMAL, max_lines=2, t2c={phrase: WORD})
        meaning = VGroup(pill("MEANING", WORD, size=SMALL), text(WORDS[word][0], LABEL, INK)).arrange(RIGHT, buff=0.25)
        gram = VGroup(pill("GRAMMAR", RATIO, size=SMALL), text(grammar, LABEL, INK)).arrange(RIGHT, buff=0.25)
        after = fitted_text(f"“{rewritten}”", w - 0.8, BODY, INK, NORMAL, max_lines=2, t2c={word: GOOD})
        block = VGroup(before, meaning, gram, after).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_height(block, SAFE_H - 1.6)
        self.place_free(block, y=0.1)
        self.no_overlap(before, meaning, gram, after)
        self.validator.check_in_frame(block)
        return before, meaning, gram, after

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 4 · One-Word Substitution", "Video 3")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        before = VGroup(text("Videos 1 and 2", SMALL, MUTED), pill("definition", WORD, size=LABEL),
                        text("→", LABEL, MUTED), pill("word", GOOD, size=LABEL)).arrange(RIGHT, buff=0.3)
        today = VGroup(text("Today", SMALL, FOCUS), pill("the definition, embedded in a SENTENCE", RATIO, size=LABEL))\
            .arrange(RIGHT, buff=0.3)
        fit = pill("the word you choose must FIT there", GOOD, size=LABEL)
        VGroup(before, today, fit).arrange(DOWN, buff=0.6).move_to(DOWN * 0.1)
        self.no_overlap(crumb, before, today, fit)
        self.validator.check_in_frame(VGroup(crumb, before, today, fit))

        n = self.narrate(
            id="intro_01",
            text="Videos one and two matched definitions to words. In real sentences, and in many exam questions, the "
                 "definition is embedded in a sentence, and the word you choose must fit there.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "matched")
        self.play(FadeIn(before, shift=UP * 0.1))
        self.at_word(n, "embedded")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.at_word(n, "fit")
        self.play(FadeIn(fit, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Context-Based Usage", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=RATIO, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Replace an underlined phrase with a word that fits both meaning and grammar", GOOD),
                 ("Use the sentence to decide between close substitutes", RATIO)]
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
            text="This video is context-based usage. By the end, you'll replace an underlined phrase with a word that fits "
                 "both meaning and grammar, and use the sentence to decide between close substitutes.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(before, today, fit), shift=UP * 0.3))
        self.at_word(n, "context-based")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["replace", "decide"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word=f"handwriting is {BLANK}", options=["illegible", "ineligible", "illiterate", "illogical"], key="a",
                traps={"b": "look-alike:  = not qualified", "c": "describes a PERSON who can't read",
                       "d": "= not reasonable"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        assert all(o in WORDS for o in h["options"]) and WORDS["illegible"][0] == "cannot be read"
        app = self.app_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.8)
        fit_width(opts, SAFE_W)
        ask = pill("which word completes the message?", FOCUS, size=LABEL)
        ask.next_to(app, DOWN, buff=0.6)
        opts.next_to(ask, DOWN, buff=0.7)
        self.no_overlap(app, ask, opts)
        self.validator.check_in_frame(VGroup(app, ask, opts))

        n = self.narrate(
            id="hook_01",
            text="A pharmacy app rejects your uploaded prescription with this message: We couldn't process your "
                 "prescription, because the doctor's handwriting is, blank.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rejects")
        self.play(FadeIn(app[0]), FadeIn(app[1][0]))
        self.at_word(n, "couldn't")
        self.play(FadeIn(app[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Which word completes the message: illegible, ineligible, illiterate, or illogical?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "Which")
        self.play(FadeIn(ask, shift=UP * 0.1))
        for row, spoken in zip(opts, ["illegible", "ineligible", "illiterate", "illogical"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("context questions: the definition sits inside a sentence", SECOND, size=LABEL)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        kinds = VGroup(
            VGroup(pill("a phrase to replace", WORD, size=SMALL),
                   text("“He made a speech without any preparation.”", LABEL, INK, t2c={"without any preparation": WORD}))
            .arrange(DOWN, buff=0.15, aligned_edge=LEFT),
            VGroup(pill("a blank", FOCUS, size=SMALL),
                   text(f"“The doctor's handwriting is {BLANK}.”", LABEL, INK, t2c={BLANK: FOCUS}))
            .arrange(DOWN, buff=0.15, aligned_edge=LEFT)).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        two = pill("TWO things must be true of the answer", GOOD, size=LABEL)
        body = VGroup(kinds, two).arrange(DOWN, buff=0.6)
        fit_width(body, SAFE_W)
        body.next_to(head, DOWN, buff=0.6)
        self.no_overlap(head, kinds, two)
        self.validator.check_in_frame(VGroup(head, body))

        n = self.narrate(
            id="concept_01",
            text="In context questions, the sentence contains either an underlined phrase to replace, or a blank. Two "
                 "things must be true of the answer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "context")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "underlined")
        self.play(FadeIn(kinds[0], shift=RIGHT * 0.2))
        self.at_word(n, "blank")
        self.play(FadeIn(kinds[1], shift=RIGHT * 0.2))
        self.at_word(n, "Two")
        self.play(FadeIn(two, shift=UP * 0.1))
        self.wait_for_narration(n)

        # Meaning and grammar.
        checks = VGroup(
            VGroup(pill("1  MEANING", WORD, size=BODY), text("carries exactly what the phrase says", LABEL, INK))
            .arrange(RIGHT, buff=0.35),
            VGroup(pill("2  GRAMMAR", RATIO, size=BODY), text("fits the sentence's structure", LABEL, INK))
            .arrange(RIGHT, buff=0.35)).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        after_is = VGroup(text(f"“… is {BLANK}”  →  an adjective:", LABEL, INK, t2c={BLANK: FOCUS}),
                          pill("illegible  ✓", GOOD, size=SMALL), pill("illiteracy  ✗  (a noun)", BAD, size=SMALL))\
            .arrange(RIGHT, buff=0.3)
        person = VGroup(text("“a person who …”  →  a noun", LABEL, INK, t2c={"a person who": WORD}))
        cbody = VGroup(checks, after_is, person).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(cbody, SAFE_W, SAFE_H - 1.4)
        cbody.move_to(UP * 0.3)
        self.validator.check_in_frame(cbody)
        n = self.narrate(
            id="concept_02",
            text="First, meaning: it must carry exactly what the phrase says. Second, grammar: it must fit the sentence's "
                 "structure. If the blank follows is, you need an adjective, like illegible; not a noun, like illiteracy. "
                 "And if the phrase is a person who, the answer is a noun.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head, body)))
        self.at_word(n, "meaning")
        self.play(FadeIn(checks[0], shift=RIGHT * 0.2))
        self.at_word(n, "grammar")
        self.play(FadeIn(checks[1], shift=RIGHT * 0.2))
        self.at_word(n, "adjective")
        self.play(FadeIn(after_is, shift=UP * 0.1))
        self.at_word(n, "person")
        self.play(FadeIn(person, shift=UP * 0.1))
        self.wait_for_narration(n)

        # Near-substitutes: the sentence decides.
        near_head = pill("context decides between near-substitutes", FOCUS, size=LABEL)
        near_head.move_to(UP * (CARD_TOP - near_head.height / 2))
        near = VGroup(*[VGroup(text(f"“{s_}”", LABEL, INK, t2c={BLANK: FOCUS}), text(f"({clue})", SMALL, MUTED),
                               pill(w, GOOD, size=LABEL)).arrange(RIGHT, buff=0.3)
                        for s_, clue, w in [(f"The committee's decision was {BLANK}.", WORDS["unanimous"][0], "unanimous"),
                                            (f"The donor wished to remain {BLANK}.", WORDS["anonymous"][0], "anonymous")]])
        near.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        which = pill("both are about people and decisions: the SENTENCE tells you which", GOOD, size=SMALL)
        nbody = VGroup(near, which).arrange(DOWN, buff=0.6)
        fit_width(nbody, SAFE_W)
        nbody.next_to(near_head, DOWN, buff=0.7)
        self.no_overlap(near_head, near, which)
        self.validator.check_in_frame(VGroup(near_head, nbody))
        n = self.narrate(
            id="concept_03",
            text="Context also helps decide between near-substitutes. The committee's decision was, blank: everyone "
                 "agreed, so unanimous. The donor wished to remain, blank: name not known, so anonymous. Both are about "
                 "people and decisions, but the sentence tells you which.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(cbody))
        self.at_word(n, "near-substitutes")
        self.play(FadeIn(near_head, shift=DOWN * 0.2))
        for r, (first, word) in zip(near, [("committee's", "unanimous"), ("donor", "anonymous")]):
            self.at_word(n, first)
            self.play(FadeIn(r[:2], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, word)
            self.play(FadeIn(r[2], shift=LEFT * 0.1), run_time=0.4)
        self.at_word(n, "tells")
        self.play(FadeIn(which, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        uses = VGroup(*[pill(u, WORD, size=LABEL) for u in ["reports", "notices", "emails"]]).arrange(RIGHT, buff=0.5)
        label = text("most real uses of these words are in sentences", LABEL, MUTED)
        exams = pill("exams increasingly test them in context too", BAD, size=LABEL)
        gram = pill("the GRAMMAR check removes options that pass a pure definition match", RATIO, size=SMALL)
        group = VGroup(VGroup(label, uses).arrange(DOWN, buff=0.25), exams, gram).arrange(DOWN, buff=0.7)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="Most real uses of these words are in sentences: in reports, notices and emails. Exams increasingly "
                 "present them in context too, where the grammar check removes options that would pass a pure definition "
                 "match.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sentences")
        self.play(FadeIn(label, shift=DOWN * 0.1))
        self.at_word(n, "reports")
        self.play(LaggedStart(*[FadeIn(u, shift=UP * 0.1) for u in uses], lag_ratio=0.3))
        self.at_word(n, "Exams")
        self.play(FadeIn(exams, shift=UP * 0.1))
        self.at_word(n, "grammar")
        self.play(FadeIn(gram, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        def part(title, job_ok, plug_ok, verdict, color):
            rows = VGroup(text(title, LABEL, color, BOLD),
                          text(("✓" if job_ok else "✗") + "  does the right job", LABEL, GOOD if job_ok else BAD),
                          text(("✓" if plug_ok else "✗") + "  has the right connector", LABEL, GOOD if plug_ok else BAD),
                          text(verdict, LABEL, color, BOLD)).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
            return self.card(rows, color=color)

        good = part("part A", True, True, "fits", GOOD)
        bad = part("part B", True, False, "still won't fit", BAD)
        parts = VGroup(good, bad).arrange(RIGHT, buff=0.8, aligned_edge=UP)
        mapping = pill("the job = MEANING   ·   the connector = GRAMMAR", FOCUS, size=LABEL)
        block = VGroup(parts, mapping).arrange(DOWN, buff=0.6)
        fit_within(block, SAFE_W, SAFE_H - 1.4)
        block.move_to(UP * 0.3)
        self.no_overlap(good, bad)
        self.no_overlap(parts, mapping)
        self.validator.check_in_frame(block)

        n = self.narrate(
            id="analogy_01",
            text="Replacing a phrase is like replacing a machine part. It must do the right job, and have the right "
                 "connector. The right job with the wrong connector still won't fit.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "machine")
        self.play(FadeIn(good[0]), FadeIn(good[1][0]), FadeIn(mapping, shift=UP * 0.1))
        self.at_word(n, "job", occurrence=1)
        self.play(FadeIn(good[1][1], shift=RIGHT * 0.1))
        self.at_word(n, "connector", occurrence=1)
        self.play(FadeIn(good[1][2], shift=RIGHT * 0.1), FadeIn(good[1][3]))
        self.at_word(n, "wrong")
        self.play(FadeIn(bad[0]), FadeIn(bad[1][:3], shift=LEFT * 0.1))
        self.at_word(n, "won't")
        self.play(FadeIn(bad[1][3], scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_unanimous(self):
        self.scene_start("S05_ex_unanimous", title="Worked Example 1")
        self.play(self.pin(self.checks_pin()))

        before, meaning, gram, after = self.replace_example(
            "The committee agreed with no one against the plan.", "agreed with no one against",
            "after “was”: an adjective", "The committee was unanimous about the plan.", "unanimous")

        n = self.narrate(
            id="ex1_01",
            text="The committee agreed, with no one against the plan. Meaning: everyone agrees. Grammar: after was, an "
                 "adjective. The committee was unanimous about the plan.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "committee", occurrence=1)
        self.play(FadeIn(before, shift=DOWN * 0.1))
        self.at_word(n, "Meaning")
        self.play(FadeIn(meaning, shift=RIGHT * 0.2), self.pin_step(0, color=WORD))
        self.at_word(n, "Grammar")
        self.play(FadeIn(gram, shift=RIGHT * 0.2), self.pin_step(1, color=RATIO))
        self.at_word(n, "unanimous")
        self.play(FadeIn(after, shift=UP * 0.1), self.pin_step(2, color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_unanimous")

    def example_extempore(self):
        self.scene_start("S06_ex_extempore", title="Worked Example 2")

        before, meaning, gram, after = self.replace_example(
            "He made a speech without any preparation.", "without any preparation",
            "before “speech”: an adjective", "He made an extempore speech.", "extempore")

        n = self.narrate(
            id="ex2_01",
            text="He made a speech without any preparation. Meaning: without preparation. Grammar: an adjective, before "
                 "speech. He made an extempore speech.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "made", occurrence=1)
        self.play(FadeIn(before, shift=DOWN * 0.1))
        self.at_word(n, "Meaning")
        self.play(FadeIn(meaning, shift=RIGHT * 0.2), self.pin_step(0, color=WORD))
        self.at_word(n, "Grammar")
        self.play(FadeIn(gram, shift=RIGHT * 0.2), self.pin_step(1, color=RATIO))
        self.at_word(n, "extempore")
        self.play(FadeIn(after, shift=UP * 0.1), self.pin_step(2, color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_extempore")

    def example_anonymous(self):
        self.scene_start("S07_ex_anonymous", title="Worked Example 3")

        before, meaning, gram, after = self.replace_example(
            "The letter was written by a person whose name was not known.",
            "written by a person whose name was not known", "the sentence changes shape: the word follows “was”",
            "The letter was anonymous.", "anonymous")

        n = self.narrate(
            id="ex3_01",
            text="The letter was written by a person whose name was not known. Meaning: name not known. Grammar: the "
                 "sentence changes shape, and the word follows was. The letter was anonymous.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "letter", occurrence=1)
        self.play(FadeIn(before, shift=DOWN * 0.1))
        self.at_word(n, "Meaning")
        self.play(FadeIn(meaning, shift=RIGHT * 0.2), self.pin_step(0, color=WORD))
        self.at_word(n, "Grammar")
        self.play(FadeIn(gram, shift=RIGHT * 0.2), self.pin_step(1, color=RATIO))
        self.at_word(n, "anonymous")
        self.play(FadeIn(after, shift=UP * 0.1), self.pin_step(2, color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_anonymous")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        rules = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("The word must carry the FULL meaning of the phrase", WORD),
                             ("The word must fit the sentence's grammar: noun, adjective, verb", RATIO),
                             ("Read the whole sentence with the word in place", GOOD),
                             ("Two words fit the meaning?  The sentence's situation decides", SECOND)])])
        rules.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(rules).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Four rules. First, the word must carry the full meaning of the phrase. Second, the word must fit the "
                 "sentence's grammar: noun, adjective or verb. Third, read the whole sentence with the word in place. And "
                 "fourth, if two words fit the meaning, the sentence's situation decides.",
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
                               "the sentence; mark the phrase or blank",
                               "the word, and its part of speech",
                               "wrong meanings, then wrong parts of speech",
                               "read the full sentence"])])
        details.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(details)
        board.next_to(strip, DOWN, buff=0.5)
        self.no_overlap(strip, board)
        self.validator.check_in_frame(VGroup(strip, board))

        n = self.narrate(
            id="process_01",
            text="The process. Read the sentence, and mark the phrase or blank. Predict the word, and its part of speech. "
                 "Eliminate wrong meanings, then wrong parts of speech. And confirm by reading the full sentence.",
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
        self.play(self.pin(self.checks_pin()))

        h = self.HOOK
        cx, w = self.free_area()
        app = self.app_card()
        needs = VGroup(VGroup(pill("GRAMMAR", RATIO, size=SMALL), text("after “is”: an adjective", LABEL, INK))
                       .arrange(RIGHT, buff=0.2),
                       VGroup(pill("MEANING", WORD, size=SMALL), text(WORDS["illegible"][0], LABEL, INK))
                       .arrange(RIGHT, buff=0.2), pill("predict: illegible", STEP_COLS["PREDICT"], size=SMALL))\
            .arrange(RIGHT, buff=0.4)
        fit_width(needs, w - 0.6)
        needs.next_to(app, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=LABEL)
        fit_height(q.group, needs.get_bottom()[1] - 0.3 - (BOTTOM_Y + 0.6))
        q.group.next_to(needs, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        fixed = self.app_card(fill="illegible")
        self.no_overlap(app, needs, q.group)
        self.no_overlap(app, self.pinned)
        self.no_overlap(needs, self.pinned)
        self.validator.check_in_frame(VGroup(app, needs, q.group))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: the handwriting is, blank. It needs an adjective, meaning cannot be read. "
                 "Predict: illegible.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(app), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(app[1][1], color=FOCUS, scale_factor=1.02))
        self.at_word(n, "adjective")
        self.play(FadeIn(needs[0], shift=UP * 0.1), self.pin_step(1, color=RATIO))
        self.at_word(n, "meaning")
        self.play(FadeIn(needs[1], shift=UP * 0.1), self.pin_step(0, color=WORD))
        self.at_word(n, "Predict")
        self.play(FadeIn(needs[2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Ineligible means not qualified: a look-alike. Illiterate describes a person who can't read. "
                 "Illogical means not reasonable.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(Indicate(q.rows, color=BAD, scale_factor=1.02))
        for letter, spoken in [("b", "Ineligible"), ("c", "Illiterate"), ("d", "Illogical")]:
            self.at_word(n, spoken)
            self.play(*q.strike(letter)[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: the doctor's handwriting is illegible. That's the answer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(ReplacementTransform(app, fixed), self.pin_step(2, color=GOOD))
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
            ["Replace the underlined phrase", "match meaning, then part of speech"],
            ["Fill the blank", "predict from the sentence; watch for look-alikes"],
            ["Two close substitutes", "let the sentence's situation decide"],
        ], [5.0, 6.8], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. Replace the underlined phrase: match meaning, then part of speech. Fill the blank: "
                 "predict from the sentence, and watch for look-alikes. And two close substitutes: let the sentence's "
                 "situation decide.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Replace", "Fill", "close"]):
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
            (self.verdict_card(False, "A look-alike: ineligible for illegible", card_w),
             self.verdict_card(True, "Check the meaning, not the look", card_w)),
            (self.verdict_card(False, "Ignoring part of speech: illiterate for a thing", card_w),
             self.verdict_card(True, "Match noun / adjective / verb", card_w)),
            (self.verdict_card(False, "Not re-reading the full sentence", card_w),
             self.verdict_card(True, "Read it with the word in place", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is choosing a look-alike, like ineligible for illegible. The second is "
                 "ignoring part of speech, like illiterate for a thing. The third is not re-reading the full sentence.",
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
        ("The minister's statement was one that could be understood in two ways.",
         "one that could be understood in two ways", ["ambitious", "ambivalent", "amphibious", "ambiguous"], "d",
         "(b) ambivalent = having mixed feelings"),
        ("Only students who meet the conditions may apply.", "who meet the conditions",
         ["legible", "edible", "eligible", "illegible"], "c", "(a) legible and (d) illegible are about handwriting"),
        ("The treaty was signed by all the members without exception.", "by all the members without exception",
         ["anonymously", "unanimously", "universally", "uniformly"], "b",
         "everyone agreed;  (c) and (d) don't carry agreement"),
    ]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        head = pill("Replace the highlighted phrase", GOOD, size=LABEL)
        lines = VGroup(*[VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL),
                                       text(f"“{sent}”", LABEL, INK, t2c={phrase: WORD})).arrange(RIGHT, buff=0.35),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, INK))
                         .arrange(DOWN, buff=0.2, aligned_edge=LEFT)
                         for i, (sent, phrase, opts, *_r) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        board = self.card(VGroup(head, lines).arrange(DOWN, buff=0.4, aligned_edge=LEFT), color=FOCUS)
        fit_within(board, SAFE_W, SAFE_H - 1.2)
        board.move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn: replace the highlighted phrase. One: the minister's statement was one that could be "
                 "understood in two ways. Ambitious, ambivalent, amphibious, or ambiguous? Two: only students who meet "
                 "the conditions may apply. Legible, edible, eligible, or illegible? Three: the treaty was signed by all "
                 "the members without exception. Anonymously, unanimously, universally, or uniformly?",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.play(FadeIn(board[0]), FadeIn(head))
        for ln, (spoken, first_option) in zip(lines, [("minister's", "Ambitious"), ("students", "Legible"),
                                                     ("treaty", "Anonymously")]):
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
        for i, (_sent, phrase, opts, key, why) in enumerate(self.PRACTICE):
            word = opts["abcd".index(key)]
            assert word in WORDS
            rows.add(VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL), text(f"“{phrase}”", LABEL, INK),
                                   text("→", LABEL, MUTED), pill(f"({key}) {word}", GOOD, size=LABEL))
                            .arrange(RIGHT, buff=0.3), text(why, SMALL, BAD)).arrange(DOWN, buff=0.18, aligned_edge=LEFT))
        rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - 1.2)
        rows.move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: ambiguous. Ambivalent means having mixed feelings. Two: eligible. Legible and illegible are about "
                 "handwriting. Three: unanimously: everyone agreed. Universally and uniformly don't carry agreement.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, why) in zip(rows, [("ambiguous", "Ambivalent"), ("eligible", "handwriting"),
                                           ("unanimously", "Universally")]):
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

        card, table = self.recap_card("Recap Card: Video 3", [
            ["Two checks", "meaning and grammar"],
            ["Look-alikes", "illegible / ineligible / illiterate"],
            ["Close substitutes", "the sentence's situation decides"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Two checks: meaning and grammar. Watch the look-alikes: illegible, ineligible, illiterate. And "
                 "for close substitutes, the sentence's situation decides.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["checks", "look-alikes", "close"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        alike = pill("substitute pairs that look or sound alike", BAD, size=LABEL)
        marks = pill("the biggest source of lost marks in this topic", RATIO, size=LABEL)
        nxt = pill("Next:  Commonly Confused Substitutions", FOCUS, size=LABEL)
        VGroup(alike, marks, nxt).arrange(DOWN, buff=0.7).move_to(UP * 0.2)
        self.no_overlap(alike, marks, nxt)
        self.validator.check_in_frame(VGroup(alike, marks, nxt))

        n = self.narrate(
            id="next_01",
            text="Video four collects the substitute pairs that look or sound alike: the biggest source of lost marks in "
                 "this topic.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.at_word(n, "alike")
        self.play(FadeIn(alike, shift=UP * 0.1))
        self.at_word(n, "biggest")
        self.play(FadeIn(marks, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")
