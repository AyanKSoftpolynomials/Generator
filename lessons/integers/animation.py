"""
Integers — LMS Educational Video
Visual Direction:
- 3Blue1Brown-inspired mathematical storytelling
- Number line is the central visual system
- Negative numbers emerge as reflections of positive numbers
- Cinematic dark background with cyan / yellow / red semantic colors
- 3D/depth used selectively for important conceptual moments

Authoring source of truth:
    animation.py

The LMS video generator extracts narration metadata automatically.
"""

from manim import *
# FIX: the framework lives in src.animation. LMSMovingCameraScene (not
# LMSScene) because the ending zooms with self.camera.frame.
from src.animation import LMSMovingCameraScene


# ============================================================
# THEME
# ============================================================

BG = "#090D16"

WHITE = "#F5F7FA"
MUTED = "#7E8797"

ZERO = "#FFD166"
POSITIVE = "#38BDF8"
NEGATIVE = "#FF6B6B"

GREEN = "#5BE7A9"
PURPLE = "#A78BFA"
ORANGE = "#FF9F43"

GRID = "#263044"

# FIX: "teacher" is not in assets/voices; use the registered teacher voice.
TEACHER = "teacher_a"


# ============================================================
# HELPERS
# ============================================================

def glow_dot(point, color, radius=0.09):
    """
    Small conceptual point with a subtle halo.
    """
    halo = Circle(
        radius=radius * 2.2,
        stroke_width=0,
        fill_color=color,
        fill_opacity=0.10,
    ).move_to(point)

    dot = Dot(
        point,
        radius=radius,
        color=color,
    )

    return VGroup(halo, dot)


def number_label(
    number,
    point,
    color=WHITE,
    scale=0.45,
):
    return MathTex(
        str(number),
        color=color,
    ).scale(scale).next_to(point, DOWN, buff=0.18)


def create_number_line(
    start=-5,
    end=5,
    unit=0.9,
    y=0,
):
    line = NumberLine(
        x_range=[start, end, 1],
        length=(end - start) * unit,
        include_numbers=False,
        include_tip=True,
        color=WHITE,
        stroke_width=3,
    ).move_to([0, y, 0])

    return line


# ============================================================
# VIDEO
# ============================================================

class IntegersVideo(LMSMovingCameraScene):

    lesson_title = "Integers"

    def construct(self):

        self.camera.background_color = BG

        # ----------------------------------------------------
        # HOOK
        # ----------------------------------------------------

        self.scene_start(
            "hook",
            title="Opening Question",
        )

        n = self.narrate(
            id="hook_main",
            text=(
                "Hello again, my dear students! "
                "How would you write five degrees below zero as a single number? "
                "You'd write minus 5, wouldn't you? "
                "But our whole numbers from last time don't allow that at all — "
                "they stop right at zero. "
                "Let's open the door below zero today."
            ),
            voice=TEACHER,
            subtitle=True,
        )

        # Temperature indicator
        thermometer = VGroup(
            Line(UP * 1.8, DOWN * 1.8, color=WHITE, stroke_width=5),
            Circle(
                radius=0.28,
                color=NEGATIVE,
                fill_color=NEGATIVE,
                fill_opacity=1,
            ).shift(DOWN * 1.8),
        )

        thermometer.scale(0.8)
        thermometer.to_edge(LEFT, buff=1.3)

        temp = MathTex(
            r"-5^\circ",
            color=NEGATIVE,
        ).scale(1.1)

        temp.next_to(thermometer, RIGHT, buff=0.5)

        # FIX (timing): each visual now lands on the words that describe it
        # (at_word uses WhisperX timings) instead of all appearing in the first
        # seconds of this 15 s narration and the rest after it has ended.
        self.play(
            Create(thermometer),
            run_time=1.2,
        )

        question = Text(
            "Five degrees below zero",
            color=WHITE,
            weight=BOLD,
        ).scale(0.65)

        question.to_edge(UP, buff=0.8)

        self.at_word(n, "five degrees")

        self.play(
            Write(question),
            run_time=0.8,
        )

        self.at_word(n, "minus")

        self.play(
            FadeIn(temp, shift=RIGHT * 0.3),
            run_time=0.5,
        )

        # Move temperature toward a mathematical representation
        self.play(
            thermometer.animate.scale(0.75).shift(LEFT * 0.5),
            temp.animate.scale(1.3).set_color(NEGATIVE),
            run_time=0.8,
        )

        # Whole numbers limitation
        whole_numbers = MathTex(
            r"0,\ 1,\ 2,\ 3,\ 4,\ 5,\ \ldots",
            color=WHITE,
        ).scale(0.75)

        whole_numbers.to_edge(DOWN, buff=1.0)

        zero_marker = SurroundingRectangle(
            MathTex("0").scale(0.8),
            color=ZERO,
            buff=0.12,
        )

        self.at_word(n, "whole numbers")

        self.play(
            Write(whole_numbers),
            run_time=1,
        )

        barrier = Line(
            LEFT * 2.8,
            RIGHT * 2.8,
            color=NEGATIVE,
            stroke_width=6,
        ).rotate(PI / 2)

        barrier.move_to(LEFT * 1.8)

        self.at_word(n, "stop right")

        self.play(
            Create(barrier),
            run_time=0.5,
        )

        self.play(
            Flash(barrier.get_center(), color=NEGATIVE),
        )

        self.wait_for_narration(n)

        self.scene_end("hook")

        # ----------------------------------------------------
        # INTRO
        # ----------------------------------------------------

        self.scene_start(
            "introduction",
            title="Meet Integers",
        )

        self.narrate(
            id="intro_main",
            text=(
                "Welcome back! Today we meet Integers — "
                "whole numbers, now joined by their negative reflections."
            ),
            voice=TEACHER,
            subtitle=True,
        )

        # FIX: clear the hook visuals (thermometer, barrier, ...) like the
        # other sections do; otherwise they overlap the new number rows.
        self.clear()

        # Central zero
        zero = MathTex("0", color=ZERO).scale(1.5)

        self.play(
            FadeIn(zero, scale=0.5),
            run_time=0.8,
        )

        # Positive side
        positive = VGroup(
            MathTex("1", color=POSITIVE),
            MathTex("2", color=POSITIVE),
            MathTex("3", color=POSITIVE),
        ).arrange(RIGHT, buff=0.7)

        positive.scale(1.1)
        positive.next_to(zero, RIGHT, buff=0.7)

        # Negative side
        negative = VGroup(
            MathTex("-1", color=NEGATIVE),
            MathTex("-2", color=NEGATIVE),
            MathTex("-3", color=NEGATIVE),
        ).arrange(LEFT, buff=0.7)

        negative.scale(1.1)
        negative.next_to(zero, LEFT, buff=0.7)

        self.play(
            LaggedStart(
                *[FadeIn(x, shift=RIGHT * 0.3) for x in positive],
                lag_ratio=0.15,
            ),
            run_time=1.0,
        )

        # Negative reflection
        self.play(
            LaggedStart(
                *[FadeIn(x, shift=LEFT * 0.3) for x in negative],
                lag_ratio=0.15,
            ),
            run_time=1.0,
        )

        reflection = DashedLine(
            LEFT * 0.1,
            RIGHT * 0.1,
            color=MUTED,
        ).rotate(PI / 2)

        reflection.scale(3)
        reflection.move_to(zero)

        self.play(
            Create(reflection),
        )

        label = Text(
            "negative reflections",
            color=NEGATIVE,
        ).scale(0.42)

        label.next_to(negative, UP, buff=0.4)

        self.play(
            FadeIn(label, shift=DOWN * 0.2),
        )

        self.wait_for_narration("intro_main")

        self.scene_end("introduction")

        # ----------------------------------------------------
        # HOW
        # ----------------------------------------------------

        self.scene_start(
            "how",
            title="How Integers Work",
        )

        self.narrate(
            id="how_main",
            text=(
                "So how do integers work? "
                "My dear students, picture a number line stretching in both directions from zero — "
                "positive whole numbers marching to the right, "
                "and their exact negative mirror images marching to the left."
            ),
            voice=TEACHER,
            subtitle=True,
        )

        self.clear()

        # Main number line
        line = create_number_line(-5, 5, unit=0.85)

        self.play(
            Create(line),
            run_time=1,
        )

        # Positive numbers
        positive_group = VGroup()

        for i in range(1, 6):
            p = line.n2p(i)
            positive_group.add(
                glow_dot(p, POSITIVE),
                number_label(i, p, POSITIVE),
            )

        self.play(
            LaggedStart(
                *[FadeIn(obj, shift=UP * 0.15)
                  for obj in positive_group],
                lag_ratio=0.05,
            ),
            run_time=1.2,
        )

        # Zero
        z = line.n2p(0)

        zero_group = VGroup(
            glow_dot(z, ZERO, radius=0.12),
            number_label(0, z, ZERO),
        )

        self.play(
            FadeIn(zero_group),
        )

        # Reflection arrows
        for i in range(1, 6):

            positive_point = line.n2p(i)
            negative_point = line.n2p(-i)

            # FIX: +PI/2 arcs ABOVE the line; -PI/2 arced below it, through
            # the POSITIVE / NEGATIVE labels.
            arrow = CurvedArrow(
                positive_point + UP * 0.15,
                negative_point + UP * 0.15,
                angle=PI / 2,
                color=NEGATIVE,
                stroke_width=2.5,
            )

            negative_dot = glow_dot(
                negative_point,
                NEGATIVE,
            )

            negative_label = number_label(
                -i,
                negative_point,
                NEGATIVE,
            )

            self.play(
                Create(arrow),
                FadeIn(negative_dot),
                Write(negative_label),
                run_time=0.35,
            )

        # Labels
        right_label = Text(
            "POSITIVE",
            color=POSITIVE,
            weight=BOLD,
        ).scale(0.42)

        right_label.next_to(line.n2p(3), DOWN, buff=0.65)

        left_label = Text(
            "NEGATIVE",
            color=NEGATIVE,
            weight=BOLD,
        ).scale(0.42)

        left_label.next_to(line.n2p(-3), DOWN, buff=0.65)

        self.play(
            FadeIn(right_label),
            FadeIn(left_label),
        )

        # Zero center emphasis
        self.play(
            Flash(
                line.n2p(0),
                color=ZERO,
                line_length=0.4,
            ),
        )

        self.wait_for_narration("how_main")

        self.scene_end("how")

        # ----------------------------------------------------
        # WHAT
        # ----------------------------------------------------

        self.scene_start(
            "what",
            title="What Are Integers?",
        )

        self.narrate(
            id="what_main",
            text=(
                "Integers include …, minus 3, minus 2, minus 1, 0, 1, 2, 3, … — "
                "stretching endlessly in both directions. "
                "Still no fractions or decimals here — only whole steps, positive or negative."
            ),
            voice=TEACHER,
            subtitle=True,
        )

        self.clear()

        # Infinite-looking number line
        line = create_number_line(-4, 4, unit=1)

        self.play(
            Create(line),
            run_time=1,
        )

        numbers = VGroup()

        for i in range(-4, 5):

            if i < 0:
                color = NEGATIVE
            elif i == 0:
                color = ZERO
            else:
                color = POSITIVE

            point = line.n2p(i)

            numbers.add(
                glow_dot(point, color),
                number_label(i, point, color),
            )

        self.play(
            LaggedStart(
                *[FadeIn(obj) for obj in numbers],
                lag_ratio=0.04,
            ),
            run_time=1.3,
        )

        # Infinity indicators
        left_inf = MathTex(
            r"\cdots",
            color=NEGATIVE,
        ).scale(1.2)

        right_inf = MathTex(
            r"\cdots",
            color=POSITIVE,
        ).scale(1.2)

        left_inf.next_to(line, LEFT, buff=0.25)
        right_inf.next_to(line, RIGHT, buff=0.25)

        self.play(
            Write(left_inf),
            Write(right_inf),
        )

        # Fractions / decimals
        fraction = MathTex(
            r"\frac{1}{2}",
            color=MUTED,
        ).scale(0.9)

        decimal = MathTex(
            r"2.5",
            color=MUTED,
        ).scale(0.9)

        fraction.move_to(line.n2p(1.5) + UP * 1.1)
        decimal.move_to(line.n2p(-2.5) + DOWN * 1.1)

        self.play(
            FadeIn(fraction),
            FadeIn(decimal),
        )

        cross1 = Cross(fraction, stroke_color=NEGATIVE, stroke_width=4)
        cross2 = Cross(decimal, stroke_color=NEGATIVE, stroke_width=4)

        self.play(
            Create(cross1),
            Create(cross2),
        )

        integer_label = Text(
            "WHOLE STEPS",
            color=GREEN,
            weight=BOLD,
        ).scale(0.48)

        integer_label.to_edge(UP, buff=0.6)

        self.play(
            FadeIn(integer_label, shift=DOWN * 0.2),
        )

        self.wait_for_narration("what_main")

        self.scene_end("what")

        # ----------------------------------------------------
        # WHY
        # ----------------------------------------------------

        self.scene_start(
            "why",
            title="Why Do We Need Integers?",
        )

        self.narrate(
            id="why_main",
            text=(
                "Now, why does this matter? "
                "Because integers let us describe real situations that whole numbers simply can't — "
                "temperatures below freezing, debts owed, floors below ground level in a building."
            ),
            voice=TEACHER,
            subtitle=True,
        )

        self.clear()

        # Central number line
        line = create_number_line(-5, 5, unit=0.8)

        self.play(
            Create(line),
            run_time=0.8,
        )

        # Temperature
        temp_icon = Text(
            "−5°C",
            color=NEGATIVE,
            weight=BOLD,
        ).scale(0.8)

        # FIX: spread the three labels out (they overlapped at -3 / -2).
        temp_icon.move_to(line.n2p(-4) + UP * 1.2)

        temp_arrow = Arrow(
            temp_icon.get_bottom(),
            line.n2p(-4) + UP * 0.1,
            color=NEGATIVE,
            buff=0.1,
        )

        # Debt
        # FIX: LaTeX cannot typeset ₹, so the amount is Text, not MathTex.
        debt = Text(
            "−₹2000",
            color=NEGATIVE,
            weight=BOLD,
        ).scale(0.6)

        debt.move_to(line.n2p(-2.5) + DOWN * 1.1)

        debt_arrow = Arrow(
            debt.get_top(),
            line.n2p(-2.5) + DOWN * 0.1,
            color=NEGATIVE,
            buff=0.1,
        )

        # Basement
        basement = Text(
            "Floor −2",
            color=PURPLE,
            weight=BOLD,
        ).scale(0.65)

        basement.move_to(line.n2p(-1.5) + UP * 1.2)

        basement_arrow = Arrow(
            basement.get_bottom(),
            line.n2p(-1.5) + UP * 0.1,
            color=PURPLE,
            buff=0.1,
        )

        self.play(
            FadeIn(temp_icon),
            Create(temp_arrow),
            run_time=0.7,
        )

        self.play(
            FadeIn(debt),
            Create(debt_arrow),
            run_time=0.7,
        )

        self.play(
            FadeIn(basement),
            Create(basement_arrow),
            run_time=0.7,
        )

        # Emphasize below-zero region
        shade = Polygon(
            line.n2p(-5) + DOWN * 0.4,
            line.n2p(0) + DOWN * 0.4,
            line.n2p(0) + UP * 0.4,
            line.n2p(-5) + UP * 0.4,
            stroke_width=0,
            fill_color=NEGATIVE,
            fill_opacity=0.08,
        )

        self.play(
            FadeIn(shade),
        )

        below_zero = Text(
            "BELOW ZERO",
            color=NEGATIVE,
            weight=BOLD,
        ).scale(0.5)

        below_zero.move_to(line.n2p(-2.5) + DOWN * 1.9)

        self.play(
            FadeIn(below_zero),
        )

        self.wait_for_narration("why_main")

        self.scene_end("why")

        # ----------------------------------------------------
        # REAL WORLD EXAMPLE
        # ----------------------------------------------------

        self.scene_start(
            "real_world_example",
            title="Real-World Example",
        )

        self.narrate(
            id="example_main",
            text=(
                "Let me tell you about a girl named Devika, "
                "helping her father record their small shop's accounts. "
                "One month showed a loss, and she wrote it down as minus 2,000 rupees."
            ),
            voice=TEACHER,
            subtitle=True,
        )

        self.clear()

        # Shop visual
        shop = VGroup(
            Rectangle(
                width=4.5,
                height=2.5,
                color=WHITE,
                stroke_width=3,
            ),
            Polygon(
                LEFT * 2.5 + UP * 1.25,
                RIGHT * 2.5 + UP * 1.25,
                RIGHT * 2.0 + UP * 2.0,
                LEFT * 2.0 + UP * 2.0,
                color=ORANGE,
                fill_opacity=0.2,
            ),
        )

        shop.move_to(LEFT * 3)

        shop_label = Text(
            "DEVIKA'S SHOP",
            color=WHITE,
            weight=BOLD,
        ).scale(0.42)

        shop_label.next_to(shop, DOWN, buff=0.25)

        self.play(
            Create(shop),
            FadeIn(shop_label),
            run_time=1,
        )

        # Account sheet
        sheet = RoundedRectangle(
            width=4.2,
            height=3.5,
            corner_radius=0.15,
            color=WHITE,
        ).move_to(RIGHT * 2.5)

        account_title = Text(
            "MONTHLY ACCOUNT",
            color=WHITE,
            weight=BOLD,
        ).scale(0.38)

        account_title.move_to(sheet.get_top() + DOWN * 0.5)

        self.play(
            Create(sheet),
            Write(account_title),
        )

        # FIX: Text instead of MathTex (₹ is not supported by LaTeX).
        profit = Text(
            "Profit: ₹1500",
            color=GREEN,
        ).scale(0.5)

        loss = Text(
            "Loss: −₹2000",
            color=NEGATIVE,
            weight=BOLD,
        ).scale(0.6)

        profit.next_to(account_title, DOWN, buff=0.5)
        loss.next_to(profit, DOWN, buff=0.5)

        self.play(
            Write(profit),
            Write(loss),
            run_time=1,
        )

        # Highlight -2000
        highlight = SurroundingRectangle(
            loss,
            color=NEGATIVE,
            buff=0.15,
        )

        self.play(
            Create(highlight),
            Flash(loss, color=NEGATIVE),
        )

        self.wait_for_narration("example_main")

        self.narrate(
            id="example_conclusion",
            text=(
                "Without integers, there would be no honest way to write that loss down at all — "
                "only integers can capture a value truly below zero."
            ),
            voice=TEACHER,
            subtitle=True,
        )

        # Transform accounting number into number-line position
        self.play(
            FadeOut(shop),
            FadeOut(shop_label),
            FadeOut(profit),
            FadeOut(account_title),
            FadeOut(sheet),
            FadeOut(highlight),
            run_time=0.8,
        )

        loss_target = MathTex(
            r"-2000",
            color=NEGATIVE,
        ).scale(1.2)

        # FIX: TransformMatchingShapes works with Text; the loss line itself
        # morphs into -2000 (a copy would leave the original on screen).
        self.play(
            TransformMatchingShapes(
                loss,
                loss_target,
            ),
            run_time=0.8,
        )

        self.wait_for_narration("example_conclusion")

        self.scene_end("real_world_example")

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        self.scene_start(
            "summary",
            title="Summary",
        )

        self.narrate(
            id="summary_main",
            text=(
                "So here's what we take away today. "
                "Integers are whole numbers plus their negative mirror images — "
                "stretching endlessly in both directions from zero, with no fractions involved."
            ),
            voice=TEACHER,
            subtitle=True,
        )

        self.clear()

        # Build concept from center outward
        center = MathTex("0", color=ZERO).scale(1.6)

        self.play(
            FadeIn(center, scale=0.5),
        )

        positive = VGroup()

        for i in range(1, 4):
            positive.add(
                MathTex(str(i), color=POSITIVE).scale(0.9)
            )

        positive.arrange(RIGHT, buff=0.65)
        positive.next_to(center, RIGHT, buff=0.7)

        negative = VGroup()

        for i in range(1, 4):
            negative.add(
                MathTex(f"-{i}", color=NEGATIVE).scale(0.9)
            )

        negative.arrange(LEFT, buff=0.65)
        negative.next_to(center, LEFT, buff=0.7)

        self.play(
            LaggedStart(
                *[FadeIn(x, shift=RIGHT * 0.2) for x in positive],
                lag_ratio=0.15,
            ),
            LaggedStart(
                *[FadeIn(x, shift=LEFT * 0.2) for x in negative],
                lag_ratio=0.15,
            ),
            run_time=1.2,
        )

        # Infinite arrows
        left_arrow = Arrow(
            LEFT * 5,
            LEFT * 3.8,
            color=NEGATIVE,
            buff=0,
        )

        right_arrow = Arrow(
            RIGHT * 3.8,
            RIGHT * 5,
            color=POSITIVE,
            buff=0,
        )

        # FIX: further out so the arrows don't touch -3 and 3.
        left_arrow.move_to(LEFT * 4.7)
        right_arrow.move_to(RIGHT * 4.7)

        self.play(
            GrowArrow(left_arrow),
            GrowArrow(right_arrow),
        )

        # Concept statement
        statement = MathTex(
            r"\text{Integers} = \text{Whole Numbers} + \text{Negative Reflections}",
            color=WHITE,
        ).scale(0.6)

        statement.to_edge(DOWN, buff=0.8)

        self.play(
            Write(statement),
            run_time=1,
        )

        self.wait_for_narration("summary_main")

        self.scene_end("summary")

        # ----------------------------------------------------
        # DONE / TRANSITION TO RATIONAL NUMBERS
        # ----------------------------------------------------

        self.scene_start(
            "done",
            title="Next: Rational Numbers",
        )

        self.narrate(
            id="done_main",
            text=(
                "That's Integers for you — whole steps, in both directions. "
                "In our next video, we welcome fractions and decimals into the family — "
                "Rational Numbers. See you there."
            ),
            voice=TEACHER,
            subtitle=True,
        )

        self.clear()

        # Final number line
        line = create_number_line(-5, 5, unit=0.75)

        self.play(
            Create(line),
            run_time=0.8,
        )

        # Integer points
        for i in range(-5, 6):

            if i < 0:
                color = NEGATIVE
            elif i == 0:
                color = ZERO
            else:
                color = POSITIVE

            point = line.n2p(i)

            self.add(
                glow_dot(point, color),
                number_label(i, point, color),
            )

        self.wait(0.5)

        # Fractional values appear between integers
        fractions = VGroup()

        for value, label in [
            (-2.5, "-2.5"),
            (-1.5, "-1.5"),
            (0.5, "1/2"),
            (1.5, "1.5"),
        ]:

            p = line.n2p(value)

            dot = Dot(
                p,
                radius=0.08,
                color=PURPLE,
            )

            txt = MathTex(
                label,
                color=PURPLE,
            ).scale(0.45)

            txt.next_to(dot, UP, buff=0.15)

            fractions.add(dot, txt)

        self.play(
            LaggedStart(
                *[FadeIn(x, scale=0.5) for x in fractions],
                lag_ratio=0.08,
            ),
            run_time=1.2,
        )

        # Reveal next concept
        next_title = Text(
            "RATIONAL NUMBERS",
            color=PURPLE,
            weight=BOLD,
        ).scale(0.65)

        next_title.to_edge(UP, buff=0.7)

        self.play(
            FadeIn(next_title, shift=DOWN * 0.3),
        )

        # Zoom toward a fraction
        fraction_focus = fractions[3]

        self.play(
            self.camera.frame.animate.scale(0.75).move_to(
                fraction_focus.get_center()
            ),
            run_time=1.2,
        )

        self.wait_for_narration("done_main")

        self.scene_end("done")


# ============================================================
# END
# ============================================================
