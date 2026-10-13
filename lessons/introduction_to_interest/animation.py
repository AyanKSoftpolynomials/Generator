"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A
Module : Module 5 - Quantitative Aptitude
Lesson : Lesson 11 - Simple & Compound Interest
Topic  : Introduction to Interest (Video 1 of 7)

Source script:
  C:\\Users\\User\\Downloads\\Aptitude_Course_Modules_v4\\Quantitative Aptitude\\
  Module 5 - Quantitative Aptitude\\Lesson 11 - Simple & Compound Interest\\
  01 - Introduction to Interest.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``.

Opening: not the first video of the course, so no spoken course welcome.
The module > lesson > video trail is shown on screen (silent), followed by a
one-idea recap of the Module Introduction (READ > MODEL > SOLVE > CHECK) and
what this video covers.

Section map (script heading -> scene):
  S00 Intro (trail + recap)        -> -
  S01 Hook                         -> loan-app screen
  S02 Objectives                   -> checklist
  S03 What is it? Why important?   -> "Interest" title card, P R T I A
  S04 The Analogy                  -> flat for rent
  S05 Formula, Derived (terms)     -> five definitions, A = P + I
  S06 Formula, Derived (units)     -> 2% bar stretches into 12 bars
  S07 Formula Box                  -> formula card
  S08 Worked Example               -> 500 hundreds x Rs 24
  S09 Common Trap                  -> red wrong step, green corrected step
  S10 Interactive Pause            -> 10-second countdown, 1.5% x 6 = 9%
  S11-S12 Practice / Answer key    -> 4 questions, 4 answer cards
  S13 Quick Revision + Summary     -> objectives tick off, rent picture, box
"""

import math

from manim import *

from src.animation import LMSScene

# ============================================================== style ====

BG = "#0B1020"
INK = "#E6EAF2"
MUTED = "#8B95A7"
PANEL = "#151C2E"
CELL = "#1B2440"

# Semantic colours: one meaning each, kept for the whole interest lesson.
P_COL = "#4FC3F7"      # principal
R_COL = "#FFB74D"      # rate
T_COL = "#CE93D8"      # time
I_COL = "#F48FB1"      # interest
A_COL = "#80CBC4"      # amount
FOCUS = "#FFD54F"      # "look here" / unknown
GOOD = "#66BB6A"       # correct / answer
BAD = "#EF5350"        # wrong / trap

FONT = "Segoe UI"
MIN_FONT = 22          # readable floor: text is never shrunk below this
TITLE = 46
BODY = 30
LABEL = 28
SMALL = 24
MATH = 44

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


def math_line(*parts, colors=None, size=MATH):
    """MathTex split into ``parts``, each part coloured from ``colors``."""
    colors = colors or {}
    line = MathTex(*parts, font_size=size, color=INK)
    for part, sub in zip(parts, line):
        if part in colors:
            sub.set_color(colors[part])
    return line


def pill(label, color=FOCUS, size=SMALL, fill_opacity=0.14):
    """Short keyword tag. The box is sized from the text, so text cannot escape."""
    t = text(label, size, color, BOLD)
    box = RoundedRectangle(corner_radius=(t.height + 0.26) / 2, width=t.width + 0.5, height=t.height + 0.26,
                           stroke_color=color, stroke_width=2, fill_color=color, fill_opacity=fill_opacity)
    t.move_to(box)
    return VGroup(box, t)


def verdict(ok, size=LABEL):
    return text("✓" if ok else "✗", size, GOOD if ok else BAD, BOLD)


# ==================================================== diagram helpers ====

# The five words of interest, in the order the script defines them.
TERMS = [("P", "Principal", P_COL), ("R", "Rate", R_COL), ("T", "Time", T_COL),
         ("I", "Interest", I_COL), ("A", "Amount", A_COL)]


def symbol_tile(letter, color, side=0.9):
    """One term letter (P, R, T, I, A) in a rounded square."""
    sq = RoundedRectangle(corner_radius=0.12, width=side, height=side, stroke_color=color,
                          stroke_width=3, fill_color=color, fill_opacity=0.14)
    return VGroup(sq, text(letter, int(side * 52), color, BOLD).move_to(sq))


def term_tile(letter, word, color, side=0.9):
    """Letter tile with its full name underneath."""
    return VGroup(symbol_tile(letter, color, side), text(word, SMALL, color)).arrange(DOWN, buff=0.18)


def house(width=2.2, color=P_COL):
    """A flat to rent: body, roof, door and two windows."""
    body = Rectangle(width=width, height=width * 0.8, stroke_color=color, stroke_width=3,
                     fill_color=color, fill_opacity=0.12)
    roof = Polygon(body.get_corner(UL) + LEFT * 0.2, body.get_corner(UR) + RIGHT * 0.2,
                   body.get_top() + UP * width * 0.45, stroke_color=color, stroke_width=3,
                   fill_color=color, fill_opacity=0.25)
    door = Rectangle(width=width * 0.2, height=width * 0.36, stroke_color=color, stroke_width=2,
                     fill_color=CELL, fill_opacity=1)
    door.move_to(body.get_bottom(), aligned_edge=DOWN)
    windows = VGroup(*[Square(width * 0.18, stroke_color=color, stroke_width=2, fill_color=CELL, fill_opacity=1)
                       for _ in range(2)]).arrange(RIGHT, buff=width * 0.3)
    windows.move_to(body.get_center() + UP * width * 0.14)
    return VGroup(body, roof, door, windows)


def bar(width, height, color, opacity=0.35):
    return Rectangle(width=width, height=height, stroke_color=color, stroke_width=2,
                     fill_color=color, fill_opacity=opacity)


def hundreds_grid(cols=25, rows=20, side=0.12, gap=0.025, color=P_COL):
    """cols x rows small squares, one per Rs 100 (25 x 20 = 500 hundreds)."""
    cells = VGroup(*[Square(side, stroke_width=0, fill_color=color, fill_opacity=0.75)
                     for _ in range(cols * rows)])
    cells.arrange_in_grid(rows=rows, cols=cols, buff=gap)
    return cells


def year_strip(months_on, cell=0.46, gap=0.05, color=T_COL):
    """Twelve month cells; the first ``months_on`` are filled."""
    cells = VGroup(*[Square(cell, stroke_color=color if k < months_on else MUTED, stroke_width=2,
                            fill_color=color, fill_opacity=0.45 if k < months_on else 0.0)
                     for k in range(12)])
    return cells.arrange(RIGHT, buff=gap)


# ============================================================= lesson ====

class IntroductionToInterestVideo(LMSScene):
    lesson_title = "Introduction to Interest"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.objectives()
        self.what_and_why()
        self.analogy()
        self.definitions()
        self.matching_units()
        self.formula_box_scene()
        self.worked_example()
        self.common_trap()
        self.interactive_pause()
        self.practice()
        self.answer()
        self.quick_revision()

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

    def question_card(self, s, color=FOCUS):
        """The on-screen question: one fitted line (or two) in a card at the top."""
        t = fitted_text(s, SAFE_W - 1.6, BODY, INK, max_lines=2)
        c = self.card(t, color=color)
        return c.move_to(UP * (CARD_TOP - c.height / 2))

    def caption(self, s, color=INK):
        """One-line keyword caption in a fixed-width bar at the bottom of the frame."""
        t = fitted_text(s, SAFE_W - 1.0, BODY, color)
        bar_ = self.card(t, width=SAFE_W - 0.4, height=t.height + 0.9)
        return bar_.move_to(UP * BOTTOM_Y)

    def breadcrumb(self, *parts):
        """Silent 'where are we' trail: Module > Lesson > Video."""
        colors = [P_COL, I_COL, R_COL]
        items = []
        for i, p in enumerate(parts):
            if i:
                items.append(text("›", LABEL, MUTED))
            items.append(pill(p, colors[i % 3], size=SMALL))
        return fit_width(VGroup(*items).arrange(RIGHT, buff=0.25), SAFE_W)

    def verdict_card(self, good, s, width):
        """A ✓ (green) or ✗ (red) card with fitted text."""
        color = GOOD if good else BAD
        body = VGroup(verdict(good, 34), fitted_text(s, width - 1.3, BODY, color, max_lines=2)).arrange(RIGHT, buff=0.25)
        return self.card(body, width=width, height=1.3, color=color)

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

    def objectives_card(self):
        """The two objectives as a checklist. Returns (card, rows, boxes)."""
        goals = [
            "Define P, R, T, I and A, and connect them with A = P + I",
            "Convert rates and time into matching units before you calculate",
        ]
        boxes, rows = VGroup(), VGroup()
        for g in goals:
            box = RoundedRectangle(corner_radius=0.06, width=0.42, height=0.42, stroke_color=MUTED, stroke_width=2.5)
            boxes.add(box)
            rows.add(VGroup(box, fitted_text(g, SAFE_W - 2.6, BODY, INK, max_lines=2)).arrange(RIGHT, buff=0.35))
        rows.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        heading = text("By the end of this video, you will be able to:", LABEL, MUTED, BOLD)
        c = self.card(VGroup(heading, rows).arrange(DOWN, buff=0.45, aligned_edge=LEFT), color=FOCUS)
        return c, rows, boxes

    def formula_box(self):
        """The script's Formula Box, as a card."""
        lines = VGroup(
            text("A = P + I   (Amount = Principal + Interest)", BODY, INK, BOLD),

            text("Monthly rate × 12 = yearly rate", BODY, R_COL, BOLD),
            text("Months ÷ 12 = years", BODY, T_COL, BOLD),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        heading = text("Formula Box", SMALL, MUTED, BOLD)
        return self.card(VGroup(heading, lines).arrange(DOWN, buff=0.35, aligned_edge=LEFT), color=P_COL, pad=0.4)

    def loan_phone(self):
        """The loan-app screen from the hook. Parts are kept as attributes."""
        body = RoundedRectangle(corner_radius=0.35, width=3.4, height=5.3, stroke_color=MUTED, stroke_width=3,
                                fill_color=PANEL, fill_opacity=1)
        notch = RoundedRectangle(corner_radius=0.06, width=0.9, height=0.12, stroke_width=0,
                                 fill_color=MUTED, fill_opacity=1)
        notch.move_to(body.get_top() + DOWN * 0.22)
        banner_text = VGroup(fitted_text("Instant cash!", 2.6, LABEL, R_COL, BOLD),
                             fitted_text("Just 2% interest per month", 2.6, SMALL, INK, max_lines=2))
        banner_text.arrange(DOWN, buff=0.12)
        banner = VGroup(RoundedRectangle(corner_radius=0.15, width=2.9, height=banner_text.height + 0.4,
                                         stroke_color=R_COL, stroke_width=2, fill_color=R_COL, fill_opacity=0.15),
                        banner_text)
        banner_text.move_to(banner[0])
        need = text("You need", SMALL, MUTED)
        amount = text("₹50,000", 50, P_COL, BOLD)
        track = Line(LEFT * 1.2, RIGHT * 1.2, color=MUTED, stroke_width=6)
        fill = Line(LEFT * 1.2, RIGHT * 0.7, color=P_COL, stroke_width=6)
        knob = Dot(RIGHT * 0.7, radius=0.15, color=P_COL)
        slider = VGroup(track, fill, knob)
        button = pill("Borrow now", GOOD, size=SMALL)
        content = VGroup(banner, need, amount, slider, button).arrange(DOWN, buff=0.35)
        content.move_to(body).shift(DOWN * 0.1)
        self.validator.check_fit(content, body, margin=0.1)
        phone = VGroup(body, notch, content)
        phone.banner, phone.rate_line, phone.amount, phone.slider, phone.knob = (
            banner, banner_text[1], amount, slider, knob)
        return phone

    # ========================================= 0. LESSON INTRO ==========
    # Purpose: where we are (silent trail), last time (one idea), today.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("Module 5 · Quantitative Aptitude", "Lesson 11 · Simple & Compound Interest",
                                "Video 1")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        last = pill("Last time", MUTED, size=SMALL).move_to(UP * 1.7)
        steps = VGroup(*[pill(s, c, size=LABEL) for s, c in
                         [("READ", P_COL), ("MODEL", R_COL), ("SOLVE", I_COL), ("CHECK", GOOD)]])
        steps.arrange(RIGHT, buff=0.9).move_to(UP * 0.3)
        arrows = VGroup(*[Arrow(a.get_right(), b.get_left(), buff=0.12, color=MUTED, stroke_width=4,
                                max_tip_length_to_length_ratio=0.3) for a, b in zip(steps, steps[1:])])
        recap = VGroup(last, steps, arrows)
        self.validator.check_in_frame(VGroup(crumb, recap))

        # SEE (silent): the trail.  HEAR: the four-step method from last time.
        n = self.narrate(
            id="intro_01",
            text="Last time, you learned the four-step method for any aptitude problem: read, model, solve, check.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.play(FadeIn(last), FadeIn(arrows))
        for step, spoken in zip(steps, ["read", "model", "solve", "check"]):
            self.at_word(n, spoken)
            self.play(FadeIn(step, scale=1.1), run_time=0.4)
        self.wait_for_narration(n)

        # HEAR: today, the method meets real money.  SEE: the title.
        title = fitted_text("Introduction to Interest", SAFE_W, 68, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=P_COL, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(DOWN * 0.3)
        n = self.narrate(
            id="intro_02",
            text="In this video, we put that method to work on real money, starting with the words every interest "
                 "problem is built on.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(recap, shift=UP * 0.3))
        self.at_word(n, "money")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========
    # Purpose: "2% per month" sounds tiny; plant the wrong guess (Rs 1,000).

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        phone = self.loan_phone().move_to(LEFT_ZONE + UP * 0.1)
        ask = fitted_text("Extra paid in one year?", ZONE_W - 0.4, BODY, INK, BOLD).move_to(RIGHT_ZONE + UP * 1.6)
        guess = pill("Most people:  about ₹1,000", FOCUS, size=LABEL).move_to(RIGHT_ZONE + UP * 0.3)
        why = text("2% of ₹50,000 = ₹1,000", BODY, MUTED).next_to(guess, DOWN, buff=0.45)
        hold = pill("Hold that guess", R_COL, size=LABEL).move_to(RIGHT_ZONE + DOWN * 2.0)
        self.validator.check_in_frame(VGroup(phone, ask, guess, why, hold))

        # HEAR: the ad.  SEE: the phone, the banner, the Rs 50,000 slider glows.
        n = self.narrate(
            id="hook_01",
            text="A loan app flashes an ad: instant cash, just two percent interest per month. You need fifty "
                 "thousand rupees, and two percent sounds like nothing.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(phone[:2]), FadeIn(phone[2][1:], shift=UP * 0.2))
        self.at_word(n, "instant")
        self.play(FadeIn(phone.banner, scale=1.1))
        self.at_word(n, "need")
        self.play(Indicate(phone.amount, color=P_COL, scale_factor=1.15), Flash(phone.knob, color=P_COL))
        self.at_word(n, "nothing")
        self.play(Indicate(phone.rate_line, color=R_COL, scale_factor=1.1))
        self.wait_for_narration(n)

        # SILENCE (pause_after): a short beat to make a guess.
        n = self.narrate(
            id="hook_02",
            text="So, roughly how much extra will you pay in a year? Take a guess before we go on.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.play(FadeIn(ask, shift=DOWN * 0.2))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        # HEAR: the usual guess and why it feels right.
        n = self.narrate(
            id="hook_03",
            text="Most people say around one thousand rupees, because two percent of fifty thousand is one thousand, "
                 "and it feels small enough to ignore.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "around")
        self.play(FadeIn(guess, scale=1.1))
        self.at_word(n, "because")
        self.play(FadeIn(why, shift=UP * 0.15))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_04",
            text="Hold that guess. By the end of this video, you'll know exactly what that ad is hiding, and you'll "
                 "be able to read any interest offer in about ten seconds.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(hold, shift=UP * 0.2))
        self.at_word(n, "hiding")
        self.play(Indicate(phone.rate_line, color=FOCUS, scale_factor=1.15))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_hook")

    # =========================================== 2. OBJECTIVES ==========

    def objectives(self):
        self.scene_start("S02_objectives", title="Objectives")

        board, rows, _ = self.objectives_card()
        board.move_to(UP * 0.2)
        self.validator.check_in_frame(board)

        # SEE: the checklist, one line at a time, on its spoken words.
        n = self.narrate(
            id="objectives_01",
            text="By the end of this video, you will be able to define principal, rate, time, interest and amount, "
                 "and connect them with A equals P plus I. You'll also be able to convert rates and time into "
                 "matching units before you calculate.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(board[1][0]))
        self.at_word(n, "define")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "convert")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ================================== 3. WHAT IS IT? WHY IMPORTANT? ==========

    def what_and_why(self):
        self.scene_start("S03_what_why", title="What is it? Why is it important?")

        title = text("Interest", 72, INK, BOLD).move_to(UP * 2.3)
        tiles = VGroup(*[term_tile(l, w, c) for l, w, c in TERMS]).arrange(RIGHT, buff=0.7).move_to(UP * 0.5)
        borrow = VGroup(pill("Borrow", P_COL, size=LABEL), text("→", LABEL, MUTED),
                        text("you pay it", BODY, INK)).arrange(RIGHT, buff=0.3)
        lend = VGroup(pill("Deposit or lend", A_COL, size=LABEL), text("→", LABEL, MUTED),
                      text("you earn it", BODY, INK)).arrange(RIGHT, buff=0.3)
        sides = VGroup(borrow, lend).arrange(RIGHT, buff=1.0).move_to(DOWN * 1.4)
        self.validator.check_in_frame(VGroup(title, tiles, sides))

        # HEAR: interest = price of using someone else's money.
        n = self.narrate(
            id="what_01",
            text="Interest is the price of using someone else's money. If you borrow, you pay it. If you deposit or "
                 "lend, you earn it.",
            voice="default",
            subtitle=True,
        )
        self.play(Write(title))
        self.at_word(n, "borrow")
        self.play(FadeIn(borrow, shift=UP * 0.2))
        self.at_word(n, "deposit")
        self.play(FadeIn(lend, shift=UP * 0.2))
        self.wait_for_narration(n)

        # HEAR: five words.  SEE: P R T I A, each on its word.
        n = self.narrate(
            id="what_02",
            text="Five words describe every interest problem: principal, rate, time, interest and amount.",
            voice="default",
            subtitle=True,
        )
        for tile_, (_, word, _) in zip(tiles, TERMS):
            self.at_word(n, word.lower(), occurrence=2 if word == "Interest" else 1)
            self.play(FadeIn(tile_, shift=UP * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        # HEAR: where it shows up.  SEE: usage chips replace the pay/earn row.
        uses = VGroup(*[pill(s, c, size=SMALL) for s, c in
                        [("Loans", P_COL), ("Fixed deposits", A_COL), ("EMIs", R_COL),
                         ("Credit cards", I_COL), ("Aptitude papers", FOCUS)]])
        uses.arrange(RIGHT, buff=0.3).move_to(DOWN * 1.4)
        fit_width(uses, SAFE_W)
        n = self.narrate(
            id="what_03",
            text="Why does it matter? Loans, fixed deposits, EMIs and credit cards all run on it, and it's one of the "
                 "most repeated topics in aptitude papers.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(sides, shift=DOWN * 0.2))
        for chip, spoken in zip(uses, ["Loans", "fixed", "EMIs", "credit", "aptitude"]):
            self.at_word(n, spoken)
            self.play(FadeIn(chip, shift=UP * 0.15), run_time=0.35)
        self.wait_for_narration(n)

        # HEAR: the single source of mistakes.  SEE: R and T flash; caption.
        n = self.narrate(
            id="what_04",
            text="And nearly every mistake in this lesson comes from a single place: mixing up the units of the rate "
                 "and the time. That's exactly the trap in our loan app.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "units")
        self.play(Indicate(tiles[1], color=R_COL, scale_factor=1.2), Indicate(tiles[2], color=T_COL, scale_factor=1.2))
        cap = self.caption("Most mistakes: mixing the units of rate and time", BAD)
        self.at_word(n, "trap")
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.validator.check_in_frame(VGroup(uses, cap))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_what_why")

    # ============================================== 4. THE ANALOGY ==========
    # Flat = principal, rent = interest, total paid over time = amount.

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        flat = house(2.3).move_to(LEFT * 4.3 + UP * 0.6)
        flat_tag = pill("Principal", P_COL, size=LABEL).next_to(flat, DOWN, buff=0.35)
        flat_note = text("the money you borrow", SMALL, MUTED).next_to(flat_tag, DOWN, buff=0.15)

        # Rent slips, one per month, stacking to the right of the flat.
        months = VGroup(*[VGroup(text(f"Month {k}", SMALL, MUTED), pill("rent", I_COL, size=SMALL))
                          .arrange(RIGHT, buff=0.3) for k in range(1, 5)])
        months.arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to(RIGHT * 0.4 + UP * 0.9)
        rent_tag = pill("Interest", I_COL, size=LABEL).next_to(months, RIGHT, buff=0.6)
        rate_tag = pill("₹ per ₹100, per period", R_COL, size=SMALL).next_to(months, UP, buff=0.35)
        total = VGroup(pill("Amount", A_COL, size=LABEL),
                       text("= flat's value + all the rent", BODY, A_COL)).arrange(RIGHT, buff=0.3)
        total.move_to(DOWN * 1.9)
        self.validator.check_in_frame(VGroup(flat, flat_note, months, rent_tag, rate_tag, total))

        n = self.narrate(
            id="analogy_01",
            text="Think of interest as rent, but for money instead of a flat. The money you borrow is the flat. The "
                 "rent you pay for using it is the interest.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "flat")
        self.play(FadeIn(flat, shift=UP * 0.2))
        self.at_word(n, "borrow")
        self.play(FadeIn(flat_tag, shift=UP * 0.15), FadeIn(flat_note))
        self.at_word(n, "using")
        self.play(FadeIn(months[0], shift=LEFT * 0.2))
        self.play(FadeIn(rent_tag, shift=LEFT * 0.2))
        self.wait_for_narration(n)

        # HEAR: quoted as a rate; the longer you stay, the more rent.  SEE: the
        # rate tag, then more months stack up and the total appears.
        n = self.narrate(
            id="analogy_02",
            text="The rent is quoted as a rate: so many rupees for every hundred rupees, for a fixed period. The "
                 "longer you stay, the more rent you pay.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rate")
        self.play(FadeIn(rate_tag, shift=DOWN * 0.15))
        self.at_word(n, "longer")
        self.play(LaggedStart(*[FadeIn(m, shift=LEFT * 0.2) for m in months[1:]], lag_ratio=0.4))
        self.at_word(n, "more")
        self.play(FadeIn(total, shift=UP * 0.2))
        self.wait_for_narration(n)

        # HEAR: per month or per year, never mixed.
        clash = VGroup(pill("per month", R_COL, size=LABEL), text("≠", 44, BAD, BOLD),
                       pill("per year", T_COL, size=LABEL)).arrange(RIGHT, buff=0.4)
        clash.move_to(total)
        n = self.narrate(
            id="analogy_03",
            text="And just as rent has to be quoted per month or per year, so does the rate, and you can't mix them up.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "quoted")
        self.play(FadeOut(total, shift=DOWN * 0.2), FadeIn(clash, shift=UP * 0.2))
        self.at_word(n, "mix")
        self.play(Indicate(clash[1], color=BAD, scale_factor=1.4))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5. DEFINITIONS, A = P + I ==========

    def definitions(self):
        self.scene_start("S05_definitions", title="Formula, Derived - The Five Terms")

        meanings = ["the money you start with", "the rent per ₹100", "how long",
                    "the total rent", "everything you end up paying or receiving"]
        rows = VGroup()
        for (letter, word, color), m in zip(TERMS, meanings):
            rows.add(VGroup(symbol_tile(letter, color, 0.7), text(word, BODY, color, BOLD),
                            fitted_text(m, 6.4, BODY, INK)).arrange(RIGHT, buff=0.35))
        rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT).move_to(UP * 0.7)
        # Put every meaning in one column, lined up after the longest word.
        col_x = max(r[1].get_right()[0] for r in rows) + 0.4
        for r in rows:
            r[2].move_to(RIGHT * col_x + UP * r[2].get_y(), aligned_edge=LEFT)
        rows.move_to(UP * 0.7)
        eq = math_line("A", "=", "P", "+", "I", colors={"A": A_COL, "P": P_COL, "I": I_COL}, size=64)
        eq_card = self.card(eq, color=A_COL, pad=0.3).move_to(DOWN * 2.45)
        self.validator.check_in_frame(VGroup(rows, eq_card))

        n = self.narrate(
            id="defs_01",
            text="Let's build the definitions. Principal, P, is the money you start with. Rate, R, is the rent per "
                 "hundred rupees. Time, T, is how long. Interest, I, is the total rent.",
            voice="default",
            subtitle=True,
        )
        for row, (_, word, _) in zip(rows[:4], TERMS[:4]):
            self.at_word(n, word)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        # HEAR: amount = everything, so A = P + I.  SEE: the last row, then
        # A, P and I fly from their tiles into the equation.
        n = self.narrate(
            id="defs_02",
            text="And Amount, A, is everything you end up paying or receiving, so A equals P plus I.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Amount")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2), run_time=0.5)
        self.at_word(n, "equals")
        self.play(FadeIn(eq_card[0]),
                  TransformFromCopy(rows[4][0][1], eq[0]), FadeIn(eq[1]),
                  TransformFromCopy(rows[0][0][1], eq[2]), FadeIn(eq[3]),
                  TransformFromCopy(rows[3][0][1], eq[4]), run_time=1.2)
        self.play(Circumscribe(eq_card, color=A_COL))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_definitions")

    # ========================================== 6. MATCHING UNITS ==========
    # A 2%-per-month bar stretches into 12 bars = 24% per year.

    def matching_units(self):
        self.scene_start("S06_units", title="Formula, Derived - Matching Units")

        bar_w, bar_h, gap = 0.5, 0.7, 0.06
        month_bars = VGroup(*[bar(bar_w, bar_h, R_COL) for _ in range(12)]).arrange(RIGHT, buff=gap)
        month_bars.move_to(UP * 1.0)
        twos = VGroup(*[text("₹2", SMALL, R_COL, BOLD).next_to(b, UP, buff=0.12) for b in month_bars])
        first_label = fitted_text("₹2 for every ₹100, every month", ZONE_W, BODY, R_COL, BOLD)
        first_label.next_to(month_bars[0], DOWN, buff=0.35, aligned_edge=LEFT)
        year_bar = bar(month_bars.width, bar_h, T_COL, 0.4).move_to(month_bars)
        year_label = fitted_text("₹24 for every ₹100, every year", SAFE_W, BODY, T_COL, BOLD)
        year_label.next_to(year_bar, DOWN, buff=0.35)
        brace = Brace(month_bars, UP, color=MUTED)
        brace_label = text("12 months", SMALL, MUTED).next_to(brace, UP, buff=0.1)
        equiv = text("2% per month  =  24% per year", 40, INK, BOLD,
                     t2c={"2% per month": R_COL, "24% per year": T_COL}).move_to(DOWN * 1.4)
        self.validator.check_in_frame(VGroup(brace_label, month_bars, twos, year_label, equiv))

        n = self.narrate(
            id="units_01",
            text="Now the most important skill: matching units. A rate of two percent per month means two rupees for "
                 "every hundred rupees, each month.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "matching")
        cap = self.caption("Match the units", FOCUS)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.at_word(n, "means")
        self.play(GrowFromEdge(month_bars[0], LEFT), FadeIn(twos[0]))
        self.play(FadeIn(first_label, shift=UP * 0.15))
        self.wait_for_narration(n)

        # HEAR: 12 months -> Rs 24 per Rs 100.  SEE: the bar repeats 12 times,
        # then merges into one yearly bar.
        n = self.narrate(
            id="units_02",
            text="Over twelve months, that's twenty-four rupees for every hundred rupees. So two percent per month "
                 "equals twenty-four percent per year.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(first_label))
        self.at_word(n, "Over")
        self.play(LaggedStart(*[AnimationGroup(TransformFromCopy(month_bars[0], b), FadeIn(t))
                                for b, t in zip(month_bars[1:], twos[1:])], lag_ratio=0.15), run_time=1.6)
        self.play(GrowFromCenter(brace), FadeIn(brace_label))
        self.at_word(n, "every")
        self.play(ReplacementTransform(month_bars, year_bar), FadeOut(twos), FadeIn(year_label, shift=UP * 0.15))
        self.at_word(n, "equals")
        self.play(Write(equiv))
        self.wait_for_narration(n)

        # HEAR: x12 for rates, /12 for months; 8 months = 8/12 year.  SEE: two
        # converter pills, then a year strip with 8 of 12 months filled.
        conv = VGroup(pill("monthly rate × 12  =  yearly rate", R_COL, size=LABEL),
                      pill("months ÷ 12  =  years", T_COL, size=LABEL)).arrange(RIGHT, buff=0.5)
        fit_width(conv, SAFE_W)
        conv.move_to(UP * 2.2)
        strip = year_strip(8).move_to(DOWN * 0.2)
        strip_brace = Brace(strip[:8], DOWN, color=T_COL)
        strip_label = text("8 months  =  8/12 of a year", BODY, T_COL, BOLD).next_to(strip_brace, DOWN, buff=0.15)
        year_tag = text("1 year = 12 months", SMALL, MUTED).next_to(strip, UP, buff=0.25)
        n = self.narrate(
            id="units_03",
            text="To convert a monthly rate to a yearly one, multiply by twelve. To convert months to years, divide "
                 "by twelve: eight months is eight twelfths of a year.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(year_bar, year_label, brace, brace_label)),
                  equiv.animate.scale(0.7).move_to(UP * 1.3))
        self.at_word(n, "multiply")
        self.play(FadeIn(conv[0], shift=DOWN * 0.15))
        self.at_word(n, "divide")
        self.play(FadeIn(conv[1], shift=DOWN * 0.15), FadeIn(year_tag), FadeIn(strip))
        self.at_word(n, "eight")
        self.play(GrowFromCenter(strip_brace), FadeIn(strip_label, shift=UP * 0.1))
        self.validator.check_in_frame(VGroup(conv, equiv, year_tag, strip, strip_label, cap))
        self.wait_for_narration(n)

        # HEAR: the rule.  SEE: the caption becomes the rule.
        rule = self.caption("Rate's period = time's period, before anything else", GOOD)
        n = self.narrate(
            id="units_04",
            text="The rule is simple: the rate's period and the time's period must be the same, before you do "
                 "anything else.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(ReplacementTransform(cap, rule))
        self.at_word(n, "same")
        self.play(Circumscribe(rule, color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_units")

    # ============================================ 7. FORMULA BOX ==========

    def formula_box_scene(self):
        self.scene_start("S07_formula_box", title="Formula Box")

        box = self.formula_box().move_to(ORIGIN)
        self.validator.check_in_frame(box)
        lines = box[1][1]

        n = self.narrate(
            id="box_01",
            text="Here's all of that in one box. A equals P plus I. A monthly rate times twelve is the yearly rate. "
                 "And months divided by twelve give years.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(box[0]), FadeIn(box[1][0]))
        for line, spoken in zip(lines, ["equals", "monthly", "months"]):
            self.at_word(n, spoken)
            self.play(FadeIn(line, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_formula_box")

    # ========================================== 8. WORKED EXAMPLE ==========
    # The hook returns: 24% per year over 500 hundreds = Rs 12,000.

    def worked_example(self):
        self.scene_start("S08_worked", title="Worked Example")

        question = self.question_card("Loan app: ₹50,000 at 2% per month.   Extra paid in one year?")
        grid = hundreds_grid().move_to(LEFT * 3.6 + DOWN * 0.75)
        grid_label = text("₹50,000  =  500 × ₹100", SMALL, P_COL, BOLD).next_to(grid, UP, buff=0.2)
        steps = VGroup(
            text("2% per month = 24% per year", BODY, INK, t2c={"2% per month": R_COL, "24% per year": T_COL}),
            text("= ₹24 for every ₹100", BODY, T_COL),
            text("500 × ₹24 = ₹12,000", 38, I_COL, BOLD),
            text("A = ₹50,000 + ₹12,000 = ₹62,000", BODY, A_COL, BOLD),
        ).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        steps.move_to(RIGHT * 2.9 + DOWN * 0.6)
        fit_width(steps, 7.0)
        self.validator.check_in_frame(VGroup(question, grid_label, grid, steps))

        n = self.narrate(
            id="worked_01",
            text="Back to the loan app. Two percent per month is twenty-four percent per year. That means "
                 "twenty-four rupees for every hundred rupees, each year.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(question, shift=DOWN * 0.3))
        self.at_word(n, "percent", occurrence=2)
        self.play(FadeIn(steps[0], shift=RIGHT * 0.2))
        self.at_word(n, "means")
        self.play(FadeIn(steps[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        # HEAR: 50,000 = 500 hundreds; 500 x 24 = 12,000.  SEE: the grid of
        # 500 hundreds fills row by row, then turns interest-pink.
        n = self.narrate(
            id="worked_02",
            text="You've borrowed fifty thousand rupees, which is five hundred hundreds. So the yearly cost is five "
                 "hundred times twenty-four rupees, which is twelve thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "borrowed")
        self.play(FadeIn(grid_label))
        self.at_word(n, "hundreds")
        rows = [grid[k * 25:(k + 1) * 25] for k in range(20)]
        self.play(LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.1), run_time=1.4)
        self.at_word(n, "times")
        self.play(grid.animate.set_fill(I_COL, 0.75), run_time=0.8)
        self.at_word(n, "twelve")
        self.play(FadeIn(steps[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        # HEAR: repay 62,000; not 1,000 extra.  SEE: A = P + I line, the old
        # guess struck out.
        old = pill("Your guess: ₹1,000", FOCUS, size=SMALL).next_to(steps[3], DOWN, buff=0.45, aligned_edge=LEFT)
        strike = Line(old.get_left(), old.get_right(), color=BAD, stroke_width=5)
        self.validator.check_in_frame(VGroup(steps, old))
        n = self.narrate(
            id="worked_03",
            text="You'd repay fifty thousand plus twelve thousand, which is sixty-two thousand rupees. Not one "
                 "thousand extra. Twelve thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "repay")
        self.play(FadeIn(steps[3], shift=RIGHT * 0.2))
        self.at_word(n, "Not")
        self.play(FadeIn(old))
        self.play(Create(strike))
        self.at_word(n, "extra")
        self.play(Indicate(steps[2], color=I_COL, scale_factor=1.12))
        self.wait_for_narration(n)

        n = self.narrate(
            id="worked_04",
            text="The ad wasn't lying. It was just quoting the rate in the smallest unit, so it sounds small.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "smallest")
        cap = self.caption("The ad quoted the rate in the smallest unit", R_COL)
        self.play(FadeOut(VGroup(old, strike)), FadeIn(cap, shift=UP * 0.2))
        self.validator.check_in_frame(VGroup(grid, steps, cap))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_worked")

    # ============================================= 9. COMMON TRAP ==========

    def common_trap(self):
        self.scene_start("S09_trap", title="Common Trap")

        card_w = SAFE_W - 1.0
        wrong = self.verdict_card(False, "2% of 50,000 = ₹1,000 for the year", card_w).move_to(UP * 1.9)
        right = self.verdict_card(True, "2% is per month:  ₹1,000 × 12 = ₹12,000", card_w).move_to(UP * 0.35)
        asks = VGroup(VGroup(pill("Rate", R_COL, size=LABEL), text("→  per what?", BODY, INK)).arrange(RIGHT, buff=0.3),
                      VGroup(pill("Time", T_COL, size=LABEL), text("→  in what unit?", BODY, INK)).arrange(RIGHT, buff=0.3))
        asks.arrange(RIGHT, buff=1.2).move_to(DOWN * 1.2)
        self.validator.check_in_frame(VGroup(wrong, right, asks))

        n = self.narrate(
            id="trap_01",
            text="The trap is the one in your head at the start of this video: using a monthly rate as though it were "
                 "yearly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "head")
        self.play(FadeIn(wrong, shift=RIGHT * 0.3))
        self.at_word(n, "yearly")
        self.play(Indicate(wrong, color=BAD, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap_02",
            text="The number looks the same, and only the period changes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "period")
        self.play(FadeIn(right, shift=RIGHT * 0.3))
        self.wait_for_narration(n)

        # HEAR: the two questions to ask.  SEE: rate -> per what?, time -> in
        # what unit?, then the convert-first caption.
        n = self.narrate(
            id="trap_03",
            text="Every time you see a rate, ask: per what? And every time you see a time, ask: in what unit? If they "
                 "don't match, convert before you calculate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "per")
        self.play(FadeIn(asks[0], shift=UP * 0.2))
        self.at_word(n, "unit")
        self.play(FadeIn(asks[1], shift=UP * 0.2))
        self.at_word(n, "convert")
        cap = self.caption("Don't match?  Convert first, then calculate", GOOD)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.validator.check_in_frame(VGroup(asks, cap))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_trap")

    # ======================================= 10. INTERACTIVE PAUSE ==========

    def interactive_pause(self):
        self.scene_start("S10_pause", title="Interactive Pause")

        question = self.question_card("Borrow ₹20,000 at 1.5% per month for 6 months.   Interest = ?")
        principal = text("₹20,000", 60, P_COL, BOLD).move_to(LEFT * 3.4 + UP * 0.3)
        units = VGroup(pill("rate: per month", R_COL, size=LABEL), pill("time: in months", T_COL, size=LABEL))
        units.arrange(RIGHT, buff=0.4).move_to(DOWN * 1.2)
        match = VGroup(verdict(True, 36), text("already match", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.2)
        match.next_to(units, DOWN, buff=0.35)
        work = VGroup(text("1.5% × 6 = 9%", 44, R_COL, BOLD),
                      text("9% of ₹20,000 = ₹1,800", 38, GOOD, BOLD)).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        work.move_to(RIGHT * 2.6 + UP * 0.3)
        self.validator.check_in_frame(VGroup(question, principal, work, units, match))

        # SILENCE (pause_after): the 10-second countdown from the script.
        n = self.narrate(
            id="pause_01",
            text="Your turn. You borrow twenty thousand rupees at one and a half percent per month for six months. "
                 "How much interest do you pay? Pause and match the units first.",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(question, shift=DOWN * 0.3))
        self.at_word(n, "borrow")
        self.play(FadeIn(principal, shift=UP * 0.2))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="pause_02",
            text="The rate is per month and the time is in months, so they already match. One and a half percent times "
                 "six months is nine percent of twenty thousand rupees, which is one thousand eight hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rate")
        self.play(FadeIn(units[0], shift=UP * 0.15))
        self.at_word(n, "time")
        self.play(FadeIn(units[1], shift=UP * 0.15))
        self.at_word(n, "match")
        self.play(FadeIn(match, scale=1.1))
        self.at_word(n, "nine")
        self.play(FadeIn(work[0], shift=RIGHT * 0.2))
        self.at_word(n, "eight")
        self.play(FadeIn(work[1], shift=RIGHT * 0.2))
        self.play(Circumscribe(work[1], color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_pause")

    # ================================================ 11. PRACTICE ==========

    def practice(self):
        self.scene_start("S11_practice", title="Practice Questions")

        qs = [
            "P = ₹2,000 and I = ₹300. Find the amount A.",
            "A shop charges 3% per month. What is the equivalent yearly rate?",
            "Find the interest on ₹8,000 at 12% per year for 9 months.",
            "A = ₹7,500 and P = ₹6,000. Find the interest, and what fraction of P it is.",
        ]
        rows = VGroup(*[VGroup(pill(f"Q{k + 1}", FOCUS), fitted_text(q, SAFE_W - 2.6, BODY, INK, max_lines=2))
                        .arrange(RIGHT, buff=0.35) for k, q in enumerate(qs)])
        rows.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        heading = text("Try each one with READ → MODEL → SOLVE → CHECK", LABEL, MUTED, BOLD)
        board = self.card(VGroup(heading, rows).arrange(DOWN, buff=0.45, aligned_edge=LEFT), color=FOCUS)
        board.move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Now four for you. Try each one with the four steps before you look at the key.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(heading), FadeIn(rows, shift=UP * 0.2))
        self.play(rows.animate.set_opacity(0.45))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_q1",
            text="One. P is two thousand rupees and I is three hundred. Find the amount.",
            voice="default",
            subtitle=True,
        )
        self.play(rows[0].animate.set_opacity(1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_q2",
            text="Two. A shop charges three percent per month. What is the equivalent yearly rate?",
            voice="default",
            subtitle=True,
        )
        self.play(rows[1].animate.set_opacity(1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_q3",
            text="Three. Find the interest on eight thousand rupees at twelve percent per year for nine months.",
            voice="default",
            subtitle=True,
        )
        self.play(rows[2].animate.set_opacity(1))
        self.wait_for_narration(n)

        # SILENCE (pause_after): countdown ring while the learner works.
        n = self.narrate(
            id="practice_q4",
            text="Four. A is seven thousand five hundred and P is six thousand. Find the interest, and then find what "
                 "fraction of P it is.",
            voice="default",
            subtitle=True,
            pause_after=15.0,
        )
        self.play(rows[3].animate.set_opacity(1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S11_practice")

    # ================================================== 12. ANSWER ==========
    # Answer key, with reasoning: one card per question in a 2 x 2 grid.

    def answer(self):
        self.scene_start("S12_answer", title="Answer Key")

        card_w = ZONE_W - 0.3
        specs = [
            ["A = 2,000 + 300", "A = ₹2,300"],
            ["3% × 12", "= 36% per year"],
            ["9 months = 9/12 = 0.75 year", "₹960 × 0.75 = ₹720"],
            ["I = 7,500 − 6,000 = ₹1,500", "1,500 / 6,000 = 1/4 = 25%"],
        ]
        cards = []
        for k, lines in enumerate(specs):
            body = VGroup(pill(f"Q{k + 1}", FOCUS, size=SMALL),
                          *[fitted_text(s, card_w - 0.8, BODY, GOOD if j == len(lines) - 1 else INK, BOLD)
                            for j, s in enumerate(lines)]).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
            cards.append(self.card(body, width=card_w, height=2.3, color=GOOD))
        for c, zone, y in zip(cards, [LEFT_ZONE, RIGHT_ZONE, LEFT_ZONE, RIGHT_ZONE], [1.4, 1.4, -1.25, -1.25]):
            c.move_to(zone + UP * y)
        self.validator.check_in_frame(VGroup(*cards))

        def reveal(card, n, words):
            """Card frame and tag first, then each line on its spoken word."""
            box, body = card
            self.play(FadeIn(box), FadeIn(body[0]), run_time=0.4)
            for line, w in zip(body[1:], words):
                self.at_word(n, w)
                self.play(FadeIn(line, shift=RIGHT * 0.15), run_time=0.4)

        n = self.narrate(
            id="answer_01",
            text="One. A equals P plus I, so two thousand plus three hundred is two thousand three hundred rupees.",
            voice="default",
            subtitle=True,
        )
        reveal(cards[0], n, ["equals", "is"])
        self.wait_for_narration(n)

        n = self.narrate(
            id="answer_02",
            text="Two. Three percent times twelve is thirty-six percent per year.",
            voice="default",
            subtitle=True,
        )
        reveal(cards[1], n, ["Three", "per"])
        self.wait_for_narration(n)

        n = self.narrate(
            id="answer_03",
            text="Three. Nine months is nine twelfths, or zero point seven five of a year. Twelve percent of eight "
                 "thousand for a full year is nine hundred and sixty rupees, so for zero point seven five of a year "
                 "it's seven hundred and twenty rupees.",
            voice="default",
            subtitle=True,
        )
        reveal(cards[2], n, ["Nine", "full"])
        self.wait_for_narration(n)

        n = self.narrate(
            id="answer_04",
            text="Four. I equals A minus P: seven thousand five hundred minus six thousand is one thousand five "
                 "hundred rupees. As a fraction of P, fifteen hundred over six thousand is one quarter, or twenty-five "
                 "percent.",
            voice="default",
            subtitle=True,
        )
        reveal(cards[3], n, ["minus", "fraction"])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_answer")

    # ========================================== 13. QUICK REVISION ==========
    # Objectives tick off; the rent picture and the Formula Box return.

    def quick_revision(self):
        self.scene_start("S13_revision", title="Quick Revision + Summary")

        board, rows, boxes = self.objectives_card()
        board.move_to(UP * 0.3)
        ticks = VGroup(*[text("✓", 34, GOOD, BOLD).move_to(b) for b in boxes])
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="revision_01",
            text="In this video you learned the five words of interest, that A equals P plus I, and how to match the "
                 "units of rate and time.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board))
        self.at_word(n, "equals")
        self.play(boxes[0].animate.set_stroke(GOOD), FadeIn(ticks[0], scale=1.4))
        self.at_word(n, "match")
        self.play(boxes[1].animate.set_stroke(GOOD), FadeIn(ticks[1], scale=1.4))
        self.wait_for_narration(n)

        # HEAR: the rent picture.  SEE: the flat returns with its three labels.
        flat = house(2.0).move_to(LEFT * 3.2 + UP * 0.6)
        flat_tag = pill("Principal", P_COL, size=SMALL).next_to(flat, DOWN, buff=0.3)
        rent = VGroup(pill("rent = Interest", I_COL, size=LABEL), pill("quoted per period", R_COL, size=LABEL),
                      pill("total paid = Amount", A_COL, size=LABEL)).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        rent.move_to(RIGHT * 2.4 + UP * 0.4)
        self.validator.check_in_frame(VGroup(flat, flat_tag, rent))
        n = self.narrate(
            id="revision_02",
            text="The rent picture gave you the idea: interest is rent for money, and it's always quoted per period.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(board, ticks)))
        self.play(FadeIn(flat, shift=UP * 0.2), FadeIn(flat_tag))
        self.at_word(n, "interest")
        self.play(FadeIn(rent[0], shift=LEFT * 0.2))
        self.at_word(n, "quoted")
        self.play(FadeIn(rent[1], shift=LEFT * 0.2), FadeIn(rent[2], shift=LEFT * 0.2))
        self.wait_for_narration(n)

        # HEAR: the trap, once more.  SEE: the Formula Box returns with the
        # "per what?" reminder.
        box = self.formula_box().move_to(UP * 0.5)
        ask = pill("Rate?  Ask: per what?", FOCUS, size=LABEL).next_to(box, DOWN, buff=0.4)
        self.validator.check_in_frame(VGroup(box, ask))
        n = self.narrate(
            id="revision_03",
            text="Remember the trap: a monthly rate is not a yearly rate. Ask per what, every time.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(flat, flat_tag, rent)))
        self.play(FadeIn(box, shift=UP * 0.2))
        self.at_word(n, "Ask")
        self.play(FadeIn(ask, scale=1.1))
        self.play(Indicate(box[1][1][1], color=R_COL, scale_factor=1.06))
        self.wait_for_narration(n)

        # Next video.
        nxt = pill("Next:  Simple Interest", GOOD, size=BODY).move_to(UP * BOTTOM_Y)
        self.validator.check_in_frame(VGroup(box, ask, nxt))
        n = self.narrate(
            id="closing_01",
            text="Next: Simple Interest.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(nxt, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S13_revision")
