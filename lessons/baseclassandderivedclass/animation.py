from manim import *
from src.animation import LMSScene


class BaseClassAndDerivedClass(LMSScene):
    """
    Lesson: Base Class and Derived Class
    Source: 01 - Base Class and Derived Class.pdf

    Layout principle:
    - Every text element is explicitly sized to its container.
    - Long narration is split into short visual phrases.
    - Important objects stay inside conservative camera safe margins.
    """

    # ---------- layout helpers ----------

    def fit_to_box(self, mob, max_width, max_height, margin=0.0):
        """Scale a mobject down only when necessary."""
        target_w = max_width - 2 * margin
        target_h = max_height - 2 * margin
        if mob.width > target_w:
            mob.scale_to_fit_width(target_w)
        if mob.height > target_h:
            mob.scale_to_fit_height(target_h)
        return mob

    def safe_title(self, text, width=11.5):
        title = Text(text, font_size=40, weight=BOLD)
        self.fit_to_box(title, width, 0.9)
        return title

    def card(self, title, body_lines, width=5.0, height=2.2, title_size=30, body_size=23):
        box = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.16,
            stroke_width=2.5,
        )

        heading = Text(title, font_size=title_size, weight=BOLD)
        self.fit_to_box(heading, width - 0.45, 0.48)

        body = Paragraph(
            *body_lines,
            alignment="center",
            font_size=body_size,
            line_spacing=0.9,
        )
        self.fit_to_box(body, width - 0.5, height - 0.9)

        content = VGroup(heading, body).arrange(DOWN, buff=0.22)
        self.fit_to_box(content, width - 0.35, height - 0.25)

        return VGroup(box, content), box, heading, body

    def role_node(self, role, alias, width=4.7, height=2.35):
        box = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.18,
            stroke_width=3,
        )
        role_text = Text(role, font_size=34, weight=BOLD)
        alias_text = Text(alias, font_size=23)
        self.fit_to_box(role_text, width - 0.5, 0.55)
        self.fit_to_box(alias_text, width - 0.5, 0.42)

        group = VGroup(role_text, alias_text).arrange(DOWN, buff=0.18)
        self.fit_to_box(group, width - 0.35, height - 0.35)

        return VGroup(box, group), box, role_text, alias_text

    # ---------- lesson ----------

    def construct(self):
        self.camera.background_color = "#0B1020"

        # =========================================================
        # 1. HOOK
        # =========================================================
        n1 = self.narrate(
            id="hook",
            text="My dear students, in every inheritance relationship, one class always gives, and another always receives.",
            voice="default",
            subtitle=True,
        )

        self.scene_start("hook")

        title = self.safe_title("Inheritance: One Class Gives, Another Receives")
        title.to_edge(UP, buff=0.45)

        giver = Circle(radius=1.0, stroke_width=3)
        receiver = Circle(radius=1.0, stroke_width=3)
        giver_label = Text("GIVES", font_size=28, weight=BOLD)
        receiver_label = Text("RECEIVES", font_size=28, weight=BOLD)
        giver_label.move_to(giver)
        receiver_label.move_to(receiver)

        giver_group = VGroup(giver, giver_label).move_to(LEFT * 3.1 + DOWN * 0.4)
        receiver_group = VGroup(receiver, receiver_label).move_to(RIGHT * 3.1 + DOWN * 0.4)

        arrow = Arrow(
            giver_group.get_right() + RIGHT * 0.15,
            receiver_group.get_left() + LEFT * 0.15,
            buff=0.1,
            stroke_width=6,
        )

        self.play(FadeIn(title, shift=DOWN * 0.2))
        self.play(FadeIn(giver_group), FadeIn(receiver_group))
        self.play(GrowArrow(arrow))
        self.wait_for_narration(n1)
        self.scene_end("hook")

        # =========================================================
        # 2. INTRO
        # =========================================================
        n2 = self.narrate(
            id="intro",
            text="Today we meet these two roles by their proper names.",
            voice="default",
            subtitle=True,
        )

        self.scene_start("intro")

        intro_title = self.safe_title("The Two Roles", width=8.5)
        intro_title.to_edge(UP, buff=0.45)

        base = self.role_node("BASE CLASS", "(parent)")
        derived = self.role_node("DERIVED CLASS", "(child)")
        base[0].move_to(LEFT * 3.1 + DOWN * 0.55)
        derived[0].move_to(RIGHT * 3.1 + DOWN * 0.55)

        naming_arrow = Arrow(
            base[0].get_right() + RIGHT * 0.18,
            derived[0].get_left() + LEFT * 0.18,
            buff=0.08,
            stroke_width=5,
        )

        self.play(
            FadeOut(title, shift=UP * 0.15),
            FadeOut(giver_group),
            FadeOut(receiver_group),
            FadeOut(arrow),
        )
        self.play(FadeIn(intro_title), FadeIn(base[0]), FadeIn(derived[0]))
        self.play(GrowArrow(naming_arrow))
        self.wait_for_narration(n2)
        self.scene_end("intro")

        # =========================================================
        # 3. HOW
        # =========================================================
        n3 = self.narrate(
            id="how",
            text=(
                "The base class, also called the parent class, is the existing class being inherited from, "
                "while the derived class, also called the child class, is the new class that inherits the "
                "base class's members, gaining access to them without rewriting a single line."
            ),
            voice="default",
            subtitle=True,
        )

        self.scene_start("how")

        how_title = self.safe_title("Base → Derived: What the Relationship Means")
        how_title.to_edge(UP, buff=0.42)

        base_box = RoundedRectangle(width=4.4, height=3.45, corner_radius=0.18, stroke_width=3)
        derived_box = RoundedRectangle(width=4.4, height=3.45, corner_radius=0.18, stroke_width=3)

        base_head = Text("Base Class", font_size=34, weight=BOLD)
        derived_head = Text("Derived Class", font_size=34, weight=BOLD)
        self.fit_to_box(base_head, 3.9, 0.5)
        self.fit_to_box(derived_head, 3.9, 0.5)

        base_members = VGroup(
            Text("name", font_size=25),
            Text("marks", font_size=25),
            Text("display()", font_size=25),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)

        inherited_members = VGroup(
            Text("name", font_size=25),
            Text("marks", font_size=25),
            Text("display()", font_size=25),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)

        for item in list(base_members) + list(inherited_members):
            self.fit_to_box(item, 3.3, 0.42)

        base_content = VGroup(base_head, base_members).arrange(DOWN, buff=0.28)
        derived_content = VGroup(derived_head, inherited_members).arrange(DOWN, buff=0.28)

        self.fit_to_box(base_content, 3.85, 2.95)
        self.fit_to_box(derived_content, 3.85, 2.95)

        base_group = VGroup(base_box, base_content).move_to(LEFT * 3.15 + DOWN * 0.35)
        derived_group = VGroup(derived_box, derived_content).move_to(RIGHT * 3.15 + DOWN * 0.35)

        inheritance_arrow = Arrow(
            base_group.get_right() + RIGHT * 0.12,
            derived_group.get_left() + LEFT * 0.12,
            buff=0.08,
            stroke_width=7,
        )

        access_tag = RoundedRectangle(width=3.3, height=0.62, corner_radius=0.12, stroke_width=2)
        access_text = Text("access without rewriting", font_size=22, weight=BOLD)
        self.fit_to_box(access_text, 3.0, 0.4)
        access_tag_group = VGroup(access_tag, access_text).next_to(inheritance_arrow, DOWN, buff=0.28)

        self.play(
            FadeOut(intro_title, shift=UP * 0.1),
            FadeOut(base[0]),
            FadeOut(derived[0]),
            FadeOut(naming_arrow),
        )
        self.play(FadeIn(how_title))
        self.play(FadeIn(base_group), FadeIn(derived_group))
        self.play(GrowArrow(inheritance_arrow))
        self.play(FadeIn(access_tag_group))
        self.play(
            Indicate(base_members, scale_factor=1.06),
            TransformFromCopy(base_members.copy(), inherited_members),
        )
        self.wait_for_narration(n3)
        self.scene_end("how")

        # =========================================================
        # 4. WHAT / WHY
        # =========================================================
        n4 = self.narrate(
            id="what_why",
            text="Every idea in this entire topic is built on correctly telling these two roles apart.",
            voice="default",
            subtitle=True,
        )

        self.scene_start("what_why")

        why_title = self.safe_title("First: Keep the Roles Distinct", width=9.5)
        why_title.to_edge(UP, buff=0.45)

        left_panel, left_box, _, left_body = self.card(
            "BASE CLASS",
            ["The class", "being inherited from"],
            width=4.8,
            height=2.7,
            title_size=31,
            body_size=25,
        )
        right_panel, right_box, _, right_body = self.card(
            "DERIVED CLASS",
            ["The new class", "that inherits"],
            width=4.8,
            height=2.7,
            title_size=31,
            body_size=25,
        )

        left_panel.move_to(LEFT * 3.1 + DOWN * 0.45)
        right_panel.move_to(RIGHT * 3.1 + DOWN * 0.45)

        role_arrow = Arrow(
            left_box.get_right() + RIGHT * 0.12,
            right_box.get_left() + LEFT * 0.12,
            buff=0.08,
            stroke_width=6,
        )

        foundation = Text("These two roles anchor the whole topic", font_size=28, weight=BOLD)
        self.fit_to_box(foundation, 8.8, 0.5)
        foundation.next_to(role_arrow, DOWN, buff=0.42)

        self.play(
            FadeOut(how_title, shift=UP * 0.1),
            FadeOut(base_group),
            FadeOut(derived_group),
            FadeOut(inheritance_arrow),
            FadeOut(access_tag_group),
        )
        self.play(FadeIn(why_title))
        self.play(FadeIn(left_panel), FadeIn(right_panel))
        self.play(GrowArrow(role_arrow), FadeIn(foundation))
        self.play(Indicate(left_box), Indicate(right_box))
        self.wait_for_narration(n4)
        self.scene_end("what_why")

        # =========================================================
        # 5. REAL-WORLD EXAMPLE
        # =========================================================
        n5 = self.narrate(
            id="real_world_example",
            text="A parent's family business, and the child who inherits it, continuing to use everything the parent already built.",
            voice="default",
            subtitle=True,
        )

        self.scene_start("real_world_example")

        ex_title = self.safe_title("Real-World Analogy: A Family Business", width=10.0)
        ex_title.to_edge(UP, buff=0.42)

        parent_card, parent_box, parent_head, parent_body = self.card(
            "PARENT",
            ["family business", "already built"],
            width=4.9,
            height=2.8,
            title_size=32,
            body_size=25,
        )
        child_card, child_box, child_head, child_body = self.card(
            "CHILD",
            ["inherits", "what already exists"],
            width=4.9,
            height=2.8,
            title_size=32,
            body_size=25,
        )

        parent_card.move_to(LEFT * 3.1 + DOWN * 0.5)
        child_card.move_to(RIGHT * 3.1 + DOWN * 0.5)

        business_flow = Arrow(
            parent_box.get_right() + RIGHT * 0.12,
            child_box.get_left() + LEFT * 0.12,
            buff=0.08,
            stroke_width=6,
        )

        received_tag = RoundedRectangle(width=3.25, height=0.66, corner_radius=0.12, stroke_width=2)
        received_text = Text("uses what was built", font_size=22, weight=BOLD)
        self.fit_to_box(received_text, 2.95, 0.42)
        received_group = VGroup(received_tag, received_text).next_to(business_flow, DOWN, buff=0.3)

        # Small "assets" strip: visualizes the inherited things without adding text overload.
        asset_row = VGroup(
            RoundedRectangle(width=1.0, height=0.72, corner_radius=0.12, stroke_width=2),
            RoundedRectangle(width=1.0, height=0.72, corner_radius=0.12, stroke_width=2),
            RoundedRectangle(width=1.0, height=0.72, corner_radius=0.12, stroke_width=2),
        ).arrange(RIGHT, buff=0.18)
        asset_row.next_to(parent_card, DOWN, buff=0.38)

        child_assets = asset_row.copy()
        child_assets.next_to(child_card, DOWN, buff=0.38)

        self.play(
            FadeOut(why_title, shift=UP * 0.1),
            FadeOut(left_panel),
            FadeOut(right_panel),
            FadeOut(role_arrow),
            FadeOut(foundation),
        )
        self.play(FadeIn(ex_title))
        self.play(FadeIn(parent_card), FadeIn(child_card))
        self.play(FadeIn(asset_row))
        self.play(GrowArrow(business_flow))
        self.play(FadeIn(received_group))
        self.play(TransformFromCopy(asset_row, child_assets))
        self.play(Indicate(parent_body), Indicate(child_body))
        self.wait_for_narration(n5)
        self.scene_end("real_world_example")

        # =========================================================
        # 6. SUMMARY
        # =========================================================
        n6 = self.narrate(
            id="summary",
            text="The base class is inherited from, and the derived class is the new class that inherits its members.",
            voice="default",
            subtitle=True,
        )

        self.scene_start("summary")

        summary_title = self.safe_title("Remember the Direction", width=8.5)
        summary_title.to_edge(UP, buff=0.45)

        base_summary, base_summary_box, _, _ = self.card(
            "BASE",
            ["inherited", "FROM"],
            width=4.2,
            height=2.35,
            title_size=33,
            body_size=26,
        )
        derived_summary, derived_summary_box, _, _ = self.card(
            "DERIVED",
            ["inherits", "MEMBERS"],
            width=4.2,
            height=2.35,
            title_size=33,
            body_size=26,
        )

        base_summary.move_to(LEFT * 2.7 + DOWN * 0.3)
        derived_summary.move_to(RIGHT * 2.7 + DOWN * 0.3)

        summary_arrow = Arrow(
            base_summary_box.get_right() + RIGHT * 0.15,
            derived_summary_box.get_left() + LEFT * 0.15,
            buff=0.08,
            stroke_width=7,
        )

        direction = Text("BASE  →  DERIVED", font_size=31, weight=BOLD)
        self.fit_to_box(direction, 6.0, 0.55)
        direction.next_to(summary_arrow, DOWN, buff=0.42)

        self.play(
            FadeOut(ex_title, shift=UP * 0.1),
            FadeOut(parent_card),
            FadeOut(child_card),
            FadeOut(asset_row),
            FadeOut(child_assets),
            FadeOut(business_flow),
            FadeOut(received_group),
        )
        self.play(FadeIn(summary_title))
        self.play(FadeIn(base_summary), FadeIn(derived_summary))
        self.play(GrowArrow(summary_arrow), FadeIn(direction))
        self.play(Indicate(base_summary_box), Indicate(derived_summary_box))
        self.wait_for_narration(n6)
        self.scene_end("summary")

        # =========================================================
        # 7. DONE
        # =========================================================
        n7 = self.narrate(
            id="done",
            text="Well done, my dear students. Now let us see exactly how this relationship is written in code. I will see you in the next video, for Syntax of Derivation.",
            voice="default",
            subtitle=True,
        )

        self.scene_start("done")

        done_title = self.safe_title("Next: Syntax of Derivation", width=9.2)
        done_title.to_edge(UP, buff=0.55)

        code_box = RoundedRectangle(
            width=10.2,
            height=3.25,
            corner_radius=0.18,
            stroke_width=3,
        )

        code_line_1 = Text("class Base { ... };", font_size=34, font="DejaVu Sans Mono")
        code_line_2 = Text("class Derived : public Base { ... };", font_size=34, font="DejaVu Sans Mono")
        self.fit_to_box(code_line_1, 9.2, 0.62)
        self.fit_to_box(code_line_2, 9.2, 0.62)

        code_group = VGroup(code_line_1, code_line_2).arrange(DOWN, buff=0.42)
        self.fit_to_box(code_group, 9.45, 2.45)
        code_group.move_to(code_box)

        self.play(
            FadeOut(summary_title, shift=UP * 0.1),
            FadeOut(base_summary),
            FadeOut(derived_summary),
            FadeOut(summary_arrow),
            FadeOut(direction),
        )
        self.play(FadeIn(done_title), FadeIn(code_box))
        self.play(FadeIn(code_group))
        self.wait_for_narration(n7)
        self.scene_end("done")
