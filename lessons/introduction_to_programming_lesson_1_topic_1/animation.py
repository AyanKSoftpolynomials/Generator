"""
C-004  Machine Language
C-CAT Section B > Module 01 C Programming > Lesson 01 > Topic 01 Introduction to Programming

Built from the natural script "C-004 - Machine Language.pdf" on the pattern of
golden_animation.py:

* one narrated class, written literally as ``class ...(LMSScene)``;
* narration is the timeline: narrate > play the visual for that idea >
  wait_for_narration; single visuals land on their spoken word with at_word;
* one method per script section, each wrapped in scene_start / clear_stage /
  scene_end;
* every position comes from the zone constants, all text goes through
  fitted_text or pill, and the busiest layouts are checked with the validator.

Depth: LMSScene is a 2D scene, so the 3D look is drawn. ``Prism`` gives every
chip, bit tile and block a lit top face, a shaded side face and a drop
shadow, all seen from the same viewpoint (DEPTH_DIR).
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
SCENERY = "#3A4257"

# Semantic colours: one meaning each, used the same way in every section.
BIT_ON = "#4FC3F7"     # a 1 / an "on" signal / machine language
BIT_OFF = "#5C6B8A"    # a 0 / an "off" signal
CPU = "#9FA8DA"        # the processor
CHIP = "#1C2640"       # chip body
PIN = "#B0BEC5"        # chip pins
OPCODE = "#FFB74D"     # the operation part of an instruction
OPERAND = "#BA68C8"    # the data / location part of an instruction
HUMAN = "#F06292"      # human-friendly languages
ASM = "#4DB6AC"        # assembly language
FOCUS = "#FFD54F"      # "look here"
GOOD = "#66BB6A"       # correct / advantage
BAD = "#EF5350"        # wrong / drawback

FONT = "Segoe UI"
MONO = "Consolas"
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
TOP_Y = FRAME_H / 2 - SAFE - 0.9              # first row under the section tag
BOTTOM_Y = -FRAME_H / 2 + SAFE + 0.45         # caption / tracker row

DEPTH_DIR = np.array([0.55, 0.34, 0.0])       # screen direction of "into the page"

# ======================================================== bit content ====
# Fixed patterns (never random) so every render is identical.

LOAD_FIVE = "10110000 00000101"               # the script's illustrative "load the value 5"
CORE_BITS = "00101101 01101001"               # a generic instruction for the anatomy
STREAM = [
    "10110000 00000101", "01101100 10100011", "11100101 00011010", "00101101 01101001",
    "10010110 11001010", "01011011 00110100", "11001001 01110001", "00110110 10011100",
]
WALL = [LOAD_FIVE] + STREAM[1:] + ["10100111 01011000"]


# ======================================================= text helpers ====

def text(s, size=BODY, color=INK, weight=NORMAL):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight)


def bits_text(s, size=BODY):
    """Binary in a monospace font: 1s in BIT_ON, 0s in BIT_OFF."""
    return Text(s, font=MONO, font_size=size, t2c={"1": BIT_ON, "0": BIT_OFF})


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


def fitted_text(s, max_width, size=BODY, color=INK, weight=NORMAL, max_lines=3):
    """Readable text no wider than ``max_width``.

    Order of preference: as written > slightly smaller (to 85 %) > wrapped
    over more lines > wrapped and smaller (never below MIN_FONT). If none of
    that fits, fail loudly: the author must shorten the text or widen the
    container. Tiny text is never an acceptable fix.
    """
    floor = max(MIN_FONT, 0.85 * size)
    for lines in range(1, max_lines + 1):
        body = s if lines == 1 else wrap_lines(s, lines)
        mob = text(body, size, color, weight)
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


def keep_in_frame(mob, margin=SAFE):
    """Shrink (if needed) and shift ``mob`` so it lies inside the safe area."""
    fit_within(mob, FRAME_W - 2 * margin, FRAME_H - 2 * margin)
    x_min, x_max = -FRAME_W / 2 + margin, FRAME_W / 2 - margin
    y_min, y_max = -FRAME_H / 2 + margin, FRAME_H / 2 - margin
    dx = max(0, x_min - mob.get_left()[0]) - max(0, mob.get_right()[0] - x_max)
    dy = max(0, y_min - mob.get_bottom()[1]) - max(0, mob.get_top()[1] - y_max)
    return mob.shift(RIGHT * dx + UP * dy)


# ================================================== 3D-look helpers ====

def tint(color, amount, towards=BLACK):
    """``color`` moved ``amount`` of the way towards ``towards``."""
    return interpolate_color(ManimColor(color), ManimColor(towards), amount)


class Prism(VGroup):
    """A box drawn with depth: front face, lit top face, shaded right side and
    a soft drop shadow. ``front`` is the face that carries labels."""

    def __init__(self, width, height, depth=0.3, color=PANEL, edge=MUTED, stroke_width=2):
        super().__init__()
        d = DEPTH_DIR * depth
        self.front = Rectangle(width=width, height=height, stroke_color=edge, stroke_width=stroke_width,
                               fill_color=color, fill_opacity=1)
        ul, ur, dr = self.front.get_corner(UL), self.front.get_corner(UR), self.front.get_corner(DR)
        self.top = Polygon(ul, ur, ur + d, ul + d, stroke_color=edge, stroke_width=stroke_width,
                           fill_color=tint(color, 0.25, WHITE), fill_opacity=1)
        self.side = Polygon(ur, dr, dr + d, ur + d, stroke_color=edge, stroke_width=stroke_width,
                            fill_color=tint(color, 0.45), fill_opacity=1)
        self.shadow = Ellipse(width=width + depth * 1.6, height=0.16 + depth * 0.5, stroke_width=0,
                              fill_color=BLACK, fill_opacity=0.45)
        self.shadow.move_to(self.front.get_bottom() + d * 0.5 + DOWN * 0.06)
        self.add(self.shadow, self.side, self.top, self.front)

    def paint(self, color, edge=None):
        """Recolour all three faces in place, keeping the lighting."""
        edge = edge or color
        self.front.set_fill(color, 1).set_stroke(edge)
        self.top.set_fill(tint(color, 0.25, WHITE), 1).set_stroke(edge)
        self.side.set_fill(tint(color, 0.45), 1).set_stroke(edge)
        return self

    def recolor(self, color, edge=None):
        """Animation version of ``paint``."""
        self.generate_target()
        self.target.paint(color, edge)
        return MoveToTarget(self)


class Chip(VGroup):
    """Processor chip with depth, pins and a glowing ``die`` in the middle."""

    def __init__(self, size=1.8, label="CPU"):
        super().__init__()
        count, pin_len, pin_w = 5, 0.12 * size, 0.05 * size
        pins = VGroup()
        for i in range(count):
            off = (i - (count - 1) / 2) * size / (count + 0.5)
            pins.add(Rectangle(width=pin_len, height=pin_w).move_to(LEFT * (size / 2 + pin_len / 2) + UP * off))
            pins.add(Rectangle(width=pin_w, height=pin_len).move_to(DOWN * (size / 2 + pin_len / 2) + RIGHT * off))
        pins.set_stroke(width=0).set_fill(PIN, 1)
        self.pins = pins
        self.body = Prism(size, size, 0.14 * size, CHIP, CPU)
        self.die = RoundedRectangle(corner_radius=0.06 * size, width=0.56 * size, height=0.56 * size,
                                    stroke_color=CPU, stroke_width=2, fill_color=CPU, fill_opacity=0.18)
        self.label = fit_width(text(label, max(MIN_FONT, round(34 * size / 1.8)), CPU, BOLD), 0.46 * size)
        self.add(pins, self.body, self.die, self.label)

    def pulse(self):
        """The processor 'acting': the die flashes."""
        return AnimationGroup(Indicate(self.die, color=FOCUS, scale_factor=1.12),
                              Flash(self.die, color=FOCUS, line_length=0.25 * self.die.width,
                                    flash_radius=0.8 * self.die.width))


def bit_tile(bit, size=0.55):
    """One bit as a small raised tile."""
    color = BIT_ON if bit == "1" else BIT_OFF
    tile = Prism(size, size, 0.22 * size, tint(color, 0.55), color, stroke_width=1.5)
    digit = Text(bit, font=MONO, font_size=round(52 * size), color=INK, weight=BOLD).move_to(tile.front)
    g = VGroup(tile, digit)
    g.tile = tile
    return g


def bit_row(bits, size=0.55, gap=0.08, byte_gap=0.3):
    """A row of bit tiles, with a wider gap between bytes."""
    row = VGroup()
    for i, b in enumerate(bits.replace(" ", "")):
        row.add(bit_tile(b, size).move_to(RIGHT * (i * (size + gap) + (i // 8) * byte_gap)))
    return row.center()


def block(label, width, height=0.8, color=PANEL, edge=MUTED, size=SMALL, depth=0.3):
    """A labelled 3D block (a language, a layer)."""
    box = Prism(width, height, depth, color, edge)
    words = fitted_text(label, width - 0.4, size, INK, BOLD, max_lines=2).move_to(box.front)
    g = VGroup(box, words)
    g.box, g.words = box, words
    return g


def lamp(on):
    """A signal lamp: lit (1) or dark (0)."""
    color = BIT_ON if on else BIT_OFF
    bulb = Circle(radius=0.55, stroke_color=color, stroke_width=4, fill_color=color,
                  fill_opacity=0.9 if on else 0.15)
    halo = VGroup(*[Circle(radius=0.55 + 0.14 * k, stroke_width=0, fill_color=color, fill_opacity=0.14 / k)
                    for k in (1, 2, 3)]) if on else VGroup()
    digit = text("1" if on else "0", TITLE, BG if on else MUTED, BOLD).move_to(bulb)
    name = text("on" if on else "off", SMALL, color, BOLD).next_to(bulb, DOWN, buff=0.45)
    g = VGroup(halo, bulb, digit, name)
    g.halo, g.bulb, g.digit, g.name = halo, bulb, digit, name
    return g


def toggle():
    """A front-panel switch, starting down (0)."""
    slot = RoundedRectangle(corner_radius=0.12, width=0.42, height=1.0, stroke_color=MUTED, stroke_width=2,
                            fill_color=BG, fill_opacity=1)
    knob = Prism(0.3, 0.3, 0.1, BIT_OFF, MUTED, stroke_width=1.5)
    knob.move_to(slot.get_bottom() + UP * 0.26)
    sw = VGroup(slot, knob)
    sw.slot, sw.knob = slot, knob
    return sw


def flip_up(sw):
    sw.knob.generate_target()
    sw.knob.target.shift(UP * 0.44).paint(BIT_ON)
    return MoveToTarget(sw.knob)


def tick(size=0.5, color=GOOD):
    return VMobject(stroke_color=color, stroke_width=8).set_points_as_corners(
        [LEFT * 0.5, DOWN * 0.4 + LEFT * 0.12, UP * 0.45 + RIGHT * 0.5]).scale(size)


def cross(size=0.5, color=BAD):
    return VGroup(Line(UL, DR), Line(UR, DL)).set_stroke(color, 8).scale(size * 0.5)


def person():
    head = Circle(radius=0.3, stroke_color=MUTED, stroke_width=5)
    body = Arc(radius=0.55, start_angle=0, angle=PI, stroke_color=MUTED, stroke_width=5)
    body.next_to(head, DOWN, buff=0.1)
    return VGroup(head, body)


def balance_scale(beam_w=7.6, drop=2.0, pan_w=3.0):
    """Balance scale built in place (pivot at UP * 1.3). ``pan_tops`` are the
    points where the left and right pans' contents sit."""
    top = UP * 1.3
    post = Rectangle(width=0.16, height=2.4, stroke_width=0, fill_color=SCENERY, fill_opacity=1)
    post.move_to(top + DOWN * 1.2)
    foot = post.get_bottom()
    base = Polygon(foot + LEFT * 0.8 + DOWN * 0.25, foot + RIGHT * 0.8 + DOWN * 0.25,
                   foot + RIGHT * 0.25, foot + LEFT * 0.25, stroke_width=0, fill_color=SCENERY, fill_opacity=1)
    beam = Rectangle(width=beam_w, height=0.12, stroke_width=0, fill_color=MUTED, fill_opacity=1).move_to(top)
    pivot = Circle(radius=0.14, stroke_width=0, fill_color=FOCUS, fill_opacity=1).move_to(top)
    scale = VGroup(post, base, beam)
    pan_tops = []
    for s in (-1, 1):
        hang = top + RIGHT * s * beam_w / 2
        pan_top = hang + DOWN * drop
        strings = VGroup(Line(hang, pan_top + LEFT * pan_w / 2), Line(hang, pan_top + RIGHT * pan_w / 2))
        strings.set_stroke(MUTED, 2)
        pan = Polygon(pan_top + LEFT * pan_w / 2, pan_top + RIGHT * pan_w / 2,
                      pan_top + RIGHT * (pan_w / 2 - 0.3) + DOWN * 0.25,
                      pan_top + LEFT * (pan_w / 2 - 0.3) + DOWN * 0.25,
                      stroke_color=MUTED, stroke_width=2, fill_color=SCENERY, fill_opacity=1)
        scale.add(strings, pan)
        pan_tops.append(pan_top)
    scale.add(pivot)
    scale.pivot, scale.pan_tops = pivot, pan_tops
    return scale



# ============================================================= lesson ====

class CommonlyConfusedCorrectionTrapsVideo(LMSScene):
    lesson_title = "Commonly Confused Correction Traps"

    def construct(self):
        self.camera.background_color = BG
        self.section_tag = None

        self.hook()
        self.objectives()
        self.concept()
        self.why_it_matters()
        self.analogy()
        self.examples()
        self.rules()
        self.process()
        self.solved()
        self.exam_patterns()
        self.mistakes()
        self.practice()
        self.answer()
        self.revision()
        self.closing()

    # ---------------------------------------------------- scene helpers --

    def show_section_tag(self, label):
        tag = pill(label.upper(), MUTED, size=18, fill_opacity=0.08)
        tag.to_corner(UL, buff=SAFE)
        if self.section_tag is None:
            self.play(FadeIn(tag), run_time=0.4)
        else:
            self.play(FadeTransform(self.section_tag, tag), run_time=0.4)
        self.section_tag = tag

    def clear_stage(self, run_time=0.55):
        others = [m for m in self.mobjects if m is not self.section_tag]
        if others:
            self.play(FadeOut(Group(*others)), run_time=run_time)

    def card(self, content, width=None, height=None, color=MUTED, pad=0.28):
        if width is not None or height is not None:
            fit_within(content, (width or 99) - 2 * pad, (height or 99) - 2 * pad)
        w = width if width is not None else content.width + 2 * pad
        h = height if height is not None else content.height + 2 * pad
        box = RoundedRectangle(
            corner_radius=0.18, width=w, height=h,
            stroke_color=color, stroke_width=2.5,
            fill_color=PANEL, fill_opacity=1
        )
        box.move_to(content)
        self.validator.check_fit(content, box, margin=0.1)
        return VGroup(box, content)

    def caption(self, s, color=INK):
        t = fitted_text(s, SAFE_W - 1.0, BODY, color, max_lines=1)
        bar = self.card(t, width=SAFE_W - 0.4, height=t.height + 0.8, color=MUTED)
        return bar.move_to(UP * BOTTOM_Y)

    def trap_block(self, name, description, color, width=3.55, height=1.18):
        title = fitted_text(name, width - 0.55, LABEL, color, BOLD, max_lines=1)
        body = fitted_text(description, width - 0.55, SMALL, INK, max_lines=2)
        content = VGroup(title, body).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        return self.card(content, width=width, height=height, color=color, pad=0.22)

    def option_row(self, letter, statement, width=10.8):
        badge = pill(letter, FOCUS, SMALL)
        body = fitted_text(statement, width - 1.0, SMALL, INK, max_lines=2)
        content = VGroup(badge, body).arrange(RIGHT, buff=0.28)
        return self.card(content, width=width, height=1.0, color=MUTED, pad=0.18)

    def rule_row(self, trap, test, width=11.0):
        left = fitted_text(trap, 3.1, SMALL, INK, BOLD, max_lines=2)
        right = fitted_text(test, 7.1, SMALL, INK, max_lines=2)
        content = VGroup(left, right).arrange(RIGHT, buff=0.55, aligned_edge=UP)
        return self.card(content, width=width, height=1.0, color=MUTED, pad=0.2)

    def practice_card(self, number, question, options, width=5.55, height=2.25):
        num = pill(str(number), FOCUS, SMALL)
        q = fitted_text(question, width - 0.65, SMALL, INK, BOLD, max_lines=2)
        opts = fitted_text(options, width - 0.65, SMALL, MUTED, max_lines=3)
        content = VGroup(
            VGroup(num, q).arrange(RIGHT, buff=0.25),
            opts
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        return self.card(content, width=width, height=height, color=MUTED, pad=0.2)

    # ======================================================= 1. HOOK ====

    def hook(self):
        self.scene_start("S01_hook", title="Hook")
        self.show_section_tag("Commonly Confused Correction Traps")

        email = self.card(
            fitted_text(
                'Please send the final report to John and I by Friday.',
                9.6, BODY, INK, BOLD, max_lines=2
            ),
            width=10.2, height=1.65, color=FOCUS, pad=0.35
        ).move_to(UP * 1.7)

        prompt = fitted_text(
            "Choose the best replacement.",
            6.5, BODY, FOCUS, BOLD, max_lines=1
        ).move_to(UP * 0.35)

        options = VGroup(
            self.option_row("A", "to John and me"),
            self.option_row("B", "to John and myself"),
            self.option_row("C", "to I and John"),
            self.option_row("D", "No improvement"),
        ).arrange(DOWN, buff=0.16).move_to(DOWN * 1.55)

        n = self.narrate(
            id="hook_01",
            text='A project email says: "Please send the final report to John and I by Friday." Choose the best replacement.',
            subtitle=True,
        )
        self.at_word(n, "project email")
        self.play(FadeIn(email, shift=UP * 0.2))
        self.at_word(n, "best replacement")
        self.play(FadeIn(prompt, shift=UP * 0.15), FadeIn(options[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Two of these options feel extra polite. Only one is correct.",
            subtitle=True,
        )
        self.at_word(n, "extra polite")
        self.play(FadeIn(options[1], shift=UP * 0.1), FadeIn(options[2], shift=UP * 0.1))
        self.at_word(n, "Only one is correct")
        self.play(FadeIn(options[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_hook")

    # =================================================== 2. OBJECTIVES ====

    def objectives(self):
        self.scene_start("S02_objectives", title="Objectives")
        self.show_section_tag("Objectives")

        cards = VGroup(
            self.card(
                fitted_text("1. Recognise the traps built into correction options.", 9.2, BODY, INK, max_lines=2),
                width=10.0, height=1.35, color=BIT_ON
            ),
            self.card(
                fitted_text('2. Avoid hypercorrection: "corrections" that are actually errors.', 9.2, BODY, INK, max_lines=2),
                width=10.0, height=1.35, color=HUMAN
            ),
        ).arrange(DOWN, buff=0.35).move_to(UP * 0.35)

        n = self.narrate(
            id="objectives_01",
            text="By the end of this lesson, you should recognise the traps built into correction options and avoid hypercorrection, where a correction that sounds better is actually an error.",
            subtitle=True,
        )
        self.at_word(n, "recognise the traps")
        self.play(FadeIn(cards[0], shift=UP * 0.2))
        self.at_word(n, "avoid hypercorrection")
        self.play(FadeIn(cards[1], shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ==================================================== 3. CONCEPT =====

    def concept(self):
        self.scene_start("S03_concept", title="The Concept")
        self.show_section_tag("The Concept")

        title = fitted_text("Five traps correction options are built around", 10.5, TITLE, FOCUS, BOLD, max_lines=2).move_to(UP * 2.6)
        traps = VGroup(
            self.trap_block("Half-fix", "One error fixed; another remains.", FOCUS),
            self.trap_block("New error", "The fix introduces another error.", BAD),
            self.trap_block("Meaning shift", "Grammar changes the intended meaning.", ASM),
            self.trap_block("Hypercorrection", "It sounds formal but is actually wrong.", HUMAN),
            self.trap_block("Wordy fix", "Correct, but longer than needed.", GOOD),
        ).arrange_in_grid(rows=2, cols=3, buff=(0.3, 0.3)).move_to(DOWN * 0.15)

        # The fifth item sits alone and is centered.
        traps[4].move_to(DOWN * 2.15)

        n = self.narrate(
            id="concept_01",
            text="Correction options are designed around five traps: half-fix, new error, meaning shift, hypercorrection, and wordy fix.",
            subtitle=True,
        )
        for phrase, idx in (
            ("half-fix", 0),
            ("new error", 1),
            ("meaning shift", 2),
            ("hypercorrection", 3),
            ("wordy fix", 4),
        ):
            self.at_word(n, phrase)
            self.play(FadeIn(traps[idx], shift=UP * 0.12))
        self.play(FadeIn(title, shift=DOWN * 0.15))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_concept")

    # ================================================ 4. WHY IT MATTERS ===

    def why_it_matters(self):
        self.scene_start("S04_why", title="Why You Need It")
        self.show_section_tag("Why You Need It")

        score = VGroup(
            pill("Original error", BAD, SMALL),
            Arrow(LEFT * 0.9, RIGHT * 0.9, color=MUTED, stroke_width=4),
            pill("Correction option", FOCUS, SMALL),
            Arrow(LEFT * 0.9, RIGHT * 0.9, color=MUTED, stroke_width=4),
            pill("Trap check", GOOD, SMALL),
        ).arrange(RIGHT, buff=0.18).move_to(UP * 1.35)

        note = self.card(
            fitted_text(
                "Knowing the five traps makes elimination fast.",
                8.8, TITLE, GOOD, BOLD, max_lines=2
            ),
            width=9.8, height=1.7, color=GOOD
        ).move_to(DOWN * 0.8)

        small = fitted_text(
            "The traps can matter more than the original error.",
            8.8, BODY, INK, max_lines=2
        ).move_to(DOWN * 2.45)

        n = self.narrate(
            id="why_01",
            text="Most students lose sentence-correction marks to these traps, not to the original error. Knowing the five traps makes elimination fast.",
            subtitle=True,
        )
        self.at_word(n, "these traps")
        self.play(FadeIn(score, shift=UP * 0.15))
        self.at_word(n, "elimination fast")
        self.play(FadeIn(note, shift=UP * 0.2), FadeIn(small, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_why")

    # ================================================= 5. ANALOGY ========

    def analogy(self):
        self.scene_start("S05_analogy", title="The Analogy")
        self.show_section_tag("The Analogy")

        note = RoundedRectangle(
            corner_radius=0.12, width=2.4, height=3.0,
            stroke_color=FOCUS, stroke_width=3,
            fill_color=PANEL, fill_opacity=1
        ).move_to(LEFT * 3.2 + DOWN * 0.2)
        uv = Circle(radius=0.65, stroke_color=GOOD, stroke_width=5, fill_color=GOOD, fill_opacity=0.15).move_to(
            LEFT * 3.2 + UP * 0.65
        )
        thread = Line(
            LEFT * 3.2 + UP * 0.05,
            LEFT * 3.2 + DOWN * 1.0,
            color=BAD, stroke_width=5
        )
        note_group = VGroup(note, uv, thread)

        text_box = self.card(
            fitted_text(
                "Counterfeit correct English can look right at a glance.",
                6.5, BODY, INK, max_lines=3
            ),
            width=7.0, height=1.65, color=FOCUS
        ).move_to(RIGHT * 2.1 + UP * 0.75)

        uv_label = pill("UV lamp = trap test", GOOD, SMALL).move_to(RIGHT * 2.2 + DOWN * 1.05)

        n = self.narrate(
            id="analogy_01",
            text="A counterfeit note looks right at a glance. Under a UV lamp, the missing security thread shows.",
            subtitle=True,
        )
        self.at_word(n, "counterfeit note")
        self.play(FadeIn(note_group, scale=0.95))
        self.at_word(n, "UV lamp")
        self.play(FadeIn(uv_label, shift=UP * 0.15), Indicate(thread, color=BAD))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Hypercorrections are counterfeit correct English; the remove the other person test is the UV lamp.",
            subtitle=True,
        )
        self.at_word(n, "Hypercorrections")
        self.play(FadeIn(text_box, shift=LEFT * 0.15))
        self.at_word(n, "remove the other person")
        self.play(Indicate(uv_label, color=GOOD, scale_factor=1.08))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_analogy")

    # ================================================= 6. EXAMPLES =======

    def examples(self):
        self.scene_start("S06_examples", title="Worked Examples")
        self.show_section_tag("Worked Examples")

        examples = [
            ('1', '"The award was given to my colleague and I." → "my colleague and me".'),
            ('2', '"Whom do you think is the best candidate?" → "Who" (he is the best candidate).'),
            ('3', '"Please contact myself for details." → "contact me".'),
        ]

        cards = VGroup(*[
            self.card(
                VGroup(
                    pill(num, FOCUS, SMALL),
                    fitted_text(s, 9.0, SMALL, INK, max_lines=3)
                ).arrange(RIGHT, buff=0.28),
                width=10.2, height=1.35, color=MUTED, pad=0.18
            )
            for num, s in examples
        ]).arrange(DOWN, buff=0.22).move_to(DOWN * 0.1)

        n = self.narrate(
            id="examples_01",
            text='First: "The award was given to my colleague and I." becomes "my colleague and me".',
            subtitle=True,
        )
        self.at_word(n, "first")
        self.play(FadeIn(cards[0], shift=UP * 0.15))
        self.at_word(n, "my colleague and me")
        self.play(Indicate(cards[0], color=GOOD, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="examples_02",
            text='Second: "Whom do you think is the best candidate?" becomes "Who", because he is the best candidate.',
            subtitle=True,
        )
        self.at_word(n, "Second")
        self.play(FadeIn(cards[1], shift=UP * 0.15))
        self.at_word(n, "Who")
        self.play(Indicate(cards[1], color=GOOD, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="examples_03",
            text='Third: "Please contact myself for details." becomes "contact me".',
            subtitle=True,
        )
        self.at_word(n, "Third")
        self.play(FadeIn(cards[2], shift=UP * 0.15))
        self.at_word(n, "contact me")
        self.play(Indicate(cards[2], color=GOOD, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_examples")

    # ================================================= 7. RULES ==========

    def rules(self):
        self.scene_start("S07_rules", title="Rules")
        self.show_section_tag("Rules")

        rows = VGroup(
            self.rule_row("Half-fix", "Re-scan the whole option with S-T-P-A-W."),
            self.rule_row("New error", "Check every changed word."),
            self.rule_row("Meaning shift", "Compare with the original meaning."),
            self.rule_row("Hypercorrection", "Remove the other person; use he / him for who / whom."),
            self.rule_row("Wordy fix", "Prefer the shorter correct option."),
        ).arrange(DOWN, buff=0.15).move_to(DOWN * 0.1)

        n = self.narrate(
            id="rules_01",
            text="Here is the trap test. For a half-fix, re-scan the whole option with S-T-P-A-W. For a new error, check every changed word. For meaning shift, compare with the original meaning. For hypercorrection, remove the other person and replace who or whom with he or him. For a wordy fix, prefer the shorter correct option.",
            subtitle=True,
        )
        for phrase, idx in (
            ("half-fix", 0),
            ("new error", 1),
            ("meaning shift", 2),
            ("hypercorrection", 3),
            ("wordy fix", 4),
        ):
            self.at_word(n, phrase)
            self.play(FadeIn(rows[idx], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_rules")

    # ================================================= 8. PROCESS ========

    def process(self):
        self.scene_start("S08_process", title="The Process")
        self.show_section_tag("The Process")

        steps = VGroup(*[
            self.card(
                VGroup(
                    pill(str(i + 1), FOCUS, SMALL),
                    fitted_text(s, 8.7, BODY, INK, max_lines=2)
                ).arrange(RIGHT, buff=0.3),
                width=10.0, height=1.15, color=MUTED
            )
            for i, s in enumerate([
                "Diagnose the original error.",
                "For each option: fix? new error? meaning? length?",
                "Apply the hypercorrection tests where pronouns change.",
                "Confirm.",
            ])
        ]).arrange(DOWN, buff=0.18).move_to(DOWN * 0.1)

        n = self.narrate(
            id="process_01",
            text="Use a four-step process. First, diagnose the original error. Second, for each option ask: fix, new error, meaning, length? Third, apply the hypercorrection tests where pronouns change. Fourth, confirm.",
            subtitle=True,
        )
        for phrase, idx in (
            ("First", 0),
            ("Second", 1),
            ("Third", 2),
            ("Fourth", 3),
        ):
            self.at_word(n, phrase)
            self.play(FadeIn(steps[idx], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_process")

    # ================================================= 9. SOLVED =========

    def solved(self):
        self.scene_start("S09_solved", title="Hook, Solved")
        self.show_section_tag("Hook, Solved")

        original = self.card(
            fitted_text('"to John and I"', 5.0, TITLE, BAD, BOLD, max_lines=1),
            width=5.5, height=1.25, color=BAD
        ).move_to(LEFT * 3.1 + UP * 1.75)

        corrected = self.card(
            fitted_text('"to John and me"', 5.0, TITLE, GOOD, BOLD, max_lines=1),
            width=5.5, height=1.25, color=GOOD
        ).move_to(RIGHT * 3.1 + UP * 1.75)

        test = self.card(
            fitted_text('"send the report to me" ✓', 8.8, BODY, INK, BOLD, max_lines=2),
            width=9.4, height=1.35, color=FOCUS
        ).move_to(UP * 0.15)

        verdict = pill("(a) is correct", GOOD, BODY).move_to(DOWN * 1.65)

        n = self.narrate(
            id="solved_01",
            text='Read: "to John and I". Predict: after "to", use the object form, me.',
            subtitle=True,
        )
        self.at_word(n, "Read")
        self.play(FadeIn(original, shift=UP * 0.15))
        self.at_word(n, "object form")
        self.play(FadeIn(test, shift=UP * 0.15))
        self.at_word(n, "me")
        self.play(FadeIn(corrected, shift=UP * 0.15))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text='Eliminate option b because myself is a hypercorrection; it is not reflexive here. Option c keeps I and changes the order. Option d keeps the error.',
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(Indicate(original, color=BAD))
        self.at_word(n, "myself")
        self.play(Indicate(test, color=HUMAN))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text='Confirm: "Please send the final report to John and me by Friday." Option a.',
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(FadeIn(verdict, shift=UP * 0.2), Indicate(corrected, color=GOOD, scale_factor=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_solved")

    # ============================================ 10. EXAM PATTERNS =======

    def exam_patterns(self):
        self.scene_start("S10_patterns", title="Exam Patterns and Solving Models")
        self.show_section_tag("Exam Patterns and Solving Models")

        rows = VGroup(
            self.rule_row("Pronoun pairs (X and I / me)", "Remove the other person and test.", width=11.2),
            self.rule_row("who / whom in a clause", "he / him test inside the clause.", width=11.2),
            self.rule_row("Two plausible options", "Check for new errors and length.", width=11.2),
        ).arrange(DOWN, buff=0.2).move_to(DOWN * 0.1)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns matter. For pronoun pairs such as X and I or X and me, remove the other person and test. For who or whom in a clause, use the he or him test inside the clause. When two options look plausible, check for new errors and length.",
            subtitle=True,
        )
        self.at_word(n, "pronoun pairs")
        self.play(FadeIn(rows[0], shift=UP * 0.12))
        self.at_word(n, "who or whom")
        self.play(FadeIn(rows[1], shift=UP * 0.12))
        self.at_word(n, "two options")
        self.play(FadeIn(rows[2], shift=UP * 0.12))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_patterns")

    # ================================================ 11. MISTAKES =======

    def mistakes(self):
        self.scene_start("S11_mistakes", title="Common Mistakes")
        self.show_section_tag("Common Mistakes")

        rows = VGroup(*[
            self.card(
                VGroup(
                    pill(str(i + 1), BAD, SMALL),
                    fitted_text(s, 9.2, BODY, INK, max_lines=2)
                ).arrange(RIGHT, buff=0.3),
                width=10.2, height=1.25, color=BAD
            )
            for i, s in enumerate([
                '"Between John and I", "to my team and I".',
                '"Contact myself".',
                '"Whom do you think will win?"',
            ])
        ]).arrange(DOWN, buff=0.2).move_to(DOWN * 0.1)

        n = self.narrate(
            id="mistakes_01",
            text='Watch for these common mistakes: "Between John and I", "to my team and I"; "Contact myself"; and "Whom do you think will win?"',
            subtitle=True,
        )
        self.at_word(n, "Between John and I")
        self.play(FadeIn(rows[0], shift=UP * 0.1))
        self.at_word(n, "Contact myself")
        self.play(FadeIn(rows[1], shift=UP * 0.1))
        self.at_word(n, "Whom do you think")
        self.play(FadeIn(rows[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_mistakes")

    # ================================================= 12. PRACTICE ======

    def practice(self):
        self.scene_start("S12_practice", title="Practice Questions")
        self.show_section_tag("Practice Questions")

        qs = VGroup(
            self.practice_card(
                1, '"Him and me worked on the project together."',
                "(a) He and me  (b) He and I  (c) Him and I  (d) No improvement",
            ),
            self.practice_card(
                2, '"The manager thanked Priya and myself."',
                "(a) Priya and I  (b) myself and Priya  (c) Priya and me  (d) No improvement",
            ),
            self.practice_card(
                3, '"She is the person whom I believe will win."',
                "(a) which  (b) whose  (c) who  (d) No improvement",
            ),
        ).arrange(DOWN, buff=0.18).move_to(DOWN * 0.1)

        n = self.narrate(
            id="practice_01",
            text='Question one: "Him and me worked on the project together." Choose the correct replacement.',
            subtitle=True,
        )
        self.at_word(n, "Question one")
        self.play(FadeIn(qs[0], shift=UP * 0.12))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text='Question two: "The manager thanked Priya and myself." Choose the correct replacement.',
            subtitle=True,
        )
        self.at_word(n, "Question two")
        self.play(FadeIn(qs[1], shift=UP * 0.12))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_03",
            text='Question three: "She is the person whom I believe will win." Choose the correct replacement.',
            subtitle=True,
        )
        self.at_word(n, "Question three")
        self.play(FadeIn(qs[2], shift=UP * 0.12))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_practice")

    # ================================================= 13. ANSWERS =======

    def answer(self):
        self.scene_start("S13_answer", title="Answers")
        self.show_section_tag("Answers")

        answers = VGroup(
            self.card(
                fitted_text('1. (b) — Subject form: "He worked", "I worked".', 9.2, BODY, GOOD, max_lines=2),
                width=10.0, height=1.25, color=GOOD
            ),
            self.card(
                fitted_text('2. (c) — Object form after "thanked".', 9.2, BODY, GOOD, max_lines=2),
                width=10.0, height=1.25, color=GOOD
            ),
            self.card(
                fitted_text('3. (c) — "I believe she will win" → who.', 9.2, BODY, GOOD, max_lines=2),
                width=10.0, height=1.25, color=GOOD
            ),
        ).arrange(DOWN, buff=0.18).move_to(DOWN * 0.1)

        n = self.narrate(
            id="answer_01",
            text='The answers are: one, b. Subject form: "He worked", "I worked". Two, c. Object form after "thanked". Three, c. "I believe she will win" leads to who.',
            subtitle=True,
        )
        self.at_word(n, "one, b")
        self.play(FadeIn(answers[0], shift=UP * 0.1))
        self.at_word(n, "Two, c")
        self.play(FadeIn(answers[1], shift=UP * 0.1))
        self.at_word(n, "Three, c")
        self.play(FadeIn(answers[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S13_answer")

    # ================================================= 14. REVISION ======

    def revision(self):
        self.scene_start("S14_revision", title="Revision")
        self.show_section_tag("Recap Card")

        traps = VGroup(*[
            pill(s, color, SMALL)
            for s, color in (
                ("Half-fix", FOCUS),
                ("New error", BAD),
                ("Meaning shift", ASM),
                ("Hypercorrection", HUMAN),
                ("Wordy fix", GOOD),
            )
        ]).arrange(RIGHT, buff=0.16).move_to(UP * 1.65)

        tests = VGroup(
            self.rule_row("I / me test", "Remove the other person.", width=10.6),
            self.rule_row("who / whom test", "he → who, him → whom.", width=10.6),
            self.rule_row("myself", "Only reflexive or emphatic.", width=10.6),
        ).arrange(DOWN, buff=0.16).move_to(DOWN * 0.65)

        n = self.narrate(
            id="revision_01",
            text="Recap. Five traps: half-fix, new error, meaning shift, hypercorrection, and wordy fix.",
            subtitle=True,
        )
        for phrase in ("half-fix", "new error", "meaning shift", "hypercorrection", "wordy fix"):
            self.at_word(n, phrase)
        self.play(LaggedStart(*[FadeIn(x, shift=UP * 0.1) for x in traps], lag_ratio=0.12))
        self.wait_for_narration(n)

        n = self.narrate(
            id="revision_02",
            text="Use the I and me test by removing the other person. For who and whom, use he and him. Myself is only reflexive or emphatic.",
            subtitle=True,
        )
        self.at_word(n, "I and me")
        self.play(FadeIn(tests[0], shift=UP * 0.1))
        self.at_word(n, "who and whom")
        self.play(FadeIn(tests[1], shift=UP * 0.1))
        self.at_word(n, "Myself")
        self.play(FadeIn(tests[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_revision")

    # ================================================= 15. CLOSING =======

    def closing(self):
        self.scene_start("S15_closing", title="Closing")
        self.show_section_tag("Next")

        statement = self.card(
            fitted_text(
                "Don't choose the option that merely sounds more correct.",
                8.6, TITLE, FOCUS, BOLD, max_lines=2
            ),
            width=9.5, height=1.8, color=FOCUS, pad=0.38
        ).move_to(UP * 1.2)

        checklist = VGroup(
            pill("Fix", GOOD, BODY),
            pill("No new error", GOOD, BODY),
            pill("Same meaning", GOOD, BODY),
            pill("Shortest correct", GOOD, BODY),
        ).arrange(RIGHT, buff=0.2).move_to(DOWN * 0.65)

        next_topic = pill("Next → Exam-Oriented Sentence Correction Patterns", ASM, SMALL).move_to(DOWN * 2.25)

        n = self.narrate(
            id="closing_01",
            text="Do not choose the option that merely sounds more correct. Check the error, new error, meaning, and length.",
            subtitle=True,
        )
        self.at_word(n, "sounds more correct")
        self.play(FadeIn(statement, shift=UP * 0.2))
        self.at_word(n, "meaning")
        self.play(FadeIn(checklist, shift=UP * 0.15))
        self.wait_for_narration(n)

        n = self.narrate(
            id="closing_02",
            text="That is the skill these correction traps are testing. The next video collects the correction patterns exams use most.",
            subtitle=True,
        )
        self.at_word(n, "skill")
        self.play(Indicate(statement, color=GOOD, scale_factor=1.04))
        self.at_word(n, "next video")
        self.play(FadeIn(next_topic, shift=UP * 0.15))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_closing")


# ============================================================= export ====

# The LMS video generator discovers LMSScene subclasses from this module.