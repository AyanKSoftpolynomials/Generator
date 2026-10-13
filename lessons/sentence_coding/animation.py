"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A
Module : Module 1 - Logical Reasoning
Lesson : Lesson 3 - Coding & Decoding II: Substitution and Sentence Coding
Topic  : Sentence Coding (Topic 2)

Source script:
  C:\\Scripts\\Section A\\Module 1 - Logical Reasoning\\Lesson 03 - Coding & Decoding II\\
  Topic 2 - Sentence Coding.md

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``.

Opening: not the first video of the course, so no spoken course welcome.
The module > lesson > topic trail is shown on screen (silent), followed by a
one-idea recap of Topic 1 (substitution) and what this video covers.

Visual note: the script's elimination grid is shown as elimination inside the
sentence itself (known pairs fade out, the leftover pair lights up), with a
running "code book" of every match found. Same idea, fewer moving parts.

Section map (script heading -> VISUAL PLAN scene):
  S00 Intro (trail + recap)       -> -
  S01 Opening Hook                -> scene 1
  S02 Concept                     -> scene 2
  S03 Common-word matching        -> scene 3
  S04 Elimination / code order    -> scene 4
  S05 Cannot be determined        -> scene 5
  S06-S08 Examples 1-3            -> scene 6
  S09 Exam Application            -> scene 7
  S10 Common Mistake              -> scene 8
  S11-S12 Practice / Answers      -> scene 9
  S13-S14 Revision / Closing      -> scene 10
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

# Semantic colours: one meaning each (same palette as the earlier topics).
WORD = "#4FC3F7"       # a real word
CODE = "#FFB74D"       # a code word
LINK = "#CE93D8"       # an undetermined link
FOCUS = "#FFD54F"      # "look here" / the shared word and code
GOOD = "#66BB6A"       # a match found / the answer
BAD = "#EF5350"        # a rejected option / trap

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
ROWS_Y = [1.55, 0.55, -0.45]                  # the three sentence rows
BOOK_Y = -1.55                                # the running code book


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


def glow(p, color=FOCUS):
    """Animation: light up a pill."""
    return AnimationGroup(p[0].animate.set_stroke(color, 3).set_fill(color, 0.28), p[1].animate.set_color(color))


def unglow(p, color):
    """Animation: return a pill to its resting colour."""
    return AnimationGroup(p[0].animate.set_stroke(color, 2).set_fill(color, 0.08), p[1].animate.set_color(color))


# ==================================================== diagram helpers ====

class Sentence(VGroup):
    """One coded sentence, laid out as: [S1]  codes  means  words.
    ``code(c)`` and ``word(w)`` return the pill for that code / word."""

    def __init__(self, label, codes, words, y, size=LABEL, width=SAFE_W):
        super().__init__()
        self.codes_list, self.words_list = list(codes), list(words)
        self.label = pill(label, MUTED, size=SMALL, fill_opacity=0.06)
        self.codes = VGroup(*[pill(c, CODE, size=size, fill_opacity=0.08) for c in codes]).arrange(RIGHT, buff=0.18)
        self.means = text("means", SMALL, MUTED)
        self.words = VGroup(*[pill(w, WORD, size=size, fill_opacity=0.08) for w in words]).arrange(RIGHT, buff=0.18)
        self.add(self.label, self.codes, self.means, self.words)
        self.arrange(RIGHT, buff=0.35)
        fit_width(self, width)
        self.move_to(UP * y)

    def code(self, c):
        return self.codes[self.codes_list.index(c)]

    def word(self, w):
        return self.words[self.words_list.index(w)]


class CodeBook:
    """A running code book that wraps entries inside the safe frame."""

    def __init__(self, y=BOOK_Y):
        self.title = text("code book:", SMALL, MUTED, BOLD)
        self.title.move_to(LEFT * 5.6 + UP * y)

        self.entries = VGroup()

        self.max_width = SAFE_W - 1.0
        self.row_gap = 0.18
        self.entry_gap = 0.3

    def add(self, word, code, color=GOOD):
        entry = pill(f"{word} = {code}", color, size=SMALL)

        if len(self.entries) == 0:
            entry.next_to(self.title, RIGHT, buff=self.entry_gap)
        else:
            previous = self.entries[-1]

            # Try putting the new entry on the same row.
            candidate = entry.copy().next_to(
                previous,
                RIGHT,
                buff=self.entry_gap
            )

            # If it would exceed the safe width, start a new row.
            right_limit = FRAME_W / 2 - SAFE

            if candidate.get_right()[0] > right_limit:
                entry.next_to(
                    self.title,
                    DOWN,
                    buff=self.row_gap
                )
                entry.align_to(self.title, LEFT)
            else:
                entry.move_to(candidate)

        self.entries.add(entry)
        return entry
        
def undetermined(words, codes, color=LINK):
    """Two words, two codes, joined by crossing '?' links: they can't be separated."""
    w = VGroup(*[pill(x, WORD, size=LABEL, fill_opacity=0.08) for x in words]).arrange(DOWN, buff=0.5)
    c = VGroup(*[pill(x, CODE, size=LABEL, fill_opacity=0.08) for x in codes]).arrange(DOWN, buff=0.5)
    c.next_to(w, RIGHT, buff=2.2)
    links = VGroup(*[Line(a.get_right(), b.get_left(), color=color, stroke_width=3)
                     for a in w for b in c])
    q = text("?", 48, color, BOLD).move_to(VGroup(w, c).get_center())
    return VGroup(w, c, links, q)


# ============================================================= lesson ====

class SentenceCodingVideo(LMSScene):
    lesson_title = "Sentence Coding"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.matching()
        self.elimination()
        self.cannot_determine()
        self.example_they()
        self.example_juice()
        self.example_could_be()
        self.exam_application()
        self.common_mistake()
        self.practice()
        self.answer()
        self.quick_revision()
        self.closing()

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

    def question_card(self, s, color=FOCUS, t2c=None):
        """The on-screen question: fitted text (one or two lines) in a card at the top."""
        t = fitted_text(s, SAFE_W - 1.6, BODY, INK, max_lines=2, t2c=t2c)
        c = self.card(t, color=color)
        return c.move_to(UP * (CARD_TOP - c.height / 2))

    def caption(self, s, color=INK):
        """One-line keyword caption in a fixed-width bar at the bottom of the frame."""
        t = fitted_text(s, SAFE_W - 1.0, BODY, color)
        bar = self.card(t, width=SAFE_W - 0.4, height=t.height + 0.9)
        return bar.move_to(UP * BOTTOM_Y)

    def breadcrumb(self, *parts):
        """Silent 'where are we' trail: Module > Lesson > Topic."""
        colors = [WORD, "#F48FB1", CODE]
        items = []
        for i, p in enumerate(parts):
            if i:
                items.append(text("›", LABEL, MUTED))
            items.append(pill(p, colors[i % 3], size=SMALL))
        return fit_width(VGroup(*items).arrange(RIGHT, buff=0.25), SAFE_W)

    def step_rows(self, rows, width):
        """Numbered rows (pill + fitted text) for routine cards."""
        return VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s, width - 1.2, BODY, INK))
                        .arrange(RIGHT, buff=0.3) for i, (s, c) in enumerate(rows)]
                      ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)

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

    @staticmethod
    def dim(s):
        """Animation: fade a sentence into the background (restorable with undim)."""
        s.save_state()
        return s.animate.fade(0.6)

    @staticmethod
    def undim(s):
        """Animation: bring a dimmed sentence back exactly as it was."""
        return Restore(s)

    def match(self, sentences, word, code):
        """Animation: glow ``word`` and ``code`` in every sentence given."""
        return AnimationGroup(*[glow(s.word(word)) for s in sentences], *[glow(s.code(code)) for s in sentences])

    def settle(self, sentences, word, code):
        """Animation: a found pair turns green (solved) in every sentence given."""
        return AnimationGroup(*[glow(s.word(word), GOOD) for s in sentences if word in s.words_list],
                              *[glow(s.code(code), GOOD) for s in sentences if code in s.codes_list])

    def opening_sentences(self):
        return [Sentence("S1", ["pit", "na", "sa"], ["you", "are", "good"], ROWS_Y[0]),
                Sentence("S2", ["na", "ho", "pa"], ["they", "are", "bad"], ROWS_Y[1]),
                Sentence("S3", ["ka", "sa", "ho"], ["good", "and", "bad"], ROWS_Y[2])]

    def juice_sentences(self):
        return [Sentence("S1", ["mi", "ko", "ta"], ["drink", "fresh", "juice"], ROWS_Y[0]),
                Sentence("S2", ["ta", "ro", "su"], ["juice", "is", "sweet"], ROWS_Y[1]),
                Sentence("S3", ["ko", "pe", "lu"], ["fresh", "cold", "water"], ROWS_Y[2])]

    # ========================================= 0. LESSON INTRO ==========
    # Purpose: where we are (silent trail), last time (one idea), today.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("Module 1 · Logical Reasoning", "Lesson 3 · Coding & Decoding II", "Topic 2")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        last = pill("Last time", MUTED, size=SMALL)
        steps = VGroup(pill("find the real answer", WORD, size=LABEL), text("→", LABEL, MUTED),
                       pill("give its new name", CODE, size=LABEL)).arrange(RIGHT, buff=0.35)
        recap = VGroup(last, steps).arrange(DOWN, buff=0.5).move_to(UP * 0.2)
        self.validator.check_in_frame(VGroup(crumb, recap))

        # SEE (silent): the trail.  HEAR: substitution in one sentence.
        n = self.narrate(
            id="intro_01",
            text="Last time, you solved substitution codes: find the real answer first, then give its new name.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.play(FadeIn(last))
        self.at_word(n, "real")
        self.play(FadeIn(steps[0], shift=UP * 0.2))
        self.at_word(n, "name")
        self.play(FadeIn(steps[1:], shift=UP * 0.2))
        self.wait_for_narration(n)

        # HEAR: today, whole sentences.  SEE: the title.
        title = fitted_text("Sentence Coding", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=CODE, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        n = self.narrate(
            id="intro_02",
            text="In this video, whole sentences are written in a code language, and we'll uncover each word's code.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(recap, shift=UP * 0.3))
        self.at_word(n, "sentences")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        # HEAR: the four objectives.  SEE: one row per objective, on its word.
        goals = [
            ("Match what two sentences share", FOCUS),
            ("Use elimination to find the rest", GOOD),
            ("Recognise “cannot be determined”", LINK),
            ("Ignore the order of the codes", BAD),
        ]
        rows = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s, SAFE_W - 2.4, BODY, INK))
                        .arrange(RIGHT, buff=0.35) for i, (s, c) in enumerate(goals)])
        rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        heading = text("By the end of this video, you will:", LABEL, MUTED, BOLD)
        objectives = self.card(VGroup(heading, rows).arrange(DOWN, buff=0.4, aligned_edge=LEFT))
        small_title = title.copy().scale(0.6)
        small_title.next_to(crumb, DOWN, buff=0.3)
        objectives.next_to(small_title, DOWN, buff=0.35)
        self.validator.check_in_frame(VGroup(crumb, small_title, objectives))
        n = self.narrate(
            id="intro_03",
            text="By the end of this video, you'll be able to match the words and codes that two sentences share, use "
                 "elimination to find the rest, recognise when a code cannot be determined, and ignore the order of "
                 "the codes.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row, spoken in zip(rows, ["match", "elimination", "recognise", "ignore"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Opening Hook")

        s1, s2, s3 = self.opening_sentences()
        question = self.question_card("What is the code for “they”?", t2c={"they": WORD})
        self.validator.check_in_frame(VGroup(question, s1, s3))

        # HEAR: the three coded sentences and the question.  SEE: one row per
        # "means", then the question card.
        n = self.narrate(
            id="hook_01",
            text="In a certain code language, pit na sa means you are good, na ho pa means they are bad, and ka sa ho "
                 "means good and bad. What's the code for they?",
            voice="default",
            subtitle=True,
        )
        for s, occurrence in zip([s1, s2, s3], [1, 2, 3]):
            self.at_word(n, "means", occurrence=occurrence)
            self.play(FadeIn(s, shift=RIGHT * 0.2), run_time=0.5)
        self.at_word(n, "code", occurrence=2)
        self.play(FadeIn(question, shift=DOWN * 0.3))
        self.wait_for_narration(n)

        # HEAR: codes aren't built from letters.  SEE: a tag.
        tag = pill("not built letter by letter", BAD, size=LABEL).move_to(UP * BOOK_Y)
        n = self.narrate(
            id="hook_02",
            text="You can't work this out letter by letter. The codes aren't built from the words at all. So how can "
                 "three sentences reveal the code for one word?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "letter", occurrence=1)
        self.play(FadeIn(tag, scale=1.1))
        self.at_word(n, "three")
        self.play(Indicate(VGroup(s1, s2, s3), color=FOCUS, scale_factor=1.02))
        self.wait_for_narration(n)

        # HEAR: the key idea.  SEE: caption.
        n = self.narrate(
            id="hook_03",
            text="The answer is a simple, powerful idea: what's common in the sentences is common in the codes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "common", occurrence=1)
        cap = self.caption("What's common in the sentences is common in the codes", GOOD)
        self.play(FadeOut(tag), FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========
    # Purpose: a word always has the same code, so a shared word means a
    # shared code.

    def concept(self):
        self.scene_start("S02_concept", title="Concept Introduction")

        s1 = Sentence("S1", ["pit", "na", "sa"], ["you", "are", "good"], 1.2)
        s2 = Sentence("S2", ["na", "ho", "pa"], ["they", "are", "bad"], -0.2)
        link1 = DashedLine(s1.word("are").get_bottom(), s2.word("are").get_top(), color=FOCUS)
        link2 = DashedLine(s1.code("na").get_bottom(), s2.code("na").get_top(), color=FOCUS)
        belong = pill("are  =  na", GOOD, size=LABEL).move_to(DOWN * 1.5)
        self.validator.check_in_frame(VGroup(s1, s2, belong))

        n = self.narrate(
            id="concept_01",
            text="In sentence coding, each word has a fixed code word, and a whole sentence is written as a set of "
                 "code words.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(s1, shift=RIGHT * 0.2))
        self.at_word(n, "sentence", occurrence=2)
        self.play(FadeIn(s2, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        # HEAR: same word, same code; one common word -> one common code.
        # SEE: "are" glows in both; "na" glows in both; they pair up.
        n = self.narrate(
            id="concept_02",
            text="The key fact is that a word always has the same code, in every sentence. So if a word appears in two "
                 "sentences, its code must also appear in both of their codes. And if exactly one word is common to "
                 "two sentences, exactly one code word is common to them, and those two must belong together.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "appears")
        self.play(self.match_words([s1, s2], "are"), Create(link1))
        self.at_word(n, "both")
        self.play(self.match_codes([s1, s2], "na"), Create(link2))
        self.at_word(n, "belong")
        self.play(FadeIn(belong, scale=1.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_03",
            text="That's the whole method. The rest is careful bookkeeping.",
            voice="default",
            subtitle=True,
        )
        cap = self.caption("One common word  ↔  one common code", GOOD)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    def match_words(self, sentences, word):
        return AnimationGroup(*[glow(s.word(word)) for s in sentences])

    def match_codes(self, sentences, code):
        return AnimationGroup(*[glow(s.code(code)) for s in sentences])

    # ======================================= 3. COMMON-WORD MATCHING ==========

    def matching(self):
        self.scene_start("S03_matching", title="Explanation - Common-word Matching")

        s1, s2, s3 = self.opening_sentences()
        book = CodeBook()
        self.play(FadeIn(VGroup(s1, s2, s3)), FadeIn(book.title))

        # HEAR: S1 and S2 share "are" and "na".  SEE: both glow; the pair goes
        # into the code book and turns green in every sentence.
        n = self.narrate(
            id="match_01",
            text="Take the first two sentences. The words you are good and they are bad share one word: are. The codes "
                 "pit na sa and na ho pa share one code: na. So are is na.",
            voice="default",
            subtitle=True,
        )
        self.play(self.dim(s3))
        self.at_word(n, "share", occurrence=1)
        self.play(self.match_words([s1, s2], "are"))
        self.at_word(n, "share", occurrence=2)
        self.play(self.match_codes([s1, s2], "na"))
        self.at_word(n, "So")
        entry = book.add("are", "na")
        self.play(FadeIn(entry, shift=DOWN * 0.2), self.settle([s1, s2], "are", "na"))
        self.wait_for_narration(n)

        # HEAR: S1 & S3 -> good = sa; S2 & S3 -> bad = ho.
        n = self.narrate(
            id="match_02",
            text="Repeat for other pairs. Sentences one and three share good, and their codes share sa. So good is sa. "
                 "Sentences two and three share bad, and their codes share ho. So bad is ho.",
            voice="default",
            subtitle=True,
        )
        self.play(self.undim(s3), self.dim(s2))
        self.at_word(n, "good", occurrence=1)
        self.play(self.match_words([s1, s3], "good"))
        self.at_word(n, "sa", occurrence=1)
        self.play(self.match_codes([s1, s3], "sa"))
        self.at_word(n, "So", occurrence=1)
        entry = book.add("good", "sa")
        self.play(FadeIn(entry, shift=DOWN * 0.2), self.settle([s1, s3], "good", "sa"))
        self.play(self.undim(s2), self.dim(s1))
        self.at_word(n, "bad", occurrence=1)
        self.play(self.match_words([s2, s3], "bad"))
        self.at_word(n, "ho", occurrence=1)
        self.play(self.match_codes([s2, s3], "ho"))
        self.at_word(n, "So", occurrence=2)
        entry = book.add("bad", "ho")
        self.play(FadeIn(entry, shift=DOWN * 0.2), self.settle([s2, s3], "bad", "ho"), self.undim(s1))
        self.validator.check_in_frame(VGroup(s1, s3, book.title, book.entries))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_matching")

    # ============================================ 4. ELIMINATION ==========

    def elimination(self):
        self.scene_start("S04_elimination", title="Explanation - Elimination")

        s1, s2, s3 = self.opening_sentences()
        book = CodeBook()
        known = [book.add("are", "na"), book.add("good", "sa"), book.add("bad", "ho")]
        for s in (s1, s2, s3):
            for w, c in [("are", "na"), ("good", "sa"), ("bad", "ho")]:
                if w in s.words_list:
                    s.word(w)[0].set_stroke(GOOD, 3).set_fill(GOOD, 0.28)
                    s.word(w)[1].set_color(GOOD)
                if c in s.codes_list:
                    s.code(c)[0].set_stroke(GOOD, 3).set_fill(GOOD, 0.28)
                    s.code(c)[1].set_color(GOOD)
        self.play(FadeIn(VGroup(s1, s2, s3)), FadeIn(book.title), FadeIn(VGroup(*known)))

        # HEAR: S2 has na, ho, pa; are = na, bad = ho; only pa is left.
        # SEE: S2 in focus; the known pairs fade; they and pa light up.
        n = self.narrate(
            id="elim_01",
            text="Now use elimination. Sentence two, they are bad, has the codes na, ho and pa. We know are is na and "
                 "bad is ho. The only code left is pa, so they is pa.",
            voice="default",
            subtitle=True,
        )
        self.play(self.dim(s1), self.dim(s3))
        self.at_word(n, "know")
        self.play(*[m.animate.fade(0.7) for m in (s2.word("are"), s2.code("na"), s2.word("bad"), s2.code("ho"))])
        self.at_word(n, "left")
        self.play(glow(s2.code("pa")), glow(s2.word("they")))
        entry = book.add("they", "pa", FOCUS)
        self.play(FadeIn(entry, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        # HEAR: you = pit, and = ka.  SEE: two more entries.
        n = self.narrate(
            id="elim_02",
            text="That answers the question. The same reasoning gives you as pit, and and as ka.",
            voice="default",
            subtitle=True,
        )
        self.play(self.undim(s1), self.undim(s3))
        self.at_word(n, "pit")
        e1 = book.add("you", "pit")
        self.play(FadeIn(e1, shift=DOWN * 0.2), glow(s1.word("you"), GOOD), glow(s1.code("pit"), GOOD))
        self.at_word(n, "ka")
        e2 = book.add("and", "ka")
        self.play(FadeIn(e2, shift=DOWN * 0.2), glow(s3.word("and"), GOOD), glow(s3.code("ka"), GOOD))
        self.validator.check_in_frame(VGroup(book.title, book.entries))
        self.wait_for_narration(n)

        # HEAR: code order means nothing.  SEE: position badges under "are"
        # and "na" in S1 and S2: 2nd/2nd, then 2nd/1st.
        self.play(FadeOut(VGroup(s3, book.title, book.entries)))
        b = lambda s, target: pill(s, FOCUS, size=SMALL).next_to(target, DOWN, buff=0.12)
        badges = [b("2nd", s1.word("are")), b("2nd", s1.code("na")), b("2nd", s2.word("are")), b("1st", s2.code("na"))]
        n = self.narrate(
            id="elim_03",
            text="Notice one thing. In sentence one, are is the second word and na is the second code. But in sentence "
                 "two, are is again second, and na is first. Code order tells you nothing. Always match by what's "
                 "common, never by position.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "second", occurrence=1)
        self.play(FadeIn(badges[0]))
        self.at_word(n, "second", occurrence=2)
        self.play(FadeIn(badges[1]))
        self.at_word(n, "again")
        self.play(FadeIn(badges[2]))
        self.at_word(n, "first")
        self.play(FadeIn(badges[3]), badges[3][0].animate.set_stroke(BAD), badges[3][1].animate.set_color(BAD))
        self.at_word(n, "nothing")
        cap = self.caption("Code order does NOT follow word order: match by what is common", BAD)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_elimination")

    # ======================================= 5. CANNOT BE DETERMINED ==========

    def cannot_determine(self):
        self.scene_start("S05_cannot", title="Explanation - Cannot Be Determined")

        rule = self.card(fitted_text("If two words appear only together, their codes cannot be separated",
                                     SAFE_W - 1.2, BODY, INK, max_lines=2), color=LINK)
        rule.move_to(UP * (CARD_TOP - rule.height / 2))
        pair = undetermined(["is", "sweet"], ["ro", "su"]).move_to(UP * 0.1)
        verdict = pill("cannot be determined", GOOD, size=BODY).move_to(DOWN * 2.0)
        self.validator.check_in_frame(VGroup(rule, pair, verdict))

        n = self.narrate(
            id="cannot_01",
            text="Sometimes the given sentences simply don't contain enough information. If two words always appear "
                 "together, or each appears in only one sentence, you can narrow them down to a pair of codes, but you "
                 "can't tell which code belongs to which word.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(rule, shift=DOWN * 0.2))
        self.at_word(n, "together")
        self.play(FadeIn(pair[0]), FadeIn(pair[1]))
        self.at_word(n, "which", occurrence=1)
        self.play(Create(pair[2]), FadeIn(pair[3], scale=1.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="cannot_02",
            text="In that situation, the correct answer is cannot be determined. It isn't a trick option. Choosing it "
                 "confidently is part of the skill.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cannot")
        self.play(FadeIn(verdict, scale=1.1))
        self.at_word(n, "confidently")
        self.play(Indicate(verdict, color=GOOD, scale_factor=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_cannot")

    # ==================================== 6. EXAMPLE 1: CODE FOR THEY ==========

    def example_they(self):
        self.scene_start("S06_example_they", title="Example 1 - Basic")

        s1, s2, s3 = self.opening_sentences()
        answer = pill("they  =  pa", GOOD, size=BODY).move_to(UP * BOOK_Y)
        self.play(FadeIn(VGroup(s1, s2, s3)))

        n = self.narrate(
            id="ex1_01",
            text="Our opening question is already solved: they is pa. Notice that we needed all three sentences. Two "
                 "of them gave us the codes for are and bad, and elimination did the rest.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pa")
        self.play(glow(s2.word("they"), GOOD), glow(s2.code("pa"), GOOD), FadeIn(answer, scale=1.1))
        self.at_word(n, "three")
        self.play(Indicate(VGroup(s1, s2, s3), color=FOCUS, scale_factor=1.02))
        self.at_word(n, "are")
        self.play(self.match_words([s1, s2], "are"), self.match_codes([s1, s2], "na"))
        self.at_word(n, "bad")
        self.play(self.match_words([s2, s3], "bad"), self.match_codes([s2, s3], "ho"))
        self.at_word(n, "elimination")
        self.play(Circumscribe(VGroup(s2.word("they"), s2.code("pa"), answer), color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_example_they")

    # ================================ 7. EXAMPLE 2: DRINK and SWEET ==========

    def example_juice(self):
        self.scene_start("S07_example_juice", title="Example 2 - Application")

        s1, s2, s3 = self.juice_sentences()
        question = self.question_card("(a) Code for “drink”?     (b) Code for “sweet”?", t2c={"drink": WORD, "sweet": WORD})
        book = CodeBook()
        self.validator.check_in_frame(VGroup(question, s1, s3, book.title))

        n = self.narrate(
            id="ex2_01",
            text="In a code, mi ko ta means drink fresh juice, ta ro su means juice is sweet, and ko pe lu means fresh "
                 "cold water. What's the code for drink? And what's the code for sweet?",
            voice="default",
            subtitle=True,
        )
        for s, occurrence in zip([s1, s2, s3], [1, 2, 3]):
            self.at_word(n, "means", occurrence=occurrence)
            self.play(FadeIn(s, shift=RIGHT * 0.2), run_time=0.5)
        self.at_word(n, "What's")
        self.play(FadeIn(question, shift=DOWN * 0.3), FadeIn(book.title))
        self.wait_for_narration(n)

        # HEAR: juice = ta, fresh = ko, drink = mi.
        n = self.narrate(
            id="ex2_02",
            text="Sentences one and two share juice and ta. So juice is ta. Sentences one and three share fresh and ko. "
                 "So fresh is ko. In sentence one, the only code left is mi. So drink is mi.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "juice", occurrence=1)
        self.play(self.match_words([s1, s2], "juice"), self.match_codes([s1, s2], "ta"))
        self.at_word(n, "So", occurrence=1)
        e = book.add("juice", "ta")
        self.play(FadeIn(e, shift=DOWN * 0.2), self.settle([s1, s2], "juice", "ta"))
        self.at_word(n, "fresh", occurrence=1)
        self.play(self.match_words([s1, s3], "fresh"), self.match_codes([s1, s3], "ko"))
        self.at_word(n, "So", occurrence=2)
        e = book.add("fresh", "ko")
        self.play(FadeIn(e, shift=DOWN * 0.2), self.settle([s1, s3], "fresh", "ko"))
        self.at_word(n, "left")
        self.play(glow(s1.code("mi")), glow(s1.word("drink")))
        self.at_word(n, "So", occurrence=3)
        e = book.add("drink", "mi", FOCUS)
        self.play(FadeIn(e, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        # HEAR: sweet: {is, sweet} share {ro, su}; no other sentence helps.
        pair = undetermined(["is", "sweet"], ["ro", "su"]).scale(0.7).move_to(RIGHT_ZONE + DOWN * 2.3)
        n = self.narrate(
            id="ex2_03",
            text="Now for sweet. In sentence two, we know juice is ta. That leaves is and sweet to share the codes ro "
                 "and su. Neither word appears in any other sentence, so there's no way to separate them.",
            voice="default",
            subtitle=True,
        )
        self.play(self.dim(s1), self.dim(s3))
        self.at_word(n, "leaves")
        self.play(*[glow(m, LINK) for m in (s2.word("is"), s2.word("sweet"), s2.code("ro"), s2.code("su"))])
        self.at_word(n, "Neither")
        self.play(FadeIn(pair, shift=UP * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex2_04",
            text="The code for sweet is either ro or su. The answer is cannot be determined.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "answer")
        e = book.add("sweet", "?", LINK)
        self.play(FadeIn(e, shift=DOWN * 0.2))
        verdict = pill("cannot be determined", GOOD, size=LABEL).move_to(LEFT_ZONE + DOWN * 2.35)
        self.play(FadeIn(verdict, scale=1.1))
        self.validator.check_in_frame(VGroup(book.entries, pair, verdict))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_example_juice")

    # =================================== 8. EXAMPLE 3: "COULD BE" ==========

    def example_could_be(self):
        self.scene_start("S08_example_could", title="Example 3 - Exam-Oriented")

        s1, s2, s3 = self.juice_sentences()
        question = self.question_card("Which could be the code for “cold juice”?", t2c={"could": FOCUS})
        opts = VGroup(*[pill(f"({k})  {c}", INK, size=LABEL, fill_opacity=0.06)
                        for k, c in zip("abcd", ["ta pe", "ko pe", "mi lu", "ro ta"])]).arrange(RIGHT, buff=0.4)
        fit_width(opts, SAFE_W).move_to(UP * BOOK_Y)
        cross = lambda o: AnimationGroup(o[0].animate.set_stroke(BAD, 2).set_fill(BAD, 0.12),
                                         o[1].animate.set_color(BAD))
        self.validator.check_in_frame(VGroup(question, s1, s3, opts))

        n = self.narrate(
            id="ex3_01",
            text="Exam questions often ask which option could be the code for a phrase. Using the same code language, "
                 "which of these could be the code for cold juice?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(VGroup(s1, s2, s3)), FadeIn(question, shift=DOWN * 0.3))
        self.at_word(n, "these")
        self.play(LaggedStart(*[FadeIn(o, shift=UP * 0.2) for o in opts], lag_ratio=0.2))
        self.wait_for_narration(n)

        # HEAR: juice = ta must be present: keeps a and d.
        n = self.narrate(
            id="ex3_02",
            text="Juice is definitely ta, so the correct option must contain ta. That leaves only options a and d.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ta", occurrence=1)
        self.play(glow(s1.code("ta"), GOOD), glow(s2.code("ta"), GOOD), glow(s1.word("juice"), GOOD),
                  glow(s2.word("juice"), GOOD))
        self.at_word(n, "leaves")
        self.play(cross(opts[1]), cross(opts[2]))
        self.wait_for_narration(n)

        # HEAR: cold is pe or lu, never ro.  SEE: S3's leftover pair; (d) out.
        n = self.narrate(
            id="ex3_03",
            text="Cold appears only in sentence three, alongside water. So cold is either pe or lu. It can't be ro, "
                 "because ro belongs to is or sweet.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(*[glow(m, LINK) for m in (s3.word("cold"), s3.word("water"), s3.code("pe"), s3.code("lu"))])
        self.at_word(n, "ro", occurrence=1)
        self.play(glow(s2.code("ro"), BAD))
        self.play(cross(opts[3]))
        self.wait_for_narration(n)

        # HEAR: (a) ta pe is the only possible option.
        n = self.narrate(
            id="ex3_04",
            text="So the answer is a, ta pe. The word could matters. We can't say for certain that cold is pe, but ta "
                 "pe is the only option that's possible.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "answer")
        self.play(glow(opts[0], GOOD), Flash(opts[0], color=GOOD))
        self.at_word(n, "could")
        cap = self.caption("“Could be”  →  possible, not certain", FOCUS)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_example_could")

    # ======================================== 9. EXAM APPLICATION ==========

    def exam_application(self):
        self.scene_start("S09_exam", title="Exam Application")

        rows = self.step_rows([
            ("Sentence pairs sharing exactly one word  →  match codes", FOCUS),
            ("Eliminate known codes within each sentence", GOOD),
            ("Leftover pair, no other clue  →  cannot be determined", LINK),
            ("“Could be”  →  keep what is possible, reject the impossible", CODE),
        ], SAFE_W - 0.8)
        heading = text("The exam routine", LABEL, MUTED, BOLD)
        routine = self.card(VGroup(heading, rows).arrange(DOWN, buff=0.3, aligned_edge=LEFT)).move_to(UP * 0.6)
        self.validator.check_in_frame(routine)

        n = self.narrate(
            id="exam_01",
            text="Here's the exam routine. First, find pairs of sentences that share exactly one word, and match their "
                 "codes. Second, eliminate known codes inside each sentence to find the rest. Third, if two words are "
                 "left sharing two codes with no other clue, the answer is cannot be determined. Fourth, for could be "
                 "questions, keep any option that is possible, and reject any option that contradicts what you know.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(routine[0]), FadeIn(heading))
        for row, spoken in zip(rows, ["First", "Second", "Third", "Fourth"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_02",
            text="Always start with the word the question asks about, and trace only the sentences that contain it. "
                 "You rarely need to decode every word.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "start")
        cap = self.caption("Start from the asked word; trace only its sentences", FOCUS)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_exam")

    # =========================================== 10. COMMON MISTAKE ==========

    def common_mistake(self):
        self.scene_start("S10_mistake", title="Common Mistake")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "“are” is the 2nd word, so its code is the 2nd code", card_w),
             self.verdict_card(True, "Match by what is common, not by position", card_w)),
            (self.verdict_card(False, "Pick ro or su for “sweet” anyway", card_w),
             self.verdict_card(True, "No clue to separate them: cannot be determined", card_w)),
            (self.verdict_card(False, "“they” appears once: cannot be determined", card_w),
             self.verdict_card(True, "Try elimination first: they = pa", card_w)),
        ]
        for (wrong, right), y in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * y)
            right.move_to(RIGHT_ZONE + UP * y)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistake_01",
            text="The first mistake is matching by position, assuming the second word's code is the second code. "
                 "Code order is shuffled on purpose.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        self.at_word(n, "position")
        self.play(FadeIn(pairs[0][0], shift=RIGHT * 0.3))
        self.at_word(n, "shuffled")
        self.play(FadeIn(pairs[0][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mistake_02",
            text="The second mistake is forcing an answer when the information isn't there. If is and sweet share ro "
                 "and su, and neither appears elsewhere, picking either one is a guess. Choose cannot be determined.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "forcing")
        self.play(FadeIn(pairs[1][0], shift=RIGHT * 0.3))
        self.at_word(n, "Choose")
        self.play(FadeIn(pairs[1][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mistake_03",
            text="The third mistake is the reverse: choosing cannot be determined too quickly, before trying "
                 "elimination. In the opening question, they appears only once, yet its code was fully determined. "
                 "Elimination worked where direct matching didn't.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "quickly")
        self.play(FadeIn(pairs[2][0], shift=RIGHT * 0.3))
        self.at_word(n, "determined", occurrence=2)
        self.play(FadeIn(pairs[2][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_mistake")

    # ================================================ 11. PRACTICE ==========

    def practice_sentences(self):
        return [Sentence("S1", ["dum", "pa", "li"], ["blue", "sky", "above"], ROWS_Y[0]),
                Sentence("S2", ["li", "so", "ke"], ["above", "the", "clouds"], ROWS_Y[1]),
                Sentence("S3", ["ke", "dum", "ra"], ["clouds", "and", "sky"], ROWS_Y[2])]

    def practice(self):
        self.scene_start("S11_practice", title="Practice Question")

        s1, s2, s3 = self.practice_sentences()
        qs = VGroup(pill("Q1  code for “blue”?", FOCUS, size=LABEL),
                    pill("Q2  code for “the”?", FOCUS, size=LABEL)).arrange(RIGHT, buff=0.6).move_to(UP * BOOK_Y)
        self.validator.check_in_frame(VGroup(s1, s3, qs))

        n = self.narrate(
            id="practice_01",
            text="Try this one.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(pill("Your turn", FOCUS, size=LABEL).move_to(UP * (CARD_TOP - 0.35))))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Dum pa li means blue sky above. Li so ke means above the clouds. Ke dum ra means clouds and sky.",
            voice="default",
            subtitle=True,
        )
        for s, occurrence in zip([s1, s2, s3], [1, 2, 3]):
            self.at_word(n, "means", occurrence=occurrence)
            self.play(FadeIn(s, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        # SILENCE (pause_after): countdown ring while the learner thinks.
        n = self.narrate(
            id="practice_03",
            text="What's the code for blue? And what's the code for the?",
            voice="default",
            subtitle=True,
            pause_after=8.0,
        )
        self.play(FadeIn(qs[0], shift=UP * 0.2))
        self.at_word(n, "And")
        self.play(FadeIn(qs[1], shift=UP * 0.2))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S11_practice")

    # ================================================== 12. ANSWER ==========

    def answer(self):
        self.scene_start("S12_answer", title="Answer and Explanation")

        s1, s2, s3 = self.practice_sentences()
        book = CodeBook()
        self.play(FadeIn(VGroup(s1, s2, s3)), FadeIn(book.title))

        # HEAR: three pairwise matches.  SEE: each pair glows, then settles.
        n = self.narrate(
            id="answer_01",
            text="Sentences one and two share above and li. Sentences one and three share sky and dum. Sentences two "
                 "and three share clouds and ke.",
            voice="default",
            subtitle=True,
        )
        for (a, b), (w, c) in zip([(s1, s2), (s1, s3), (s2, s3)], [("above", "li"), ("sky", "dum"), ("clouds", "ke")]):
            self.at_word(n, c)
            self.play(self.match_words([a, b], w), self.match_codes([a, b], c), run_time=0.5)
            e = book.add(w, c)
            self.play(FadeIn(e, shift=DOWN * 0.2), self.settle([a, b], w, c), run_time=0.5)
        self.wait_for_narration(n)

        # HEAR: S1: remove dum and li -> blue = pa.
        n = self.narrate(
            id="answer_02",
            text="In sentence one, blue sky above is dum, pa and li. Remove dum and li, and blue is pa.",
            voice="default",
            subtitle=True,
        )
        self.play(self.dim(s2), self.dim(s3))
        self.at_word(n, "Remove")
        self.play(*[m.animate.fade(0.7) for m in (s1.code("dum"), s1.code("li"), s1.word("sky"), s1.word("above"))])
        self.at_word(n, "pa", occurrence=2)
        e = book.add("blue", "pa", FOCUS)
        self.play(glow(s1.word("blue")), glow(s1.code("pa")), FadeIn(e, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        # HEAR: S2: remove li and ke -> the = so.
        n = self.narrate(
            id="answer_03",
            text="In sentence two, above the clouds is li, so and ke. Remove li and ke, and the is so.",
            voice="default",
            subtitle=True,
        )
        self.play(self.undim(s2), self.dim(s1))
        self.at_word(n, "Remove")
        self.play(*[m.animate.fade(0.7) for m in (s2.code("li"), s2.code("ke"), s2.word("above"), s2.word("clouds"))])
        self.at_word(n, "so", occurrence=2)
        e = book.add("the", "so", FOCUS)
        self.play(glow(s2.word("the")), glow(s2.code("so")), FadeIn(e, shift=DOWN * 0.2))
        self.validator.check_in_frame(VGroup(book.title, book.entries))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answer_04",
            text="Both codes can be determined, because each sentence has only one word left after elimination.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        cap = self.caption("One word left after elimination  →  determined", GOOD)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_answer")

    # ========================================== 13. QUICK REVISION ==========

    def quick_revision(self):
        self.scene_start("S13_revision", title="Quick Revision")

        card_w, card_h = SAFE_W - 1.0, 5.0
        items = [
            ("Same word  →  same code, in every sentence", WORD),
            ("One common word between two sentences  ↔  one common code", FOCUS),
            ("Eliminate known codes to find the rest", GOOD),
            ("Code order is meaningless", BAD),
            ("Two unresolved words sharing two codes  →  cannot be determined", LINK),
            ("“Could be”  →  possible, not certain", CODE),
        ]
        bullets = VGroup(*[VGroup(Dot(radius=0.07, color=c), fitted_text(s, card_w - 1.4, BODY, c, max_lines=2))
                           .arrange(RIGHT, buff=0.3) for s, c in items]).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        board = self.card(bullets, width=card_w, height=card_h).move_to(DOWN * 0.1)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="revision_01",
            text="To revise: a word always has the same code. So a word common to two sentences matches the code "
                 "common to them. Once some codes are known, eliminate them to reveal the others.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        self.play(FadeIn(bullets[0], shift=RIGHT * 0.2))
        self.at_word(n, "matches")
        self.play(FadeIn(bullets[1], shift=RIGHT * 0.2))
        self.at_word(n, "eliminate")
        self.play(FadeIn(bullets[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="revision_02",
            text="Ignore the order of codes. When two words share two codes with no further clue, the answer is cannot "
                 "be determined. And in could be questions, choose what is possible, not what is certain.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(bullets[3], shift=RIGHT * 0.2))
        self.at_word(n, "When")
        self.play(FadeIn(bullets[4], shift=RIGHT * 0.2))
        self.at_word(n, "could")
        self.play(FadeIn(bullets[5], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S13_revision")

    # ================================================= 14. CLOSING ==========
    # Purpose: teaser for Symbol & Conditional Coding: a letter-to-symbol
    # table with a condition.

    def closing(self):
        self.scene_start("S14_closing", title="Closing")

        letters = ["A", "B", "C", "D", "E"]
        symbols = ["#", "@", "5", "%", "8"]
        top = VGroup(*[pill(x, WORD, size=BODY, fill_opacity=0.08) for x in letters]).arrange(RIGHT, buff=0.35)
        bottom = VGroup(*[pill(x, CODE, size=BODY, fill_opacity=0.08) for x in symbols])
        for b, t in zip(bottom, top):
            b.next_to(t, DOWN, buff=0.35)
        table = VGroup(top, bottom).move_to(UP * 1.0)
        condition = pill("if the first letter is a vowel …", FOCUS, size=LABEL).move_to(DOWN * 0.7)
        nxt = pill("Next:  Symbol & Conditional Coding", CODE, size=BODY).move_to(DOWN * 2.1)
        self.validator.check_in_frame(VGroup(table, condition, nxt))

        n = self.narrate(
            id="closing_01",
            text="In the final topic of this lesson, letters are replaced by digits and symbols, and special conditions "
                 "change the code depending on the word. It's a test of careful reading, and we'll build a routine for "
                 "it next.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "letters")
        self.play(FadeIn(top, shift=DOWN * 0.2))
        self.at_word(n, "symbols")
        self.play(LaggedStart(*[FadeIn(b, shift=DOWN * 0.15) for b in bottom], lag_ratio=0.2))
        self.at_word(n, "conditions")
        self.play(FadeIn(condition, scale=1.1))
        self.at_word(n, "routine")
        self.play(FadeIn(nxt, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S14_closing")
