from manim import *
from src.animation import LMSScene


class IntroductionToCodingDecoding(LMSScene):
    """
    C-CAT Preparation — Introduction to Coding-Decoding

    Manim-only lesson.
    The scene design deliberately uses adaptive sizing and conservative safe
    margins so generated text does not overflow its visual containers.
    """

    SAFE_X = 6.35
    SAFE_Y = 3.45

    # ------------------------------------------------------------------
    # Layout / safety helpers
    # ------------------------------------------------------------------

    def fit(self, mob, max_width=None, max_height=None, margin=0.0):
        if max_width is not None:
            target_w = max(0.1, max_width - 2 * margin)
            if mob.width > target_w:
                mob.scale_to_fit_width(target_w)

        if max_height is not None:
            target_h = max(0.1, max_height - 2 * margin)
            if mob.height > target_h:
                mob.scale_to_fit_height(target_h)

        return mob

    def title(self, text, width=12.0, font_size=42):
        t = Text(text, font_size=font_size, weight=BOLD)
        return self.fit(t, width, 0.65)

    def box_text(self, text, width, height, font_size=28, weight=NORMAL):
        t = Text(text, font_size=font_size, weight=weight)
        return self.fit(t, width, height)

    def rounded_card(
        self,
        heading,
        body_lines,
        width=4.8,
        height=2.7,
        heading_size=30,
        body_size=24,
    ):
        box = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.16,
            stroke_width=2.5,
        )

        head = Text(heading, font_size=heading_size, weight=BOLD)
        self.fit(head, width - 0.45, 0.55)

        body = Paragraph(
            *body_lines,
            alignment="center",
            font_size=body_size,
            line_spacing=0.85,
        )
        self.fit(body, width - 0.45, height - 0.95)

        content = VGroup(head, body).arrange(DOWN, buff=0.22)
        self.fit(content, width - 0.35, height - 0.30)
        return VGroup(box, content), box, head, body

    def letter_tile(self, letter, number=None, size=0.68, letter_size=28, number_size=17):
        tile = RoundedRectangle(
            width=size,
            height=size,
            corner_radius=0.08,
            stroke_width=1.8,
        )
        glyph = Text(letter, font_size=letter_size, weight=BOLD)
        self.fit(glyph, size - 0.16, size - 0.16)

        group = VGroup(tile, glyph)

        if number is not None:
            num = Text(str(number), font_size=number_size)
            self.fit(num, size - 0.12, 0.24)
            num.next_to(tile, DOWN, buff=0.08)
            group = VGroup(group, num)

        return group

    def alphabet_row(self, show_positions=False, tile_size=0.66):
        letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        tiles = VGroup(
            *[
                self.letter_tile(ch, i + 1 if show_positions else None, size=tile_size)
                for i, ch in enumerate(letters)
            ]
        )
        tiles.arrange(RIGHT, buff=0.045)
        self.fit(tiles, 12.5, 2.25)
        return tiles

    def word_row(self, word, font_size=38, buff=0.28):
        letters = VGroup(*[Text(ch, font_size=font_size, weight=BOLD) for ch in word])
        letters.arrange(RIGHT, buff=buff)
        self.fit(letters, 11.5, 0.95)
        return letters

    def labelled_arrow(self, start, end, label, label_size=25, color=None):
        arrow = Arrow(start, end, buff=0.10, stroke_width=4.5, color=color)
        tag = Text(label, font_size=label_size, weight=BOLD)
        self.fit(tag, 1.7, 0.42)
        tag.next_to(arrow, UP, buff=0.08)
        return arrow, tag

    def option_card(self, letter, value, width=2.35, height=0.78, size=27):
        box = RoundedRectangle(width=width, height=height, corner_radius=0.12, stroke_width=2)
        text = Text(f"({letter}) {value}", font_size=size)
        self.fit(text, width - 0.24, height - 0.18)
        return VGroup(box, text)

    def code_panel(self, lines, width=10.8, height=2.6, font_size=28):
        box = RoundedRectangle(width=width, height=height, corner_radius=0.18, stroke_width=2.5)
        code_lines = VGroup(
            *[
                Text(line, font_size=font_size, font="DejaVu Sans Mono")
                for line in lines
            ]
        ).arrange(DOWN, buff=0.22)
        self.fit(code_lines, width - 0.50, height - 0.38)
        code_lines.move_to(box)
        return VGroup(box, code_lines)

    def scene_title(self, text, width=12.0):
        t = self.title(text, width=width)
        t.to_edge(UP, buff=0.38)
        return t

    # ------------------------------------------------------------------
    # Lesson
    # ------------------------------------------------------------------

    def construct(self):
        self.camera.background_color = "#0B1020"

        # ==============================================================
        # 1. OPENING HOOK — message -> rule -> code -> decode
        # ==============================================================
        n1 = self.narrate(
            id="opening_hook",
            text=(
                "When you send a message on a modern messaging app, it does not travel across the internet "
                "as plain text. It is transformed by a rule into something unreadable. Only the receiver, "
                "who knows the rule, can turn it back into the original message. Now suppose you intercepted "
                "one such message, and you also knew what the original text was. Could you work out the rule? "
                "And once you had it, could you read the next message? That is exactly what a coding-decoding "
                "question asks you to do. The encryption is far simpler, of course, but the thinking process is the same."
            ),
            voice="default",
            subtitle=True,
        )
        self.scene_start("opening_hook")

        t = self.scene_title("A Message Goes In… A Code Comes Out", width=11.6)

        plain = RoundedRectangle(width=2.9, height=1.45, corner_radius=0.16, stroke_width=2.5)
        plain_word = Text("HELLO", font_size=38, weight=BOLD)
        self.fit(plain_word, 2.45, 0.62)
        plain_group = VGroup(plain, plain_word)

        rule_box = RoundedRectangle(width=2.5, height=1.45, corner_radius=0.16, stroke_width=2.5)
        rule_text = Text("RULE", font_size=33, weight=BOLD)
        self.fit(rule_text, 2.1, 0.55)
        rule_group = VGroup(rule_box, rule_text)

        coded = RoundedRectangle(width=2.9, height=1.45, corner_radius=0.16, stroke_width=2.5)
        coded_word = Text("IFMMP", font_size=38, weight=BOLD)
        self.fit(coded_word, 2.45, 0.62)
        coded_group = VGroup(coded, coded_word)

        plain_group.move_to(LEFT * 4.25 + DOWN * 0.25)
        rule_group.move_to(DOWN * 0.25)
        coded_group.move_to(RIGHT * 4.25 + DOWN * 0.25)

        a1 = Arrow(plain_group.get_right() + RIGHT * 0.10, rule_group.get_left() + LEFT * 0.10, buff=0.06, stroke_width=5)
        a2 = Arrow(rule_group.get_right() + RIGHT * 0.10, coded_group.get_left() + LEFT * 0.10, buff=0.06, stroke_width=5)

        reverse_note = Text("reverse the rule", font_size=25, weight=BOLD)
        self.fit(reverse_note, 3.1, 0.42)
        reverse_note.next_to(rule_group, DOWN, buff=0.50)

        back_arrow = CurvedArrow(
            coded_group.get_bottom() + DOWN * 0.15,
            plain_group.get_bottom() + DOWN * 0.15,
            angle=-PI / 2,
            stroke_width=4,
        )

        self.play(FadeIn(t))
        self.play(FadeIn(plain_group))
        self.play(GrowArrow(a1), FadeIn(rule_group))
        self.play(GrowArrow(a2), FadeIn(coded_group))
        self.play(Create(back_arrow), FadeIn(reverse_note))
        self.wait_for_narration(n1)
        self.scene_end("opening_hook")

        # ==============================================================
        # 2. CONCEPT INTRODUCTION — vocabulary
        # ==============================================================
        n2 = self.narrate(
            id="concept_introduction",
            text=(
                "Let's set up the vocabulary we'll use in every lesson of this chapter. "
                "The original word is the meaningful word we start with, for example, CAT. "
                "The code word is what that word becomes after a transformation, for example, DBU. "
                "The coding rule is the fixed logic that turns the original word into the code word. "
                "Coding means applying the rule to get the code word. Decoding means reversing the rule "
                "to recover the original word. In a coding-decoding question, you are usually given one "
                "or more pairs of original and code words. From them you must find the rule, and then apply "
                "it to a new word. So, formally: coding-decoding is a reasoning task in which you identify "
                "the systematic rule that transforms given information into a coded form, and then apply "
                "that rule consistently to new information. The key word is systematic. A valid coding rule "
                "applies the same way to every letter, or follows a clear pattern across positions. If a rule "
                "works for one letter but not the next, it is not the rule."
            ),
            voice="default",
            subtitle=True,
        )
        self.scene_start("concept_introduction")

        t2 = self.scene_title("The Vocabulary")

        original, _, _, _ = self.rounded_card("ORIGINAL WORD", ["The word we", "start with"], width=2.8, height=2.25, heading_size=27, body_size=22)
        coded, _, _, _ = self.rounded_card("CODE WORD", ["The transformed", "word"], width=2.8, height=2.25, heading_size=27, body_size=22)
        rule, _, _, _ = self.rounded_card("CODING RULE", ["The fixed logic", "of transformation"], width=2.8, height=2.25, heading_size=27, body_size=22)
        process, _, _, _ = self.rounded_card("CODING ↔ DECODING", ["Apply the rule", "or reverse it"], width=3.15, height=2.25, heading_size=25, body_size=22)

        cards = VGroup(original, coded, rule, process).arrange(RIGHT, buff=0.28)
        cards.move_to(DOWN * 0.20)
        self.fit(cards, 12.6, 3.0)

        pair = VGroup(
            Text("CAT", font_size=32, weight=BOLD),
            Text("→", font_size=35, weight=BOLD),
            Text("DBU", font_size=32, weight=BOLD),
        ).arrange(RIGHT, buff=0.22)
        pair.next_to(cards, DOWN, buff=0.50)

        systematic = Text("SYSTEMATIC = the same logic must keep working", font_size=27, weight=BOLD)
        self.fit(systematic, 10.8, 0.50)
        systematic.to_edge(DOWN, buff=0.40)

        self.play(
            FadeOut(t),
            FadeOut(plain_group),
            FadeOut(rule_group),
            FadeOut(coded_group),
            FadeOut(a1),
            FadeOut(a2),
            FadeOut(back_arrow),
            FadeOut(reverse_note),
        )
        self.play(FadeIn(t2))
        self.play(LaggedStart(*[FadeIn(c) for c in cards], lag_ratio=0.14))
        self.play(FadeIn(pair), FadeIn(systematic))
        self.play(Indicate(pair, scale_factor=1.05))
        self.wait_for_narration(n2)
        self.scene_end("concept_introduction")

        # ==============================================================
        # 3. CORE EXPLANATION — five forms
        # ==============================================================
        n3 = self.narrate(
            id="core_explanation",
            text=(
                "Coding rules come in several forms. Later in this lesson, we'll study each one separately: "
                "Letter coding: letters are replaced by other letters. Number coding: letters or words are "
                "represented by numbers. Symbol coding: letters or digits are replaced by symbols. "
                "Substitution coding: one word is called by another word's name. Mixed coding: words in a "
                "sentence share codes, and you must match them. All of these depend on one skill: fast, accurate "
                "handling of the alphabet. So before we solve anything, let's build the toolkit."
            ),
            voice="default",
            subtitle=True,
        )
        self.scene_start("core_explanation")

        t3 = self.scene_title("Five Common Forms of Coding")

        labels = [
            ("LETTER", "letters → letters"),
            ("NUMBER", "letters → numbers"),
            ("SYMBOL", "letters → symbols"),
            ("SUBSTITUTION", "word → another word"),
            ("MIXED", "match shared codes"),
        ]

        cards3 = VGroup()
        for heading, body in labels:
            c, _, _, _ = self.rounded_card(
                heading,
                [body],
                width=2.22,
                height=2.45,
                heading_size=25,
                body_size=20,
            )
            cards3.add(c)

        cards3.arrange(RIGHT, buff=0.16)
        self.fit(cards3, 12.65, 2.85)
        cards3.move_to(DOWN * 0.15)

        toolkit = RoundedRectangle(width=9.6, height=1.05, corner_radius=0.16, stroke_width=2)
        toolkit_text = Text("All five depend on one toolkit: fast, accurate alphabet handling", font_size=27, weight=BOLD)
        self.fit(toolkit_text, 9.1, 0.72)
        VGroup(toolkit, toolkit_text).move_to(DOWN * 2.55)

        self.play(FadeOut(t2), FadeOut(cards), FadeOut(pair), FadeOut(systematic))
        self.play(FadeIn(t3))
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.15) for c in cards3], lag_ratio=0.12))
        self.play(FadeIn(toolkit), FadeIn(toolkit_text))
        self.wait_for_narration(n3)
        self.scene_end("core_explanation")

        # ==============================================================
        # 4. TOOL 1 — positions + anchors
        # ==============================================================
        n4 = self.narrate(
            id="tool_1_positions",
            text=(
                "Tool 1: Positions. Each letter has a position from 1 to 26. A is 1, B is 2, and so on up "
                "to Z at 26. You shouldn't count on your fingers in the exam. Use anchor letters instead. "
                "Remember E-J-O-T-Y: E is 5, J is 10, O is 15, T is 20, Y is 25. From any anchor, you are "
                "at most two steps from your target letter. For example, R is two before T, so R is 18."
            ),
            voice="default",
            subtitle=True,
        )
        self.scene_start("tool_1_positions")

        t4 = self.scene_title("Tool 1 — Letter Positions", width=10.8)
        row = self.alphabet_row(show_positions=True, tile_size=0.62)
        row.to_edge(DOWN, buff=1.18)

        anchor_letters = {"E", "J", "O", "T", "Y"}
        anchor_marks = VGroup()
        for tile in row:
            letter = tile[1].text if hasattr(tile[1], "text") else ""
            # Use position index instead of depending on internal Text text access.
        # Explicitly locate anchor indices: E=4, J=9, O=14, T=19, Y=24.
        for idx in [4, 9, 14, 19, 24]:
            tile = row[idx]
            mark = SurroundingRectangle(tile, buff=0.04, stroke_width=3)
            anchor_marks.add(mark)

        anchor_strip = RoundedRectangle(width=6.0, height=0.85, corner_radius=0.14, stroke_width=2)
        anchor_text = Text("E(5)   J(10)   O(15)   T(20)   Y(25)", font_size=29, weight=BOLD)
        self.fit(anchor_text, 5.55, 0.55)
        VGroup(anchor_strip, anchor_text).to_edge(UP, buff=1.10)

        r_demo = Text("R = two before T = 18", font_size=29, weight=BOLD)
        self.fit(r_demo, 5.4, 0.5)
        r_demo.move_to(DOWN * 1.30)

        self.play(FadeOut(t3), FadeOut(cards3), FadeOut(toolkit), FadeOut(toolkit_text))
        self.play(FadeIn(t4), FadeIn(row), FadeIn(anchor_strip), FadeIn(anchor_text))
        self.play(LaggedStart(*[Create(m) for m in anchor_marks], lag_ratio=0.10))
        self.play(FadeIn(r_demo))
        self.wait_for_narration(n4)
        self.scene_end("tool_1_positions")

        # ==============================================================
        # 5. TOOL 2 — opposite letters
        # ==============================================================
        n5 = self.narrate(
            id="tool_2_opposites",
            text=(
                "Tool 2: Opposite letters. If you fold the alphabet in half, A pairs with Z, B with Y, "
                "C with X, and so on down to M with N. Every opposite pair has positions that add up to 27. "
                "So the opposite of G, position 7, is at position 20, which is T."
            ),
            voice="default",
            subtitle=True,
        )
        self.scene_start("tool_2_opposites")

        t5 = self.scene_title("Tool 2 — Opposite Letters", width=10.6)

        top = self.alphabet_row(show_positions=False, tile_size=0.60)
        bottom_letters = "ZYXWVUTSRQPONMLKJIHGFEDCBA"
        bottom = VGroup(*[Text(ch, font_size=26, weight=BOLD) for ch in bottom_letters])
        bottom.arrange(RIGHT, buff=0.075)
        self.fit(bottom, 12.3, 0.65)

        top.to_edge(UP, buff=1.30)
        bottom.move_to(DOWN * 0.55)

        pairing_lines = VGroup()
        for i in range(26):
            x1 = top[i].get_bottom()
            x2 = bottom[i].get_top()
            pairing_lines.add(Line(x1, x2, stroke_width=1.5))

        equation_box = RoundedRectangle(width=6.0, height=1.0, corner_radius=0.15, stroke_width=2.2)
        equation = Text("position + opposite position = 27", font_size=30, weight=BOLD)
        self.fit(equation, 5.6, 0.66)
        VGroup(equation_box, equation).move_to(DOWN * 2.55)

        g_demo = Text("G = 7   →   T = 20", font_size=30, weight=BOLD)
        self.fit(g_demo, 4.7, 0.52)
        g_demo.next_to(equation_box, UP, buff=0.32)

        self.play(FadeOut(t4), FadeOut(row), FadeOut(anchor_strip), FadeOut(anchor_text), FadeOut(anchor_marks), FadeOut(r_demo))
        self.play(FadeIn(t5), FadeIn(top), FadeIn(bottom))
        self.play(LaggedStart(*[Create(line) for line in pairing_lines], lag_ratio=0.035))
        self.play(FadeIn(equation_box), FadeIn(equation), FadeIn(g_demo))
        self.wait_for_narration(n5)
        self.scene_end("tool_2_opposites")

        # ==============================================================
        # 6. TOOL 3 — circular alphabet
        # ==============================================================
        n6 = self.narrate(
            id="tool_3_circular",
            text=(
                "Tool 3: The alphabet is circular. Suppose the rule is 'move forward by 2' and the letter "
                "is Y. You go to Z, and then wrap back to A. In position terms: if a result goes above 26, subtract 26."
            ),
            voice="default",
            subtitle=True,
        )
        self.scene_start("tool_3_circular")

        t6 = self.scene_title("Tool 3 — The Alphabet Is Circular", width=11.0)

        circle = Circle(radius=2.15, stroke_width=3)
        circle.shift(UP * 0.05)

        circle_letters = VGroup()
        for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            angle = PI / 2 - TAU * i / 26
            p = circle.get_center() + 2.65 * np.array([np.cos(angle), np.sin(angle), 0])
            glyph = Text(ch, font_size=25, weight=BOLD)
            self.fit(glyph, 0.48, 0.48)
            glyph.move_to(p)
            circle_letters.add(glyph)

        y_pos = circle_letters[24].get_center()
        z_pos = circle_letters[25].get_center()
        a_pos = circle_letters[0].get_center()

        y_dot = Dot(y_pos, radius=0.09)
        z_dot = Dot(z_pos, radius=0.09)
        a_dot = Dot(a_pos, radius=0.09)

        y_label = Text("Y", font_size=28, weight=BOLD).next_to(y_dot, OUT, buff=0.18)
        move_label = Text("+2", font_size=29, weight=BOLD)
        self.fit(move_label, 0.8, 0.45)
        move_label.move_to(circle.get_center() + RIGHT * 3.45)

        wrap = CurvedArrow(
            y_dot.get_center() + UP * 0.10,
            a_dot.get_center() + LEFT * 0.05,
            angle=-PI / 2.5,
            stroke_width=4.5,
        )

        math_box = RoundedRectangle(width=5.9, height=1.15, corner_radius=0.15, stroke_width=2.3)
        math_text = Text("25 + 2 = 27 → 27 − 26 = 1 → A", font_size=27, weight=BOLD)
        self.fit(math_text, 5.45, 0.72)
        VGroup(math_box, math_text).move_to(DOWN * 2.70)

        self.play(FadeOut(t5), FadeOut(top), FadeOut(bottom), FadeOut(pairing_lines), FadeOut(equation_box), FadeOut(equation), FadeOut(g_demo))
        self.play(FadeIn(t6), FadeIn(circle), FadeIn(circle_letters))
        self.play(FadeIn(y_dot), FadeIn(z_dot), FadeIn(a_dot))
        self.play(FadeIn(y_label), FadeIn(move_label))
        self.play(Create(wrap))
        self.play(FadeIn(math_box), FadeIn(math_text))
        self.wait_for_narration(n6)
        self.scene_end("tool_3_circular")

        # ==============================================================
        # 7. METHOD — compare letter by letter
        # ==============================================================
        n7 = self.narrate(
            id="method",
            text=(
                "With these three tools, the method is always the same. Compare each letter of the original "
                "word with the matching letter of the code word, and measure the change."
            ),
            voice="default",
            subtitle=True,
        )
        self.scene_start("method")

        t7 = self.scene_title("The Method: Compare, Measure, Apply", width=11.2)

        original = self.word_row("CAT")
        coded = self.word_row("DBU")
        original.move_to(LEFT * 2.5 + UP * 0.85)
        coded.move_to(LEFT * 2.5 + DOWN * 0.25)

        arrows = VGroup()
        pluses = VGroup()
        for i in range(3):
            arr, lab = self.labelled_arrow(
                original[i].get_bottom() + DOWN * 0.05,
                coded[i].get_top() + UP * 0.05,
                "+1",
                label_size=23,
            )
            arrows.add(arr)
            pluses.add(lab)

        compare_box = RoundedRectangle(width=5.0, height=2.8, corner_radius=0.18, stroke_width=2.4)
        compare_lines = VGroup(
            Text("C(3) → D(4)  = +1", font_size=24),
            Text("A(1) → B(2)  = +1", font_size=24),
            Text("T(20) → U(21) = +1", font_size=24),
        ).arrange(DOWN, buff=0.18)
        self.fit(compare_lines, 4.55, 2.2)
        compare_lines.move_to(compare_box)
        compare_group = VGroup(compare_box, compare_lines)
        compare_group.move_to(RIGHT * 3.55 + DOWN * 0.15)

        systematic = Text("Check the entire word before trusting the rule.", font_size=29, weight=BOLD)
        self.fit(systematic, 10.2, 0.52)
        systematic.to_edge(DOWN, buff=0.42)

        self.play(FadeOut(t6), FadeOut(circle), FadeOut(circle_letters), FadeOut(y_dot), FadeOut(z_dot), FadeOut(a_dot), FadeOut(y_label), FadeOut(move_label), FadeOut(wrap), FadeOut(math_box), FadeOut(math_text))
        self.play(FadeIn(t7), FadeIn(original), FadeIn(coded))
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.14))
        self.play(FadeIn(pluses))
        self.play(FadeIn(compare_group), FadeIn(systematic))
        self.wait_for_narration(n7)
        self.scene_end("method")

        # ==============================================================
        # 8. EXAMPLE 1 — CAT -> DBU, DOG -> EPH
        # ==============================================================
        n8 = self.narrate(
            id="example_1",
            text=(
                "Example 1: Basic. If CAT is coded as DBU, how is DOG coded? Compare the words letter by letter. "
                "C, position 3, becomes D, position 4. That is +1. A, position 1, becomes B, position 2. That is +1. "
                "T, position 20, becomes U, position 21. That is +1. The rule holds for every letter: move each letter "
                "one step forward. Apply it to DOG. D becomes E, O becomes P, G becomes H. DOG is coded as EPH. "
                "Notice that we checked the rule on all three letters before using it. That habit will save you from traps later."
            ),
            voice="default",
            subtitle=True,
        )
        self.scene_start("example_1")

        t8 = self.scene_title("Example 1 — Find the Rule, Then Apply It", width=11.4)

        prompt_box = RoundedRectangle(width=5.0, height=0.95, corner_radius=0.14, stroke_width=2)
        prompt = Text("CAT  →  DBU", font_size=35, weight=BOLD)
        self.fit(prompt, 4.5, 0.60)
        VGroup(prompt_box, prompt).move_to(LEFT * 3.35 + UP * 2.0)

        cat = self.word_row("CAT", font_size=38)
        dbu = self.word_row("DBU", font_size=38)
        cat.move_to(LEFT * 3.35 + UP * 0.90)
        dbu.move_to(LEFT * 3.35 + DOWN * 0.20)

        local_arrows = VGroup()
        local_labels = VGroup()
        for i in range(3):
            arr, lab = self.labelled_arrow(
                cat[i].get_bottom() + DOWN * 0.04,
                dbu[i].get_top() + UP * 0.04,
                "+1",
                label_size=22,
            )
            local_arrows.add(arr)
            local_labels.add(lab)

        apply_box = RoundedRectangle(width=5.9, height=3.35, corner_radius=0.18, stroke_width=2.5)
        dog = Text("DOG", font_size=40, weight=BOLD)
        eph = Text("EPH", font_size=40, weight=BOLD)
        self.fit(dog, 4.8, 0.62)
        self.fit(eph, 4.8, 0.62)

        d1 = Text("D → E", font_size=26)
        d2 = Text("O → P", font_size=26)
        d3 = Text("G → H", font_size=26)
        steps = VGroup(d1, d2, d3).arrange(DOWN, buff=0.13)
        self.fit(steps, 4.6, 1.55)

        apply_content = VGroup(
            dog,
            Text("+1 each letter", font_size=25, weight=BOLD),
            steps,
            Text("Answer: EPH", font_size=29, weight=BOLD),
        ).arrange(DOWN, buff=0.18)
        self.fit(apply_content, 5.45, 2.95)
        apply_content.move_to(apply_box)
        apply_group = VGroup(apply_box, apply_content).move_to(RIGHT * 3.25 + DOWN * 0.25)

        self.play(FadeOut(t7), FadeOut(original), FadeOut(coded), FadeOut(arrows), FadeOut(pluses), FadeOut(compare_group), FadeOut(systematic))
        self.play(FadeIn(t8), FadeIn(prompt_box), FadeIn(prompt), FadeIn(cat), FadeIn(dbu))
        self.play(LaggedStart(*[GrowArrow(a) for a in local_arrows], lag_ratio=0.12))
        self.play(FadeIn(local_labels))
        self.play(FadeIn(apply_group))
        self.play(Indicate(eph, scale_factor=1.06))
        self.wait_for_narration(n8)
        self.scene_end("example_1")

        # ==============================================================
        # 9. APPLICATION — computing connections
        # ==============================================================
        n9 = self.narrate(
            id="application",
            text=(
                "Is this only an exam puzzle? Not really. The rule in Example 1 is a simple form of the Caesar "
                "cipher, one of the oldest known encryption techniques. Each letter is shifted by a fixed number "
                "of positions. The underlying idea, that information can be transformed by a rule and recovered "
                "by reversing it, runs through computing: Character encoding: your computer stores the letter A "
                "as the number 65 in ASCII. Encryption: secure communication uses far more complex transformation "
                "rules. Data compression: files are re-encoded into smaller representations. So when you practise "
                "coding-decoding, you're training the same pattern-detection skill that underlies how information "
                "is represented and protected. That's one reason this topic appears in C-CAT."
            ),
            voice="default",
            subtitle=True,
        )
        self.scene_start("application")

        t9 = self.scene_title("The Same Idea Appears in Computing", width=11.8)

        panels = VGroup()
        app_data = [
            ("ASCII", "A  →  65"),
            ("ENCRYPTION", "message  →  code"),
            ("COMPRESSION", "file  →  smaller form"),
        ]
        for head, body in app_data:
            p, _, _, _ = self.rounded_card(
                head,
                [body],
                width=3.55,
                height=2.55,
                heading_size=27,
                body_size=22,
            )
            panels.add(p)

        panels.arrange(RIGHT, buff=0.32)
        panels.move_to(UP * 0.05)
        self.fit(panels, 11.9, 2.9)

        bridge = Arrow(
            panels[0].get_right() + RIGHT * 0.12,
            panels[1].get_left() + LEFT * 0.12,
            buff=0.10,
            stroke_width=2.5,
        )
        bridge2 = Arrow(
            panels[1].get_right() + RIGHT * 0.12,
            panels[2].get_left() + LEFT * 0.12,
            buff=0.10,
            stroke_width=2.5,
        )

        core = RoundedRectangle(width=9.8, height=1.05, corner_radius=0.15, stroke_width=2.2)
        core_text = Text("Transform information with a rule → represent → recover or reconstruct", font_size=27, weight=BOLD)
        self.fit(core_text, 9.35, 0.68)
        VGroup(core, core_text).move_to(DOWN * 2.45)

        self.play(FadeOut(t8), FadeOut(prompt_box), FadeOut(prompt), FadeOut(cat), FadeOut(dbu), FadeOut(local_arrows), FadeOut(local_labels), FadeOut(apply_group))
        self.play(FadeIn(t9))
        self.play(LaggedStart(*[FadeIn(p) for p in panels], lag_ratio=0.16))
        self.play(Create(bridge), Create(bridge2))
        self.play(FadeIn(core), FadeIn(core_text))
        self.wait_for_narration(n9)
        self.scene_end("application")

        # ==============================================================
        # 10. EXAM-ORIENTED — MONKEY -> XDJMNL; TIGER -> QDFHS
        # ==============================================================
        n10 = self.narrate(
            id="exam_oriented",
            text=(
                "Example 3: Exam-oriented. In a certain code, MONKEY is written as XDJMNL. How is TIGER written "
                "in that code? (a) UJHFS (b) QDFHS (c) SHFDQ (d) QDFGS. Let's apply the method. Step 1: Check the length. "
                "MONKEY has six letters, and so does XDJMNL. So each letter probably maps to one letter. Step 2: Compare "
                "the first letters. M becomes X. That's a jump of +11, which is unusual. When a direct comparison looks "
                "strange, check whether the word has been reversed. Step 3: Reverse the original word. MONKEY reversed "
                "is YEKNOM. Now compare YEKNOM with XDJMNL: every letter moves −1. The rule is: reverse the word, then "
                "move each letter one step back. It works for all six letters. Step 4: Apply it to TIGER. Reversed, TIGER "
                "is REGIT. Moving each letter back one step gives QDFHS. The answer is (b). Now look at why the other options "
                "exist. Each one is a deliberate trap. (a) uses +1 with no reversal. (c) moves −1 but forgets reversal. "
                "(d) uses reversal and direction correctly but miscounts I − 1 as G instead of H. Time-saving tip: you often "
                "don't need to code the whole word. Once you know the first letter must be Q, options (a) and (c) are gone. "
                "Checking one more letter separates (b) from (d)."
            ),
            voice="default",
            subtitle=True,
        )
        self.scene_start("exam_oriented")

        t10 = self.scene_title("Exam Example — Spot the Hidden Transformation", width=12.0)

        qbox = RoundedRectangle(width=8.8, height=1.25, corner_radius=0.15, stroke_width=2.3)
        qtext = Text("MONKEY  →  XDJMNL     |     TIGER  →  ?", font_size=30, weight=BOLD)
        self.fit(qtext, 8.35, 0.78)
        VGroup(qbox, qtext).move_to(UP * 2.05)

        opts = VGroup(
            self.option_card("a", "UJHFS"),
            self.option_card("b", "QDFHS"),
            self.option_card("c", "SHFDQ"),
            self.option_card("d", "QDFGS"),
        ).arrange(RIGHT, buff=0.18)
        self.fit(opts, 10.5, 1.0)
        opts.move_to(DOWN * 2.45)

        check = VGroup(
            Text("1. Same length", font_size=25, weight=BOLD),
            Text("2. Direct shift looks irregular", font_size=25, weight=BOLD),
            Text("3. Try reversal", font_size=25, weight=BOLD),
            Text("4. Reverse +1 step back", font_size=25, weight=BOLD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.13)
        self.fit(check, 5.65, 2.45)
        check.move_to(LEFT * 3.55 + DOWN * 0.10)

        transform_box = RoundedRectangle(width=5.2, height=2.75, corner_radius=0.18, stroke_width=2.4)
        rev = Text("MONKEY", font_size=31, weight=BOLD)
        rev_arrow = Text("↓ reverse", font_size=24, weight=BOLD)
        reversed_word = Text("YEKNOM", font_size=31, weight=BOLD)
        step = Text("−1 each letter", font_size=26, weight=BOLD)
        answer = Text("TIGER → REGIT → QDFHS", font_size=25, weight=BOLD)
        for m, w, h in [
            (rev, 4.6, 0.52),
            (rev_arrow, 2.5, 0.40),
            (reversed_word, 4.6, 0.52),
            (step, 4.0, 0.45),
            (answer, 4.65, 0.48),
        ]:
            self.fit(m, w, h)
        transform_content = VGroup(rev, rev_arrow, reversed_word, step, answer).arrange(DOWN, buff=0.12)
        self.fit(transform_content, 4.85, 2.4)
        transform_content.move_to(transform_box)
        transform_group = VGroup(transform_box, transform_content).move_to(RIGHT * 3.55 + DOWN * 0.05)

        self.play(FadeOut(t9), FadeOut(panels), FadeOut(bridge), FadeOut(bridge2), FadeOut(core), FadeOut(core_text))
        self.play(FadeIn(t10), FadeIn(qbox), FadeIn(qtext), FadeIn(opts))
        self.play(FadeIn(check), FadeIn(transform_group))
        self.play(Indicate(opts[1], scale_factor=1.05))
        self.wait_for_narration(n10)
        self.scene_end("exam_oriented")

        # ==============================================================
        # 11. EXAM ROUTINE — five-step flow
        # ==============================================================
        n11 = self.narrate(
            id="exam_routine",
            text=(
                "So the general exam routine is: Compare lengths. Compare letter by letter and measure the change. "
                "If the change looks irregular, check reversal and opposite letters. Verify the rule on every letter. "
                "Apply the rule to the new word, and use early letters to eliminate options."
            ),
            voice="default",
            subtitle=True,
        )
        self.scene_start("exam_routine")

        t11 = self.scene_title("Five-Step Exam Routine", width=10.8)

        steps = [
            "Compare lengths",
            "Measure the change",
            "Check reversal / opposites",
            "Verify every letter",
            "Apply + eliminate",
        ]

        nodes = VGroup()
        for i, label in enumerate(steps, start=1):
            c, _, _, _ = self.rounded_card(
                f"STEP {i}",
                [label],
                width=2.30,
                height=2.15,
                heading_size=25,
                body_size=20,
            )
            nodes.add(c)

        nodes.arrange(RIGHT, buff=0.12)
        self.fit(nodes, 12.5, 2.55)
        nodes.move_to(DOWN * 0.15)

        arrows = VGroup()
        for i in range(4):
            arrows.add(
                Arrow(
                    nodes[i].get_right(),
                    nodes[i + 1].get_left(),
                    buff=0.07,
                    stroke_width=3,
                )
            )

        self.play(FadeOut(t10), FadeOut(qbox), FadeOut(qtext), FadeOut(opts), FadeOut(check), FadeOut(transform_group))
        self.play(FadeIn(t11))
        self.play(LaggedStart(*[FadeIn(n) for n in nodes], lag_ratio=0.10))
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.12))
        self.wait_for_narration(n11)
        self.scene_end("exam_routine")

        # ==============================================================
        # 12. COMMON MISTAKES
        # ==============================================================
        n12 = self.narrate(
            id="common_mistakes",
            text=(
                "Three mistakes account for most wrong answers in this topic. Mistake 1: Deciding the rule from a "
                "single letter. If C becomes D, the rule might be +1. But it might also be a pattern like +1, +2, +3 "
                "across positions. Always confirm with every letter. Mistake 2: Ignoring the circular alphabet. Y plus "
                "2 is not position 27. It wraps around to A. Subtract 26 whenever you go past Z. Mistake 3: Mixing up "
                "the direction when decoding. If coding means +2, then decoding means −2. Under time pressure, candidates "
                "often apply the coding rule again instead of reversing it."
            ),
            voice="default",
            subtitle=True,
        )
        self.scene_start("common_mistakes")

        t12 = self.scene_title("Three Common Mistakes", width=10.5)

        mistake_data = [
            ("1", "Verify every letter"),
            ("2", "Z wraps to A"),
            ("3", "Decode = reverse the rule"),
        ]

        mistake_cards = VGroup()
        for num, body in mistake_data:
            c, _, _, _ = self.rounded_card(
                f"MISTAKE {num}",
                [body],
                width=3.65,
                height=2.55,
                heading_size=27,
                body_size=22,
            )
            mistake_cards.add(c)

        mistake_cards.arrange(RIGHT, buff=0.35)
        self.fit(mistake_cards, 11.8, 2.9)
        mistake_cards.move_to(DOWN * 0.10)

        detail = RoundedRectangle(width=10.5, height=1.00, corner_radius=0.14, stroke_width=2.2)
        detail_text = Text("Don't trust a pattern until every required letter agrees.", font_size=28, weight=BOLD)
        self.fit(detail_text, 10.1, 0.65)
        VGroup(detail, detail_text).move_to(DOWN * 2.55)

        self.play(FadeOut(t11), FadeOut(nodes), FadeOut(arrows))
        self.play(FadeIn(t12))
        self.play(LaggedStart(*[FadeIn(c) for c in mistake_cards], lag_ratio=0.15))
        self.play(FadeIn(detail), FadeIn(detail_text))
        self.wait_for_narration(n12)
        self.scene_end("common_mistakes")

        # ==============================================================
        # 13. PRACTICE QUESTION — intentional pause
        # ==============================================================
        n13 = self.narrate(
            id="practice_question",
            text=(
                "Try this one yourself. If ROSE is coded as TQUG, how is LILY coded? "
                "Compare the letters, find the rule, check it on every letter, and apply it. Watch the last letter carefully."
            ),
            voice="default",
            subtitle=True,
        )
        self.scene_start("practice_question")

        t13 = self.scene_title("Practice — Your Turn", width=9.5)

        practice_box = RoundedRectangle(width=10.7, height=2.25, corner_radius=0.18, stroke_width=2.7)
        p1 = Text("ROSE  →  TQUG", font_size=39, weight=BOLD)
        p2 = Text("LILY  →  ?", font_size=43, weight=BOLD)
        self.fit(p1, 9.7, 0.72)
        self.fit(p2, 9.7, 0.72)
        practice_content = VGroup(p1, p2).arrange(DOWN, buff=0.30)
        practice_content.move_to(practice_box)

        instruction = Text("Compare → find the rule → verify → apply", font_size=28, weight=BOLD)
        self.fit(instruction, 8.8, 0.55)
        instruction.to_edge(DOWN, buff=0.75)

        pause = Text("PAUSE", font_size=34, weight=BOLD)
        self.fit(pause, 3.0, 0.55)
        pause.to_edge(DOWN, buff=0.25)

        self.play(FadeOut(t12), FadeOut(mistake_cards), FadeOut(detail), FadeOut(detail_text))
        self.play(FadeIn(t13), FadeIn(practice_box), FadeIn(practice_content))
        self.play(FadeIn(instruction), FadeIn(pause))
        self.wait_for_narration(n13)
        self.wait(2)
        self.scene_end("practice_question")

        # ==============================================================
        # 14. ANSWER — ROSE -> TQUG; LILY -> NKNA
        # ==============================================================
        n14 = self.narrate(
            id="answer_explanation",
            text=(
                "Compare ROSE with TQUG: R, position 18, to T, position 20 is +2. O, position 15, to Q, position 17 "
                "is +2. S, position 19, to U, position 21 is +2. E, position 5, to G, position 7 is +2. The rule is: "
                "move each letter two steps forward. Apply it to LILY. L becomes N, I becomes K, and the second L becomes N. "
                "Now the last letter, Y. Its position is 25, and 25 + 2 = 27. That is beyond Z, so subtract 26 to get "
                "position 1, which is A. LILY is coded as NKNA. If you wrote something odd for the last letter, you've just "
                "met the wrap-around trap. It's better to meet it here than in the exam."
            ),
            voice="default",
            subtitle=True,
        )
        self.scene_start("answer_explanation")

        t14 = self.scene_title("Answer — Watch the Final Letter", width=10.8)

        source_word = self.word_row("ROSE", font_size=34)
        target_word = self.word_row("TQUG", font_size=34)
        source_word.move_to(LEFT * 3.6 + UP * 1.55)
        target_word.move_to(LEFT * 3.6 + DOWN * 0.05)

        step_arrows = VGroup()
        step_labels = VGroup()
        for i in range(4):
            arr, lab = self.labelled_arrow(
                source_word[i].get_bottom() + DOWN * 0.04,
                target_word[i].get_top() + UP * 0.04,
                "+2",
                label_size=20,
            )
            step_arrows.add(arr)
            step_labels.add(lab)

        lily = self.word_row("LILY", font_size=38)
        nkna = self.word_row("NKNA", font_size=38)
        lily.move_to(RIGHT * 3.45 + UP * 1.55)
        nkna.move_to(RIGHT * 3.45 + DOWN * 0.05)

        lily_arrows = VGroup()
        lily_labels = VGroup()
        for i in range(4):
            label = "+2"
            arr, lab = self.labelled_arrow(
                lily[i].get_bottom() + DOWN * 0.04,
                nkna[i].get_top() + UP * 0.04,
                label,
                label_size=20,
            )
            lily_arrows.add(arr)
            lily_labels.add(lab)

        wrap_box = RoundedRectangle(width=5.55, height=1.12, corner_radius=0.14, stroke_width=2.4)
        wrap_text = Text("Y(25) + 2 = 27 → 1 → A", font_size=28, weight=BOLD)
        self.fit(wrap_text, 5.15, 0.72)
        VGroup(wrap_box, wrap_text).move_to(DOWN * 2.48)

        answer = Text("LILY → NKNA", font_size=34, weight=BOLD)
        self.fit(answer, 4.7, 0.55)
        answer.next_to(wrap_box, UP, buff=0.30)

        self.play(FadeOut(t13), FadeOut(practice_box), FadeOut(practice_content), FadeOut(instruction), FadeOut(pause))
        self.play(FadeIn(t14))
        self.play(FadeIn(source_word), FadeIn(target_word))
        self.play(LaggedStart(*[GrowArrow(a) for a in step_arrows], lag_ratio=0.10))
        self.play(FadeIn(step_labels))
        self.play(FadeIn(lily), FadeIn(nkna))
        self.play(LaggedStart(*[GrowArrow(a) for a in lily_arrows], lag_ratio=0.10))
        self.play(FadeIn(lily_labels))
        self.play(FadeIn(wrap_box), FadeIn(wrap_text), FadeIn(answer))
        self.play(Indicate(nkna[3], scale_factor=1.12))
        self.wait_for_narration(n14)
        self.scene_end("answer_explanation")

        # ==============================================================
        # 15. QUICK REVISION
        # ==============================================================
        n15 = self.narrate(
            id="quick_revision",
            text=(
                "Let's summarise. Coding-decoding means finding a coding rule from given pairs of original and code words, "
                "then applying it consistently. Know your letter positions. Use the E-J-O-T-Y anchors: 5, 10, 15, 20, 25. "
                "Opposite letters have positions that add up to 27. The alphabet is circular: after Z comes A. "
                "The method is: compare lengths, compare letter by letter, check for reversal or opposite letters, verify "
                "on every letter, then apply and eliminate."
            ),
            voice="default",
            subtitle=True,
        )
        self.scene_start("quick_revision")

        t15 = self.scene_title("Quick Revision — Five Things to Remember", width=11.5)

        rev_items = [
            ("1", "Find the rule"),
            ("2", "Use E-J-O-T-Y anchors"),
            ("3", "Opposites add to 27"),
            ("4", "Z wraps to A"),
            ("5", "Verify → apply → eliminate"),
        ]

        rev_cards = VGroup()
        for num, body in rev_items:
            c, _, _, _ = self.rounded_card(
                f"{num}",
                [body],
                width=2.32,
                height=2.15,
                heading_size=30,
                body_size=19,
            )
            rev_cards.add(c)

        rev_cards.arrange(RIGHT, buff=0.10)
        self.fit(rev_cards, 12.65, 2.55)
        rev_cards.move_to(DOWN * 0.15)

        anchors = RoundedRectangle(width=6.4, height=0.85, corner_radius=0.13, stroke_width=2)
        anchor_text2 = Text("E(5)   J(10)   O(15)   T(20)   Y(25)", font_size=27, weight=BOLD)
        self.fit(anchor_text2, 5.95, 0.52)
        VGroup(anchors, anchor_text2).move_to(DOWN * 2.55)

        self.play(
            FadeOut(t14),
            FadeOut(source_word),
            FadeOut(target_word),
            FadeOut(step_arrows),
            FadeOut(step_labels),
            FadeOut(lily),
            FadeOut(nkna),
            FadeOut(lily_arrows),
            FadeOut(lily_labels),
            FadeOut(wrap_box),
            FadeOut(wrap_text),
            FadeOut(answer),
        )
        self.play(FadeIn(t15))
        self.play(LaggedStart(*[FadeIn(c) for c in rev_cards], lag_ratio=0.10))
        self.play(FadeIn(anchors), FadeIn(anchor_text2))
        self.wait_for_narration(n15)
        self.scene_end("quick_revision")

        # ==============================================================
        # 16. CLOSING — next lesson
        # ==============================================================
        n16 = self.narrate(
            id="closing",
            text=(
                "You now have the vocabulary, the alphabet toolkit, and a dependable method. "
                "In the next concept, Letter Coding, we'll use these tools on a wider range of rules: "
                "variable shifts, position-based patterns, opposite-letter codes, and combinations of these. "
                "The method stays the same; only the rules get more interesting."
            ),
            voice="default",
            subtitle=True,
        )
        self.scene_start("closing")

        t16 = self.scene_title("You Have the Toolkit", width=9.8)

        toolkit_nodes = VGroup()
        for label in ["Vocabulary", "Positions", "Opposites", "Circular alphabet", "Exam routine"]:
            node = RoundedRectangle(width=2.0, height=0.78, corner_radius=0.13, stroke_width=2)
            txt = Text(label, font_size=21, weight=BOLD)
            self.fit(txt, 1.72, 0.50)
            toolkit_nodes.add(VGroup(node, txt))

        toolkit_nodes.arrange(RIGHT, buff=0.14)
        self.fit(toolkit_nodes, 11.8, 1.0)
        toolkit_nodes.move_to(UP * 0.75)

        next_box = RoundedRectangle(width=8.8, height=1.55, corner_radius=0.18, stroke_width=2.6)
        next_head = Text("NEXT: LETTER CODING", font_size=34, weight=BOLD)
        next_body = Text("More shifts • position patterns • opposite-letter codes", font_size=25)
        self.fit(next_head, 7.95, 0.58)
        self.fit(next_body, 7.9, 0.48)
        next_content = VGroup(next_head, next_body).arrange(DOWN, buff=0.18)
        self.fit(next_content, 8.2, 1.15)
        next_content.move_to(next_box)
        next_group = VGroup(next_box, next_content).move_to(DOWN * 1.25)

        method_tag = Text("Same method. More interesting rules.", font_size=28, weight=BOLD)
        self.fit(method_tag, 7.6, 0.50)
        method_tag.to_edge(DOWN, buff=0.48)

        self.play(FadeOut(t15), FadeOut(rev_cards), FadeOut(anchors), FadeOut(anchor_text2))
        self.play(FadeIn(t16))
        self.play(LaggedStart(*[FadeIn(n, shift=UP * 0.12) for n in toolkit_nodes], lag_ratio=0.10))
        self.play(FadeIn(next_group), FadeIn(method_tag))
        self.wait_for_narration(n16)
        self.scene_end("closing")
