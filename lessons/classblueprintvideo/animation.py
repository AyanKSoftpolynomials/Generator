"""
Class as a Blueprint — C-CAT | Section A | Module 2: OOP (C++)
Day 23 | Subtopic A: Class Definition

Manim-only lesson animation.

Teaching flow from the supplied source:
HOOK -> INTRO -> HOW -> WHAT / WHY -> REAL-WORLD EXAMPLE
-> SUMMARY -> DONE

Authoring contract:
- animation.py is the source of truth.
- self.narrate() registers narration/voice/subtitle metadata.
- The existing LMS generator supplies TTS, actual audio timing,
  WhisperX alignment, subtitle generation, caching and FFmpeg.
- No Blender.
- No manual JSON.
"""

from manim import *
from src.animation import LMSScene


# ============================================================
# VISUAL THEME
# ============================================================

BG = "#090D16"
WHITE = "#F5F7FA"
MUTED = "#7E8797"
GRID = "#273244"

BLUE = "#38BDF8"       # data / structure
GREEN = "#5BE7A9"      # behavior / objects
YELLOW = "#FFD166"     # emphasis
PURPLE = "#A78BFA"     # blueprint
ORANGE = "#FF9F43"     # real-world metaphor
RED = "#FF6B6B"        # "not directly usable"


class ClassBlueprintVideo(LMSScene):

    def construct(self):
        self.camera.background_color = BG

        self.hook()
        self.introduction()
        self.how()
        self.what_why()
        self.real_world_example()
        self.summary()
        self.done()

    # ========================================================
    # HELPERS
    # ========================================================

    def title(self, text, color=WHITE, size=52):
        return Text(
            text,
            font_size=size,
            color=color,
            weight=BOLD,
        )

    def mono(self, text, color=WHITE, size=28):
        return Text(
            text,
            font="DejaVu Sans Mono",
            font_size=size,
            color=color,
        )

    def card(
        self,
        label,
        color=BLUE,
        width=3.5,
        height=1.0,
        size=27,
    ):
        box = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.16,
            color=color,
            stroke_width=2.5,
            fill_color=color,
            fill_opacity=0.08,
        )
        txt = Text(
            label,
            font_size=size,
            color=WHITE,
            weight=BOLD,
        )
        txt.move_to(box)
        return VGroup(box, txt)

    def blueprint(self, width=7.5, height=5.0):
        outer = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.2,
            color=PURPLE,
            stroke_width=3,
            fill_color="#0D1420",
            fill_opacity=0.7,
        )

        inner = RoundedRectangle(
            width=width - 0.35,
            height=height - 0.35,
            corner_radius=0.13,
            color=GRID,
            stroke_width=1.5,
        )

        # Technical drafting marks.
        marks = VGroup()
        for x in (-width / 2 + 0.35, width / 2 - 0.35):
            marks.add(
                Line(
                    [x, -height / 2 + 0.15, 0],
                    [x, -height / 2 + 0.38, 0],
                    color=BLUE,
                    stroke_width=2,
                )
            )
        for y in (-height / 2 + 0.35, height / 2 - 0.35):
            marks.add(
                Line(
                    [-width / 2 + 0.15, y, 0],
                    [-width / 2 + 0.38, y, 0],
                    color=BLUE,
                    stroke_width=2,
                )
            )

        return VGroup(outer, inner, marks)

    def cookie_cutter(self):
        outer = RoundedRectangle(
            width=3.5,
            height=3.1,
            corner_radius=0.5,
            color=ORANGE,
            stroke_width=4,
        )

        inner = RoundedRectangle(
            width=2.65,
            height=2.3,
            corner_radius=0.4,
            color=YELLOW,
            stroke_width=3,
            fill_color=ORANGE,
            fill_opacity=0.08,
        )

        top = Arc(
            radius=1.1,
            start_angle=0,
            angle=PI,
            color=BLUE,
            stroke_width=3,
        )
        top.move_to(UP * 1.08)

        return VGroup(outer, inner, top)

    def object_card(self, name, roll, marks):
        box = RoundedRectangle(
            width=3.2,
            height=2.9,
            corner_radius=0.18,
            color=GREEN,
            stroke_width=2.5,
            fill_color="#0B1A18",
            fill_opacity=0.7,
        )

        heading = Text(
            name,
            font_size=29,
            color=GREEN,
            weight=BOLD,
        )
        heading.move_to(box.get_top() + DOWN * 0.45)

        rows = VGroup(
            self.mono(f'name = "{name}"', BLUE, 21),
            self.mono(f"rollNo = {roll}", BLUE, 21),
            self.mono(f"marks = {marks}", BLUE, 21),
        ).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.15,
        )
        rows.move_to(box.get_center() + DOWN * 0.35)

        return VGroup(box, heading, rows)

    # ========================================================
    # 1. HOOK
    # ========================================================

    def hook(self):
        self.scene_start("hook")

        n = self.narrate(
            id="hook_01",
            text=(
                "My dear students, let us honestly bring data members and "
                "member functions truly together, into one complete idea."
            ),
            voice="teacher",
            subtitle=True,
        )

        heading = self.title(
            "BRING TWO IDEAS TOGETHER",
            color=YELLOW,
            size=47,
        )
        heading.to_edge(UP, buff=0.6)

        self.play(
            Write(heading),
            run_time=0.65,
        )

        data = self.card(
            "DATA MEMBERS",
            color=BLUE,
            width=3.5,
        )
        functions = self.card(
            "MEMBER FUNCTIONS",
            color=GREEN,
            width=3.8,
        )

        data.move_to(LEFT * 2.3)
        functions.move_to(RIGHT * 2.3)

        plus = Text(
            "+",
            font_size=55,
            color=WHITE,
            weight=BOLD,
        )
        plus.move_to(ORIGIN)

        self.play(
            FadeIn(data, shift=RIGHT * 0.35),
            FadeIn(functions, shift=LEFT * 0.35),
            Write(plus),
            run_time=1.0,
        )

        self.wait_for_narration(n)

        arrow = Arrow(
            DOWN * 0.1,
            DOWN * 1.4,
            color=YELLOW,
            stroke_width=4,
        )

        complete = self.card(
            "ONE COMPLETE IDEA",
            color=PURPLE,
            width=4.4,
            height=1.15,
            size=30,
        )
        complete.move_to(DOWN * 1.85)

        self.play(
            GrowArrow(arrow),
            FadeIn(complete, shift=UP * 0.25),
            run_time=0.8,
        )

        self.wait(0.6)

        self.play(
            FadeOut(
                VGroup(
                    heading,
                    data,
                    functions,
                    plus,
                    arrow,
                    complete,
                )
            ),
            run_time=0.55,
        )

        self.scene_end("hook")

    # ========================================================
    # 2. INTRODUCTION
    # ========================================================

    def introduction(self):
        self.scene_start("introduction")

        n = self.narrate(
            id="intro_01",
            text="Today we meet the class as a true, complete blueprint.",
            voice="teacher",
            subtitle=True,
        )

        title = self.title(
            "THE CLASS AS A BLUEPRINT",
            color=YELLOW,
            size=60,
        )

        self.play(
            Write(title),
            run_time=0.8,
        )

        self.wait_for_narration(n)

        self.play(
            title.animate.scale(0.72).to_edge(UP, buff=0.6),
            run_time=0.7,
        )

        frame = self.blueprint()

        class_name = self.title(
            "class Student",
            color=PURPLE,
            size=42,
        )
        class_name.move_to(
            frame.get_top() + DOWN * 0.55
        )

        data = self.card(
            "DATA MEMBERS",
            color=BLUE,
            width=3.0,
            height=0.9,
            size=25,
        )
        functions = self.card(
            "MEMBER FUNCTIONS",
            color=GREEN,
            width=3.2,
            height=0.9,
            size=25,
        )

        data.move_to(
            frame.get_center() + LEFT * 1.65 + DOWN * 0.25
        )
        functions.move_to(
            frame.get_center() + RIGHT * 1.65 + DOWN * 0.25
        )

        self.play(
            Create(frame),
            Write(class_name),
            run_time=0.9,
        )

        self.play(
            FadeIn(data, shift=UP * 0.2),
            FadeIn(functions, shift=UP * 0.2),
            run_time=0.75,
        )

        equation = Text(
            "CLASS = DATA + BEHAVIOUR",
            font_size=31,
            color=WHITE,
            weight=BOLD,
        )
        equation.to_edge(DOWN, buff=0.5)

        self.play(
            FadeIn(equation, shift=UP * 0.2),
            run_time=0.55,
        )

        self.wait(0.8)

        self.play(
            FadeOut(
                VGroup(
                    title,
                    frame,
                    class_name,
                    data,
                    functions,
                    equation,
                )
            ),
            run_time=0.55,
        )

        self.scene_end("introduction")

    # ========================================================
    # 3. HOW
    # ========================================================

    def how(self):
        self.scene_start("how")

        n = self.narrate(
            id="how_01",
            text=(
                "A class is genuinely the complete combination of its data members "
                "and member functions, described once, honestly, in one single place, "
                "and this true blueprint itself is never directly used, it is simply, honestly, described."
            ),
            voice="teacher",
            subtitle=True,
        )

        heading = self.title(
            "HOW DOES THE BLUEPRINT WORK?",
            color=YELLOW,
            size=45,
        )
        heading.to_edge(UP, buff=0.55)

        self.play(
            Write(heading),
            run_time=0.65,
        )

        # Main blueprint.
        frame = self.blueprint(
            width=8.6,
            height=5.0,
        )
        frame.move_to(
            LEFT * 0.8
        )

        class_name = self.title(
            "class Student",
            color=PURPLE,
            size=38,
        )
        class_name.move_to(
            frame.get_top() + DOWN * 0.5
        )

        data_code = VGroup(
            self.mono("string name;", BLUE, 25),
            self.mono("int marks;", BLUE, 25),
        ).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.15,
        )
        data_code.move_to(
            frame.get_center() + LEFT * 1.75 + DOWN * 0.3
        )

        fn_code = VGroup(
            self.mono("void displayMarks()", GREEN, 23),
            self.mono("{ ... }", GREEN, 23),
        ).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.15,
        )
        fn_code.move_to(
            frame.get_center() + RIGHT * 1.75 + DOWN * 0.25
        )

        divider = Line(
            frame.get_center() + UP * 1.35,
            frame.get_center() + DOWN * 1.7,
            color=GRID,
            stroke_width=2,
        )

        data_label = Text(
            "DATA",
            font_size=23,
            color=BLUE,
            weight=BOLD,
        )
        data_label.next_to(
            data_code,
            UP,
            buff=0.25,
        )

        fn_label = Text(
            "BEHAVIOUR",
            font_size=23,
            color=GREEN,
            weight=BOLD,
        )
        fn_label.next_to(
            fn_code,
            UP,
            buff=0.25,
        )

        self.play(
            Create(frame),
            Write(class_name),
            run_time=0.9,
        )

        self.play(
            Create(divider),
            FadeIn(data_label),
            FadeIn(fn_label),
            LaggedStart(
                *[
                    FadeIn(x, shift=RIGHT * 0.2)
                    for x in data_code
                ],
                lag_ratio=0.15,
            ),
            LaggedStart(
                *[
                    FadeIn(x, shift=RIGHT * 0.2)
                    for x in fn_code
                ],
                lag_ratio=0.15,
            ),
            run_time=1.0,
        )

        self.wait_for_narration(n)

        # Explicit "description only" cue.
        description = Text(
            "DESCRIBES — IT DOES NOT EXIST AS AN OBJECT",
            font_size=29,
            color=RED,
            weight=BOLD,
        )
        description.to_edge(DOWN, buff=0.45)

        strike = Line(
            frame.get_bottom() + LEFT * 1.8 + DOWN * 0.1,
            frame.get_bottom() + RIGHT * 1.8 + DOWN * 0.1,
            color=RED,
            stroke_width=4,
        )

        self.play(
            FadeIn(description),
            Create(strike),
            run_time=0.65,
        )

        self.wait(0.8)

        self.play(
            FadeOut(
                VGroup(
                    heading,
                    frame,
                    class_name,
                    data_code,
                    fn_code,
                    divider,
                    data_label,
                    fn_label,
                    description,
                    strike,
                )
            ),
            run_time=0.6,
        )

        self.scene_end("how")

    # ========================================================
    # 4. WHAT / WHY
    # ========================================================

    def what_why(self):
        self.scene_start("what_why")

        n = self.narrate(
            id="what_why_01",
            text=(
                "Understanding a class as merely a true description, not a real, usable "
                "thing itself, is precisely the honest foundation object creation, meeting "
                "us next, builds directly on."
            ),
            voice="teacher",
            subtitle=True,
        )

        heading = self.title(
            "DESCRIPTION FIRST",
            color=YELLOW,
            size=51,
        )
        heading.to_edge(UP, buff=0.55)

        self.play(
            Write(heading),
            run_time=0.65,
        )

        # Left: blueprint / description.
        blueprint = self.blueprint(
            width=4.1,
            height=4.0,
        )
        blueprint.move_to(
            LEFT * 3.2 + DOWN * 0.15
        )

        bp_label = self.title(
            "CLASS",
            color=PURPLE,
            size=42,
        )
        bp_label.move_to(
            blueprint.get_top() + DOWN * 0.52
        )

        bp_code = VGroup(
            self.mono("name", BLUE, 25),
            self.mono("marks", BLUE, 25),
            self.mono("displayMarks()", GREEN, 23),
        ).arrange(
            DOWN,
            buff=0.2,
        )
        bp_code.move_to(
            blueprint.get_center() + DOWN * 0.25
        )

        self.play(
            Create(blueprint),
            Write(bp_label),
            LaggedStart(
                *[FadeIn(x) for x in bp_code],
                lag_ratio=0.13,
            ),
            run_time=1.0,
        )

        # Arrow toward "object creation next".
        arrow = Arrow(
            LEFT * 0.7,
            RIGHT * 0.7,
            color=YELLOW,
            stroke_width=4,
        )
        arrow.move_to(
            ORIGIN + DOWN * 0.2
        )

        next_text = Text(
            "OBJECT CREATION",
            font_size=29,
            color=GREEN,
            weight=BOLD,
        )
        next_text.next_to(
            arrow,
            DOWN,
            buff=0.35,
        )

        self.play(
            GrowArrow(arrow),
            FadeIn(next_text),
            run_time=0.65,
        )

        # Right: not yet an object, just a future result.
        ghost = DashedVMobject(
            RoundedRectangle(
                width=3.5,
                height=3.5,
                corner_radius=0.2,
                color=MUTED,
            ),
            num_dashes=24,
        )
        ghost.move_to(
            RIGHT * 3.1 + DOWN * 0.15
        )

        ghost_text = Text(
            "REAL OBJECT\nCOMES NEXT",
            font_size=30,
            color=MUTED,
            weight=BOLD,
            line_spacing=1.1,
        )
        ghost_text.move_to(
            ghost.get_center()
        )

        self.play(
            Create(ghost),
            FadeIn(ghost_text),
            run_time=0.75,
        )

        self.wait_for_narration(n)

        foundation = Text(
            "THE CLASS IS THE DESCRIPTION",
            font_size=30,
            color=PURPLE,
            weight=BOLD,
        )
        foundation.to_edge(DOWN, buff=0.45)

        self.play(
            FadeIn(foundation, shift=UP * 0.15),
            run_time=0.5,
        )

        self.wait(0.7)

        self.play(
            FadeOut(
                VGroup(
                    heading,
                    blueprint,
                    bp_label,
                    bp_code,
                    arrow,
                    next_text,
                    ghost,
                    ghost_text,
                    foundation,
                )
            ),
            run_time=0.6,
        )

        self.scene_end("what_why")

    # ========================================================
    # 5. REAL-WORLD EXAMPLE
    # ========================================================

    def real_world_example(self):
        self.scene_start("real_world_example")

        n = self.narrate(
            id="example_01",
            text=(
                "The cookie cutter's own honest, complete design, ingredients and baking "
                "steps together, described once, though genuinely never itself eaten."
            ),
            voice="teacher",
            subtitle=True,
        )

        heading = self.title(
            "THE COOKIE CUTTER BLUEPRINT",
            color=YELLOW,
            size=45,
        )
        heading.to_edge(UP, buff=0.55)

        self.play(
            Write(heading),
            run_time=0.65,
        )

        cutter = self.cookie_cutter()
        cutter.move_to(
            LEFT * 3.3 + DOWN * 0.2
        )

        cutter_label = Text(
            "DESIGN",
            font_size=29,
            color=ORANGE,
            weight=BOLD,
        )
        cutter_label.next_to(
            cutter,
            DOWN,
            buff=0.25,
        )

        self.play(
            Create(cutter),
            FadeIn(cutter_label),
            run_time=0.9,
        )

        # Ingredients = data.
        ingredients = VGroup(
            self.card("FLOUR", BLUE, width=2.15, height=0.72, size=22),
            self.card("SUGAR", BLUE, width=2.15, height=0.72, size=22),
            self.card("BUTTER", BLUE, width=2.15, height=0.72, size=22),
        ).arrange(
            DOWN,
            buff=0.13,
        )
        ingredients.move_to(
            RIGHT * 1.0 + UP * 0.65
        )

        ingredients_label = Text(
            "INGREDIENTS",
            font_size=24,
            color=BLUE,
            weight=BOLD,
        )
        ingredients_label.next_to(
            ingredients,
            UP,
            buff=0.22,
        )

        # Baking steps = functions.
        steps = VGroup(
            self.card("MIX()", GREEN, width=2.15, height=0.72, size=22),
            self.card("CUT()", GREEN, width=2.15, height=0.72, size=22),
            self.card("BAKE()", GREEN, width=2.15, height=0.72, size=22),
        ).arrange(
            DOWN,
            buff=0.13,
        )
        steps.move_to(
            RIGHT * 4.2 + UP * 0.65
        )

        steps_label = Text(
            "ACTIONS",
            font_size=24,
            color=GREEN,
            weight=BOLD,
        )
        steps_label.next_to(
            steps,
            UP,
            buff=0.22,
        )

        self.play(
            FadeIn(ingredients_label),
            LaggedStart(
                *[
                    FadeIn(x, shift=RIGHT * 0.2)
                    for x in ingredients
                ],
                lag_ratio=0.14,
            ),
            run_time=0.8,
        )

        self.play(
            FadeIn(steps_label),
            LaggedStart(
                *[
                    FadeIn(x, shift=RIGHT * 0.2)
                    for x in steps
                ],
                lag_ratio=0.14,
            ),
            run_time=0.8,
        )

        # Connect metaphor to blueprint.
        c1 = CurvedArrow(
            cutter.get_right(),
            ingredients.get_left(),
            color=BLUE,
            stroke_width=3,
        )
        c2 = CurvedArrow(
            cutter.get_right() + DOWN * 0.15,
            steps.get_left(),
            color=GREEN,
            stroke_width=3,
        )

        self.play(
            Create(c1),
            Create(c2),
            run_time=0.65,
        )

        self.wait_for_narration(n)

        never_eaten = Text(
            "THE CUTTER ITSELF IS NOT THE COOKIE",
            font_size=29,
            color=RED,
            weight=BOLD,
        )
        never_eaten.to_edge(
            DOWN,
            buff=0.45,
        )

        self.play(
            FadeIn(never_eaten, shift=UP * 0.2),
            run_time=0.5,
        )

        self.wait(0.75)

        # Transform metaphor back into OOP.
        self.play(
            FadeOut(
                VGroup(
                    heading,
                    cutter,
                    cutter_label,
                    ingredients,
                    ingredients_label,
                    steps,
                    steps_label,
                    c1,
                    c2,
                    never_eaten,
                )
            ),
            run_time=0.6,
        )

        self.scene_end("real_world_example")

    # ========================================================
    # 6. SUMMARY
    # ========================================================

    def summary(self):
        self.scene_start("summary")

        n = self.narrate(
            id="summary_01",
            text=(
                "A class is the complete blueprint combining data members and member "
                "functions, described once but not directly used."
            ),
            voice="teacher",
            subtitle=True,
        )

        heading = self.title(
            "CLASS = COMPLETE BLUEPRINT",
            color=YELLOW,
            size=49,
        )
        heading.to_edge(UP, buff=0.55)

        self.play(
            Write(heading),
            run_time=0.65,
        )

        data = self.card(
            "DATA MEMBERS",
            color=BLUE,
            width=3.3,
        )
        functions = self.card(
            "MEMBER FUNCTIONS",
            color=GREEN,
            width=3.5,
        )

        plus = Text(
            "+",
            font_size=48,
            color=WHITE,
            weight=BOLD,
        )

        combined = self.card(
            "CLASS BLUEPRINT",
            color=PURPLE,
            width=3.5,
            height=1.15,
            size=30,
        )

        top = VGroup(
            data,
            plus,
            functions,
        ).arrange(
            RIGHT,
            buff=0.28,
        )
        top.move_to(
            UP * 0.8
        )

        arrow = Arrow(
            DOWN * 0.05,
            DOWN * 0.9,
            color=YELLOW,
            stroke_width=4,
        )
        arrow.move_to(
            DOWN * 0.15
        )

        combined.move_to(
            DOWN * 1.35
        )

        self.play(
            FadeIn(data, shift=RIGHT * 0.25),
            Write(plus),
            FadeIn(functions, shift=LEFT * 0.25),
            run_time=0.85,
        )

        self.play(
            GrowArrow(arrow),
            FadeIn(combined, shift=UP * 0.2),
            run_time=0.75,
        )

        # "Described once" cue.
        described_once = Text(
            "DESCRIBED ONCE",
            font_size=31,
            color=PURPLE,
            weight=BOLD,
        )
        described_once.to_edge(
            DOWN,
            buff=1.05,
        )

        not_object = Text(
            "NOT DIRECTLY USED AS AN OBJECT",
            font_size=27,
            color=RED,
            weight=BOLD,
        )
        not_object.to_edge(
            DOWN,
            buff=0.48,
        )

        self.play(
            FadeIn(described_once),
            FadeIn(not_object),
            run_time=0.65,
        )

        self.wait_for_narration(n)

        self.play(
            Indicate(
                combined,
                color=PURPLE,
                scale_factor=1.06,
            ),
            run_time=0.8,
        )

        self.play(
            FadeOut(
                VGroup(
                    heading,
                    data,
                    plus,
                    functions,
                    combined,
                    arrow,
                    described_once,
                    not_object,
                )
            ),
            run_time=0.6,
        )

        self.scene_end("summary")

    # ========================================================
    # 7. DONE
    # ========================================================

    def done(self):
        self.scene_start("done")

        n = self.narrate(
            id="done_01",
            text=(
                "Truly excellent work, my dear students. We have now fully met "
                "a class's own true anatomy. I will see you in the next video, "
                "as we bring a real object to life from it."
            ),
            voice="teacher",
            subtitle=True,
        )

        title = self.title(
            "CLASS AS A BLUEPRINT",
            color=PURPLE,
            size=57,
        )
        title.move_to(
            UP * 1.35
        )

        check = MathTex(
            r"\checkmark",
            color=GREEN,
        ).scale(1.3)
        check.next_to(
            title,
            RIGHT,
            buff=0.3,
        )

        anatomy = VGroup(
            self.card(
                "DATA MEMBERS",
                color=BLUE,
                width=3.1,
                height=0.82,
                size=24,
            ),
            Text(
                "+",
                font_size=38,
                color=WHITE,
                weight=BOLD,
            ),
            self.card(
                "MEMBER FUNCTIONS",
                color=GREEN,
                width=3.4,
                height=0.82,
                size=24,
            ),
        ).arrange(
            RIGHT,
            buff=0.22,
        )
        anatomy.scale(0.9)
        anatomy.move_to(
            DOWN * 0.1
        )

        summary_line = Text(
            "ONE BLUEPRINT • ONE COMPLETE DESCRIPTION",
            font_size=28,
            color=WHITE,
            weight=BOLD,
        )
        summary_line.to_edge(
            DOWN,
            buff=1.25,
        )

        next_card = self.card(
            "NEXT → OBJECT CREATION",
            color=YELLOW,
            width=5.6,
            height=1.0,
            size=29,
        )
        next_card.to_edge(
            DOWN,
            buff=0.45,
        )

        self.play(
            Write(title),
            Write(check),
            run_time=0.75,
        )

        self.play(
            FadeIn(anatomy, shift=UP * 0.2),
            run_time=0.7,
        )

        self.play(
            FadeIn(summary_line),
            FadeIn(next_card, shift=UP * 0.25),
            run_time=0.7,
        )

        self.wait_for_narration(n)

        self.play(
            Indicate(
                next_card,
                color=YELLOW,
                scale_factor=1.05,
            ),
            run_time=0.8,
        )

        self.play(
            FadeOut(
                VGroup(
                    title,
                    check,
                    anatomy,
                    summary_line,
                    next_card,
                )
            ),
            run_time=0.75,
        )

        self.scene_end("done")
