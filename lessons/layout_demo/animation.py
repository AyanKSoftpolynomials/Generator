"""
Layout checks: a short example of the optional explicit validation API.

Every lesson is checked automatically while the generator reads it (text that
overflows its box, leaves the frame, collides with other text, or is too
small). A lesson can also state its intent explicitly:

  * self.validator.check_fit(text, box, margin=...)  text must sit inside box;
    if it does not, it is shrunk (never below the readable minimum) and moved
    inside, the same way in the dry run and the real render.
  * check_in_frame / check_spacing / check_size / check_no_overlap: report only.
  * self.validator.ignore(mob): leave a deliberate effect out of the automatic checks.

Generate:  python generate.py lessons/layout_demo/animation.py
"""

from manim import *

from src.animation import LMSScene

CARD_COLORS = ("#38BDF8", "#51CF66", "#FFD166")


class LayoutDemoVideo(LMSScene):
    lesson_title = "Layout Checks Demo"
    default_voice = "teacher_a"

    def card(self, label: str, color: str) -> VGroup:
        box = RoundedRectangle(width=3.4, height=1.3, corner_radius=0.18, color=color,
                               fill_color=color, fill_opacity=0.08)
        text = Text(label, font_size=34, weight=BOLD).move_to(box)
        # Longer labels than the card was designed for are fitted, not left overflowing.
        self.validator.check_fit(text, box, margin=0.2)
        return VGroup(box, text)

    def construct(self):
        self.scene_start("cards", title="Three Cards")
        title = Text("Parts of a Class", font_size=46, weight=BOLD).to_edge(UP)
        self.validator.check_in_frame(title)

        cards = VGroup(
            self.card("DATA MEMBERS", CARD_COLORS[0]),
            self.card("MEMBER FUNCTIONS", CARD_COLORS[1]),              # too wide at size 34: fitted
            self.card("ACCESS", CARD_COLORS[2]),
        ).arrange(RIGHT, buff=0.5).next_to(title, DOWN, buff=1.0)
        self.validator.check_spacing(cards[0], cards[1], min_gap=0.3)
        self.validator.check_size(cards, max_width=config.frame_width - 1)

        n = self.narrate("cards_01", "A class has data members, member functions and access rules.")
        self.play(FadeIn(title))
        self.play_with(n, LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards], lag_ratio=0.3))

        # A deliberate effect: the title slides out past the edge. Not a layout mistake.
        self.validator.ignore(title)
        n = self.narrate("cards_02", "Each card fits its label, however long the words are.")
        self.play_with(n, title.animate.shift(LEFT * 12), cards.animate.shift(UP * 1.2))
