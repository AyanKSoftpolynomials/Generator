"""
Data Members — C-CAT | Section A | Module 2: OOP (C++)
Day 23 | Subtopic A: Class Definition

Manim-only lesson animation.

Source lesson:
- Hook
- Introduction
- How
- What / Why
- Real-world example
- Summary
- Done

animation.py remains the authoring source of truth.
The existing LMS generator handles:
TTS -> voice selection -> audio timing -> WhisperX -> subtitles -> FFmpeg.
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

BLUE = "#38BDF8"       # class / data
CYAN = "#67E8F9"       # technical accents
YELLOW = "#FFD166"     # emphasis
GREEN = "#5BE7A9"      # object / ownership
PURPLE = "#A78BFA"     # blueprint
ORANGE = "#FF9F43"     # real-world object
RED = "#FF6B6B"        # warnings / incorrect


class DataMembersVideo(LMSScene):
    """
    Data Members lesson.

    Central visual metaphor:
        CLASS BLUEPRINT
              |
              +---- data members
                    |
                    +---- each object gets its own copy

    The lesson moves from an abstract class -> a concrete Student class
    -> individual objects -> each object's own data.
    """

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

    def mono(self, text, color=WHITE, size=30):
        return Text(
            text,
            font="DejaVu Sans Mono",
            font_size=size,
            color=color,
        )

    def rounded_card(
        self,
        label,
        color=BLUE,
        width=3.3,
        height=1.05,
        size=25,
    ):
        box = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.15,
            stroke_color=color,
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

    def class_frame(self, width=8.6, height=5.0):
        outer = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.18,
            stroke_color=BLUE,
            stroke_width=3,
            fill_color="#0D1524",
            fill_opacity=0.65,
        )

        inner = RoundedRectangle(
            width=width - 0.42,
            height=height - 0.42,
            corner_radius=0.12,
            stroke_color=GRID,
            stroke_width=1.5,
        )

        return VGroup(outer, inner)

    def variable_row(self, name, value, y=0, color=BLUE):
        name_obj = self.mono(name, color=color, size=28)
        equals = self.mono("=", color=WHITE, size=28)
        value_obj = self.mono(value, color=YELLOW, size=28)

        row = VGroup(
            name_obj,
            equals,
            value_obj,
        ).arrange(RIGHT, buff=0.18)

        row.move_to([0, y, 0])
        return row

    def student_object(self, name, number, marks):
        card = RoundedRectangle(
            width=3.45,
            height=3.0,
            corner_radius=0.2,
            stroke_color=GREEN,
            stroke_width=2.5,
            fill_color="#0B1A18",
            fill_opacity=0.65,
        )

        label = Text(
            name,
            font_size=30,
            color=GREEN,
            weight=BOLD,
        )
        label.move_to(card.get_top() + DOWN * 0.48)

        divider = Line(
            card.get_left() + RIGHT * 0.3 + DOWN * 0.05,
            card.get_right() + LEFT * 0.3 + DOWN * 0.05,
            color=GRID,
            stroke_width=2,
        )

        name_row = self.variable_row(
            "name",
            f'"{name}"',
            y=0,
            color=BLUE,
        )
        number_row = self.variable_row(
            "rollNo",
            str(number),
            y=0,
            color=BLUE,
        )
        marks_row = self.variable_row(
            "marks",
            str(marks),
            y=0,
            color=BLUE,
        )

        rows = VGroup(
            name_row,
            number_row,
            marks_row,
        ).arrange(
            DOWN,
            buff=0.22,
        )

        rows.scale(0.82)
        rows.move_to(card.get_center() + DOWN * 0.35)

        return VGroup(
            card,
            label,
            divider,
            rows,
        )

    def cookie_shape(self):
        outer = RoundedRectangle(
            width=3.2,
            height=3.0,
            corner_radius=0.48,
            color=ORANGE,
            stroke_width=4,
        )

        inner = RoundedRectangle(
            width=2.45,
            height=2.25,
            corner_radius=0.35,
            color=YELLOW,
            stroke_width=2.5,
        )

        inner.set_fill(ORANGE, opacity=0.12)

        center = Dot(
            ORIGIN,
            radius=0.06,
            color=YELLOW,
        )

        return VGroup(
            outer,
            inner,
            center,
        )

    def ingredient_chip(self, text, color=BLUE):
        return self.rounded_card(
            text,
            color=color,
            width=2.3,
            height=0.8,
            size=24,
        )

    # ========================================================
    # 1. HOOK
    # ========================================================

    def hook(self):
        self.scene_start("hook")

        n = self.narrate(
            id="hook_01",
            text=(
                "My dear students, a class genuinely needs some honest "
                "place to truly hold its own data."
            ),
            voice="teacher",
            subtitle=True,
        )

        heading = self.title(
            "A CLASS NEEDS A PLACE TO HOLD DATA",
            color=YELLOW,
            size=43,
        )
        heading.to_edge(UP, buff=0.6)

        self.play(
            FadeIn(heading, shift=UP * 0.2),
            run_time=0.6,
        )

        # Empty blueprint/container.
        container = self.class_frame(
            width=8.2,
            height=4.3,
        )

        container.move_to(ORIGIN)

        class_label = self.title(
            "CLASS",
            color=BLUE,
            size=52,
        )
        class_label.move_to(
            container.get_top() + DOWN * 0.55
        )

        empty = Text(
            "WHERE IS THE DATA?",
            font_size=34,
            color=MUTED,
            weight=BOLD,
        )
        empty.move_to(
            container.get_center() + DOWN * 0.35
        )

        self.play(
            Create(container),
            Write(class_label),
            FadeIn(empty),
            run_time=1.0,
        )

        self.wait_for_narration(n)

        # A data field drops into the class.
        data_box = self.rounded_card(
            "name",
            color=BLUE,
            width=2.4,
            height=0.9,
            size=30,
        )
        data_box.move_to(
            container.get_center() + DOWN * 0.7
        )

        arrow = Arrow(
            data_box.get_top() + UP * 1.3,
            data_box.get_top() + UP * 0.1,
            color=YELLOW,
            stroke_width=4,
        )

        self.play(
            FadeIn(arrow),
            run_time=0.4,
        )

        self.play(
            FadeIn(data_box, shift=DOWN * 0.8),
            run_time=0.7,
        )

        self.play(
            Flash(
                data_box.get_center(),
                color=YELLOW,
                line_length=0.25,
            ),
        )

        self.wait(0.5)

        self.play(
            FadeOut(
                VGroup(
                    heading,
                    container,
                    class_label,
                    empty,
                    data_box,
                    arrow,
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
            text="Today we meet data members.",
            voice="teacher",
            subtitle=True,
        )

        title = self.title(
            "DATA MEMBERS",
            color=YELLOW,
            size=68,
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

        definition = Text(
            "VARIABLES THAT BELONG INSIDE A CLASS",
            font_size=34,
            color=WHITE,
            weight=BOLD,
        )

        definition.move_to(
            ORIGIN + UP * 0.45
        )

        self.play(
            FadeIn(definition, shift=UP * 0.2),
            run_time=0.55,
        )

        self.wait(0.5)

        # Visual: variables live inside the class.
        frame = self.class_frame(
            width=7.2,
            height=3.0,
        )
        frame.move_to(DOWN * 0.85)

        student_class = self.mono(
            "class Student",
            color=BLUE,
            size=31,
        )
        student_class.move_to(
            frame.get_top() + DOWN * 0.5
        )

        members = VGroup(
            self.mono("name;", color=WHITE, size=28),
            self.mono("rollNo;", color=WHITE, size=28),
            self.mono("marks;", color=WHITE, size=28),
        ).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.16,
        )

        members.move_to(
            frame.get_center() + DOWN * 0.25
        )

        self.play(
            Create(frame),
            Write(student_class),
            LaggedStart(
                *[FadeIn(x, shift=RIGHT * 0.25) for x in members],
                lag_ratio=0.18,
            ),
            run_time=1.1,
        )

        label = Text(
            "DATA MEMBERS",
            font_size=29,
            color=YELLOW,
            weight=BOLD,
        )
        label.to_edge(DOWN, buff=0.45)

        self.play(
            FadeIn(label),
            run_time=0.45,
        )

        self.wait(0.8)

        self.play(
            FadeOut(
                VGroup(
                    title,
                    definition,
                    frame,
                    student_class,
                    members,
                    label,
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
                "Data members are honestly the variables declared directly "
                "inside a class, describing the true information each object "
                "of that class will genuinely, individually hold."
            ),
            voice="teacher",
            subtitle=True,
        )

        heading = self.title(
            "HOW DO DATA MEMBERS WORK?",
            color=YELLOW,
            size=47,
        )
        heading.to_edge(UP, buff=0.55)

        self.play(
            Write(heading),
            run_time=0.65,
        )

        # Blueprint on left.
        blueprint = self.class_frame(
            width=4.4,
            height=4.2,
        )
        blueprint.move_to(LEFT * 3.1)

        class_name = self.title(
            "Student",
            color=BLUE,
            size=38,
        )
        class_name.move_to(
            blueprint.get_top() + DOWN * 0.55
        )

        data_members = VGroup(
            self.rounded_card(
                "name",
                color=BLUE,
                width=2.4,
                height=0.75,
                size=26,
            ),
            self.rounded_card(
                "rollNo",
                color=BLUE,
                width=2.4,
                height=0.75,
                size=26,
            ),
            self.rounded_card(
                "marks",
                color=BLUE,
                width=2.4,
                height=0.75,
                size=26,
            ),
        ).arrange(
            DOWN,
            buff=0.18,
        )

        data_members.move_to(
            blueprint.get_center() + DOWN * 0.35
        )

        # Objects on right.
        object_a = self.student_object(
            "Aarav",
            101,
            88,
        )
        object_b = self.student_object(
            "Meera",
            102,
            94,
        )

        object_a.scale(0.72)
        object_b.scale(0.72)

        objects = VGroup(
            object_a,
            object_b,
        ).arrange(
            DOWN,
            buff=0.25,
        )
        objects.move_to(RIGHT * 3.0)

        arrow_a = Arrow(
            blueprint.get_right(),
            object_a.get_left(),
            color=GREEN,
            stroke_width=3,
        )

        arrow_b = Arrow(
            blueprint.get_right() + DOWN * 0.15,
            object_b.get_left(),
            color=GREEN,
            stroke_width=3,
        )

        self.play(
            Create(blueprint),
            Write(class_name),
            LaggedStart(
                *[
                    FadeIn(x, scale=0.9)
                    for x in data_members
                ],
                lag_ratio=0.12,
            ),
            run_time=1.15,
        )

        self.play(
            GrowArrow(arrow_a),
            GrowArrow(arrow_b),
            run_time=0.65,
        )

        self.play(
            FadeIn(object_a, shift=RIGHT * 0.3),
            FadeIn(object_b, shift=RIGHT * 0.3),
            run_time=0.9,
        )

        self.wait_for_narration(n)

        # The members are copied into objects.
        copy_label = Text(
            "EACH OBJECT GETS ITS OWN COPY",
            font_size=30,
            color=GREEN,
            weight=BOLD,
        )
        copy_label.to_edge(DOWN, buff=0.45)

        self.play(
            FadeIn(copy_label, shift=UP * 0.15),
            run_time=0.55,
        )

        for target in [
            object_a.get_center(),
            object_b.get_center(),
        ]:
            self.play(
                Flash(
                    target,
                    color=GREEN,
                    line_length=0.3,
                ),
                run_time=0.45,
            )

        self.wait(0.6)

        self.play(
            FadeOut(
                VGroup(
                    heading,
                    blueprint,
                    class_name,
                    data_members,
                    objects,
                    arrow_a,
                    arrow_b,
                    copy_label,
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
            id="what_01",
            text=(
                "These are precisely the true, honest fields every object "
                "made from this blueprint will genuinely carry its own copy of."
            ),
            voice="teacher",
            subtitle=True,
        )

        heading = self.title(
            "WHAT DOES EACH OBJECT CARRY?",
            color=YELLOW,
            size=45,
        )
        heading.to_edge(UP, buff=0.55)

        self.play(
            Write(heading),
            run_time=0.65,
        )

        # One blueprint, three objects.
        blueprint = self.class_frame(
            width=3.7,
            height=4.2,
        )
        blueprint.move_to(LEFT * 3.9)

        class_name = self.title(
            "Student",
            color=BLUE,
            size=38,
        )
        class_name.move_to(
            blueprint.get_top() + DOWN * 0.55
        )

        blueprint_members = VGroup(
            self.mono("name", color=BLUE, size=28),
            self.mono("rollNo", color=BLUE, size=28),
            self.mono("marks", color=BLUE, size=28),
        ).arrange(
            DOWN,
            buff=0.25,
        )
        blueprint_members.move_to(
            blueprint.get_center() + DOWN * 0.35
        )

        self.play(
            Create(blueprint),
            Write(class_name),
            LaggedStart(
                *[FadeIn(x, shift=RIGHT * 0.2)
                  for x in blueprint_members],
                lag_ratio=0.12,
            ),
            run_time=1.0,
        )

        # Objects.
        obj1 = self.student_object("Aarav", 101, 88)
        obj2 = self.student_object("Meera", 102, 94)
        obj3 = self.student_object("Kabir", 103, 76)

        for obj in [obj1, obj2, obj3]:
            obj.scale(0.52)

        object_row = VGroup(
            obj1,
            obj2,
            obj3,
        ).arrange(
            RIGHT,
            buff=0.15,
        )
        object_row.move_to(RIGHT * 2.35 + DOWN * 0.2)

        connectors = VGroup()

        for obj in [obj1, obj2, obj3]:
            connectors.add(
                Arrow(
                    blueprint.get_right(),
                    obj.get_left(),
                    color=GREEN,
                    stroke_width=2.5,
                )
            )

        self.play(
            LaggedStart(
                *[
                    GrowArrow(line)
                    for line in connectors
                ],
                lag_ratio=0.1,
            ),
            run_time=0.75,
        )

        self.play(
            LaggedStart(
                *[
                    FadeIn(obj, shift=RIGHT * 0.2)
                    for obj in object_row
                ],
                lag_ratio=0.14,
            ),
            run_time=1.0,
        )

        self.wait_for_narration(n)

        own_copy = Text(
            "OWN COPY",
            font_size=29,
            color=GREEN,
            weight=BOLD,
        )

        own_copy.next_to(
            object_row,
            DOWN,
            buff=0.35,
        )

        self.play(
            FadeIn(own_copy, shift=UP * 0.15),
            run_time=0.5,
        )

        # Make each object flash in a different color emphasis.
        for obj in [obj1, obj2, obj3]:
            self.play(
                Indicate(
                    obj,
                    color=GREEN,
                    scale_factor=1.04,
                ),
                run_time=0.5,
            )

        self.play(
            FadeOut(
                VGroup(
                    heading,
                    blueprint,
                    class_name,
                    blueprint_members,
                    connectors,
                    object_row,
                    own_copy,
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
                "A cookie cutter's own honest design listing exactly which "
                "ingredients each cookie will genuinely, truly need."
            ),
            voice="teacher",
            subtitle=True,
        )

        heading = self.title(
            "REAL-WORLD EXAMPLE",
            color=YELLOW,
            size=48,
        )
        heading.to_edge(UP, buff=0.55)

        self.play(
            Write(heading),
            run_time=0.65,
        )

        cutter = self.cookie_shape()
        cutter.move_to(LEFT * 3.6 + DOWN * 0.15)

        cutter_label = Text(
            "COOKIE CUTTER",
            font_size=30,
            color=ORANGE,
            weight=BOLD,
        )
        cutter_label.next_to(
            cutter,
            DOWN,
            buff=0.3,
        )

        self.play(
            Create(cutter),
            FadeIn(cutter_label),
            run_time=0.9,
        )

        # Ingredient data.
        ingredient_box = RoundedRectangle(
            width=5.2,
            height=3.65,
            corner_radius=0.18,
            stroke_color=BLUE,
            stroke_width=2.5,
            fill_color="#0D1524",
            fill_opacity=0.7,
        )
        ingredient_box.move_to(
            RIGHT * 2.45 + DOWN * 0.05
        )

        box_title = Text(
            "WHAT EACH COOKIE NEEDS",
            font_size=29,
            color=BLUE,
            weight=BOLD,
        )
        box_title.move_to(
            ingredient_box.get_top() + DOWN * 0.52
        )

        chips = VGroup(
            self.ingredient_chip("flour", BLUE),
            self.ingredient_chip("sugar", YELLOW),
            self.ingredient_chip("butter", GREEN),
            self.ingredient_chip("shape", PURPLE),
        )

        chips.arrange(
            RIGHT,
            buff=0.12,
        )
        chips.scale(0.84)
        chips.move_to(
            ingredient_box.get_center() + DOWN * 0.2
        )

        self.play(
            Create(ingredient_box),
            Write(box_title),
            run_time=0.8,
        )

        self.play(
            LaggedStart(
                *[
                    FadeIn(chip, scale=0.85)
                    for chip in chips
                ],
                lag_ratio=0.15,
            ),
            run_time=0.9,
        )

        arrow = CurvedArrow(
            cutter.get_right(),
            ingredient_box.get_left(),
            color=ORANGE,
            stroke_width=3.5,
        )

        self.play(
            Create(arrow),
            run_time=0.55,
        )

        self.wait_for_narration(n)

        # Connect metaphor explicitly.
        class_analogy = Text(
            "CLASS  →  DESIGN / BLUEPRINT",
            font_size=31,
            color=BLUE,
            weight=BOLD,
        )
        class_analogy.move_to(
            DOWN * 1.95
        )

        object_analogy = Text(
            "OBJECT  →  ONE COOKIE",
            font_size=31,
            color=GREEN,
            weight=BOLD,
        )
        object_analogy.move_to(
            DOWN * 2.45
        )

        self.play(
            FadeIn(class_analogy, shift=UP * 0.15),
            FadeIn(object_analogy, shift=UP * 0.15),
            run_time=0.65,
        )

        self.wait(0.7)

        self.play(
            FadeOut(
                VGroup(
                    heading,
                    cutter,
                    cutter_label,
                    ingredient_box,
                    box_title,
                    chips,
                    arrow,
                    class_analogy,
                    object_analogy,
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
                "Data members are the variables declared inside a class, "
                "describing what information each object will hold."
            ),
            voice="teacher",
            subtitle=True,
        )

        heading = self.title(
            "DATA MEMBERS",
            color=YELLOW,
            size=57,
        )
        heading.to_edge(UP, buff=0.55)

        self.play(
            Write(heading),
            run_time=0.65,
        )

        # Compact equation-like visual.
        class_box = self.rounded_card(
            "CLASS",
            color=BLUE,
            width=2.5,
            height=0.95,
            size=32,
        )

        plus = Text(
            "+",
            font_size=45,
            color=WHITE,
            weight=BOLD,
        )

        variables = self.rounded_card(
            "VARIABLES",
            color=YELLOW,
            width=3.0,
            height=0.95,
            size=31,
        )

        arrow = Arrow(
            ORIGIN,
            RIGHT * 1.2,
            color=GREEN,
            stroke_width=4,
        )

        object_box = self.rounded_card(
            "OBJECT HOLDS DATA",
            color=GREEN,
            width=4.1,
            height=1.05,
            size=30,
        )

        top_row = VGroup(
            class_box,
            plus,
            variables,
        ).arrange(
            RIGHT,
            buff=0.28,
        )
        top_row.move_to(
            UP * 0.8
        )

        object_box.move_to(
            DOWN * 0.65
        )

        self.play(
            FadeIn(class_box, shift=RIGHT * 0.2),
            FadeIn(plus),
            FadeIn(variables, scale=1.05),
            run_time=0.9,
        )

        self.play(
            GrowArrow(arrow),
            FadeIn(object_box, shift=DOWN * 0.2),
            run_time=0.8,
        )

        self.wait_for_narration(n)

        # Formal code reminder.
        code = VGroup(
            self.mono("class Student", BLUE, 28),
            self.mono("string name;", WHITE, 28),
            self.mono("int rollNo;", WHITE, 28),
            self.mono("int marks;", WHITE, 28),
        ).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.12,
        )

        code.move_to(
            DOWN * 2.1
        )

        self.play(
            LaggedStart(
                *[
                    FadeIn(line, shift=RIGHT * 0.15)
                    for line in code
                ],
                lag_ratio=0.08,
            ),
            run_time=0.8,
        )

        self.wait(0.7)

        self.play(
            FadeOut(
                VGroup(
                    heading,
                    top_row,
                    arrow,
                    object_box,
                    code,
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
                "Well done, my dear students. Now let us meet the true "
                "behaviour a class can also genuinely offer. "
                "I will see you in the next video, for Member Functions."
            ),
            voice="teacher",
            subtitle=True,
        )

        main = self.title(
            "DATA MEMBERS",
            color=YELLOW,
            size=60,
        )
        main.move_to(
            UP * 1.25
        )

        check = MathTex(
            r"\checkmark",
            color=GREEN,
        ).scale(1.25)
        check.next_to(
            main,
            RIGHT,
            buff=0.3,
        )

        statement = Text(
            "WHAT INFORMATION DOES AN OBJECT HOLD?",
            font_size=31,
            color=WHITE,
            weight=BOLD,
        )
        statement.next_to(
            main,
            DOWN,
            buff=0.5,
        )

        next_card = self.rounded_card(
            "NEXT → MEMBER FUNCTIONS",
            color=GREEN,
            width=5.2,
            height=1.05,
            size=31,
        )
        next_card.to_edge(
            DOWN,
            buff=0.65,
        )

        self.play(
            Write(main),
            Write(check),
            run_time=0.75,
        )

        self.play(
            FadeIn(statement, shift=UP * 0.2),
            run_time=0.5,
        )

        self.play(
            FadeIn(next_card, shift=UP * 0.3),
            run_time=0.7,
        )

        self.wait_for_narration(n)

        self.play(
            Indicate(
                next_card,
                color=GREEN,
                scale_factor=1.05,
            ),
            run_time=0.8,
        )

        self.play(
            FadeOut(
                VGroup(
                    main,
                    check,
                    statement,
                    next_card,
                )
            ),
            run_time=0.7,
        )

        self.scene_end("done")
