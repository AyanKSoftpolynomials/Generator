"""
animation.py for the LMS video generator.

Course : CDAC C-CAT Preparation - Data Structures
Video  : Lists - The Classroom Movie
Source : C:/Scripts/Section A/Classroom Movie Scripts/Lists - The Classroom Movie.md

Look (3Blue1Brown style):
  - near-black background, white text, ONE blue and ONE brown accent;
    yellow only for a passing highlight, green / red only for right / wrong
  - text in Latin Modern Roman (the Computer Modern face of 3Blue1Brown), taken from the
    MiKTeX folder on this machine; Cambria is used if that folder is missing
  - code in Consolas
  - sizes: title 54, heading 38, body 32, label 28, small 24; nothing below 22

Roles (the script has no speaker labels; every line was assigned by meaning):
  NARRATOR  introduces and connects scenes        self.N   voice "vijay"
  TEACHER   teaches, asks, guides                 self.T / self.Q (question, shown on screen)   voice "aditya"
  STUDENT   answers, doubts, makes mistakes       self.S (always shown on screen)   voice "kavya"
  Stage directions are not spoken: they are the visuals.
  Spoken text uses words ("head arrow next arrow data"); the board shows the code.

Screen zones:
  top band   teacher (left corner), scene heading, student (right corner)
  strip      the question being asked or the student's line
  board      everything else (BOARD_TOP down to FLOOR)

Section map:
  S01 The connection   S02 Why lists matter in C-CAT   S03 What is a list   S04 The chain
  S05 Another C-CAT challenge   S06 Following a NULL link   S07 Real life   S08 The C-CAT takeaway
  S09 Summary   S10 Next session
"""

import math
import os
import types

import numpy as np
from manim import *

from src.animation import LMSScene

# ============================================================== style ====

BG = "#101010"
FILL = "#1B1B1B"           # inside of boxes
INK = "#F5F5F5"            # main text
MUTED = "#9A9A9A"          # supporting text
BLUE = "#58C4DD"           # accent 1: data, key terms
BROWN = "#CD853F"          # accent 2: links, pointers to remember
FLASH = "#FFFF00"          # a passing highlight only
GOOD = "#83C167"           # the right answer
BAD = "#FC6255"            # wrong / dangerous

LM_DIR = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "MiKTeX", "fonts", "opentype", "public", "lm")


def serif_font():
    """Latin Modern Roman when MiKTeX has it (registered for this run only), else Cambria."""
    try:
        import manimpango

        files = [os.path.join(LM_DIR, f"lmroman10-{style}.otf") for style in ("regular", "bold", "italic")]
        if all(os.path.exists(f) for f in files) and all(manimpango.register_font(f) for f in files):
            if "Latin Modern Roman 10" in manimpango.list_fonts():
                return "Latin Modern Roman 10"
    except Exception:
        pass
    return "Cambria"


FONT = serif_font()
MONO = "Consolas"
MIN_FONT = 22              # readable floor: text is never shrunk below this
TITLE = 54
HEAD = 38
BODY = 32
LABEL = 28
SMALL = 24
CODE = 24

# ============================================================= layout ====

FRAME_W = config.frame_width
FRAME_H = config.frame_height
SAFE = 0.45                                   # margin kept clear on every side
EDGE_X = FRAME_W / 2 - SAFE                   # furthest x any content may reach
TOP = FRAME_H / 2 - SAFE
FLOOR = -FRAME_H / 2 + SAFE + 0.1             # lowest y any content may reach

FACE_R = 0.36
HEAD_Y = 3.02                                 # centre of the scene heading
HEAD_W = FRAME_W - 2 * (SAFE + 2.6 * FACE_R + 0.4)
TIMER_Y = 2.58                                # the thinking-time bar
STRIP_TOP, STRIP_BOTTOM = 2.42, 1.48          # the spoken-line strip
STRIP_Y = (STRIP_TOP + STRIP_BOTTOM) / 2
STRIP_W = 11.0
BOARD_TOP = 1.32                              # top of the board while the strip is in use
BOARD_HIGH = 2.4                              # top of the board in scenes that show no spoken line

NARRATOR_VOICE = "vijay"
TEACHER_VOICE = "aditya"
STUDENT_VOICE = "kavya"
VOICES = {"N": NARRATOR_VOICE, "T": TEACHER_VOICE, "S": STUDENT_VOICE}
TURN_PAUSE = 0.6               # silence after each block, so the voices never run together


# ======================================================= text helpers ====

def text(s, size=BODY, color=INK, weight=NORMAL, slant=NORMAL, font=FONT):
    return Text(s, font=font, font_size=size, color=color, weight=weight, slant=slant, disable_ligatures=True)


def code(s, size=CODE, color=INK, weight=NORMAL):
    """Program text, variable names and values."""
    return text(s, size, color, weight, NORMAL, MONO)


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


def fitted_text(s, max_width, size=BODY, color=INK, weight=NORMAL, max_lines=3, slant=NORMAL):
    """Readable text no wider than ``max_width``: as written, else wrapped, else a little smaller.

    Never below MIN_FONT; if that is not enough it fails loudly."""
    for lines in range(1, max_lines + 1):
        mob = text(s if lines == 1 else wrap_lines(s, lines), size, color, weight, slant)
        if mob.width <= max_width:
            return mob
    if size * max_width / mob.width >= MIN_FONT:
        return mob.scale(max_width / mob.width)
    raise ValueError(f"Text {s!r} cannot fit {max_width:.2f} units at a readable size; shorten it.")


def phrase(*parts, buff=0.22):
    """Text and code pieces on one line."""
    return VGroup(*parts).arrange(RIGHT, buff=buff)


def column(*mobs, buff=0.25):
    """Mobjects under one another, left edges aligned."""
    return VGroup(*mobs).arrange(DOWN, buff=buff, aligned_edge=LEFT)


def place(mob, left=None, top=None, x=None, y=None):
    """Put ``mob`` by its left edge / top edge, or by its centre."""
    if x is not None:
        mob.set_x(x)
    if y is not None:
        mob.set_y(y)
    if left is not None:
        mob.shift(RIGHT * (left - mob.get_left()[0]))
    if top is not None:
        mob.shift(UP * (top - mob.get_top()[1]))
    return mob


def hl(mob, scale=1.12):
    """Highlight a text or an arrow for a moment."""
    return Indicate(mob, color=FLASH, scale_factor=scale)


def ring(mob):
    """Highlight a box for a moment (a frame that draws itself and fades)."""
    return Circumscribe(mob, color=FLASH, buff=0.1, fade_out=True, stroke_width=5)


def tick(size=0.3, color=GOOD):
    t = VMobject(stroke_color=color, stroke_width=6)
    t.set_points_as_corners([np.array([-0.5, 0.0, 0.0]), np.array([-0.12, -0.4, 0.0]), np.array([0.5, 0.45, 0.0])])
    return t.scale(size)


def bullets(items, size=LABEL, buff=0.25):
    """Rows of a blue dot and one line each. ``items`` are strings or ready-made mobjects."""
    rows = VGroup()
    for item in items:
        body = text(item, size) if isinstance(item, str) else item
        rows.add(VGroup(Dot(radius=0.07, color=BLUE), body).arrange(RIGHT, buff=0.3))
    return rows.arrange(DOWN, buff=buff, aligned_edge=LEFT)


# ==================================================== diagram pieces ====

class Listing(VGroup):
    """A program listing: one Text per line, indentation kept, blank lines as half gaps."""

    def __init__(self, src, size=CODE, color=INK):
        super().__init__()
        unit = code("M" * 10, size).width / 10
        step, y = size * 0.0175, 0.0
        self.base, self.lit = color, None
        for raw in src.strip("\n").split("\n"):
            if not raw.strip():
                y -= step / 2
                continue
            line = code(raw.strip() + "|", size, color)        # the bar gives every line the same height
            line.move_to(UP * y).align_to(RIGHT * (len(raw) - len(raw.lstrip())) * unit, LEFT)
            line.remove(line[-1])
            self.add(line)
            y -= step
        self.lines = list(self.submobjects)

    def focus(self, i, color=FLASH):
        """Animations that light line ``i`` (None: no line) and put the last lit line back."""
        anims = []
        if self.lit is not None and self.lit != i:
            anims.append(self.lines[self.lit].animate.set_color(self.base))
        if i is not None and self.lit != i:
            anims.append(self.lines[i].animate.set_color(color))
        self.lit = i
        return anims


class Node(VGroup):
    """A list node: a data part (blue) and a link part (brown).

    ``mark`` is what the link part shows: "dot" (it points somewhere), "null" or None (empty).
    ``link=False`` draws the data part only; ``grow()`` adds the link part later."""

    def __init__(self, value, mark="dot", link=True, dw=1.0, lw=1.05, h=0.85, size=BODY):
        super().__init__()
        self.data = Rectangle(width=dw, height=h, stroke_color=BLUE, stroke_width=3, fill_color=FILL, fill_opacity=1)
        self.link = Rectangle(width=lw, height=h, stroke_color=BROWN, stroke_width=3, fill_color=FILL, fill_opacity=1)
        self.val = code(str(value), size, INK).move_to(self.data)
        self.mark = None
        self.add(self.data, self.val)
        self.link.next_to(self.data, RIGHT, buff=0)
        if link:
            self.add(self.link)
            if mark:
                self.set_mark(mark)

    def grow(self):
        """The link part appears beside the data part (where the node is now)."""
        self.link.next_to(self.data, RIGHT, buff=0)
        self.add(self.link)
        return FadeIn(self.link, shift=RIGHT * 0.15)

    def set_mark(self, kind):
        """Fill the link part; returns the new mark (fade it in)."""
        if kind == "null":
            self.mark = code("NULL", MIN_FONT, BROWN).move_to(self.link)
        else:
            self.mark = Dot(self.link.get_center(), radius=0.075, color=BROWN)
        self.add(self.mark)
        return self.mark


def link_arrow(a, b, color=BROWN):
    """The arrow from the link part of ``a`` to node ``b``."""
    return Arrow(a.link.get_center(), b.data.get_left() + LEFT * 0.06, buff=0, color=color, stroke_width=4,
                 tip_length=0.22)


def chain(values, x=0.0, y=0.0, gap=1.0, last="null", **node_args):
    """Nodes in a row with their link arrows. Returns VGroup(nodes, arrows) with ``.nodes`` and ``.arrows``."""
    nodes = VGroup(*[Node(v, "dot", **node_args) for v in values[:-1]],
                   Node(values[-1], last, **node_args))
    nodes.arrange(RIGHT, buff=gap).move_to(RIGHT * x + UP * y)
    arrows = VGroup(*[link_arrow(a, b) for a, b in zip(nodes, nodes[1:])])
    group = VGroup(nodes, arrows)
    group.nodes, group.arrows = nodes, arrows
    return group


def pointer(name, node, color=BLUE, side=UP):
    """A named pointer variable resting on the data part of ``node``."""
    at = node.data.get_edge_center(side)
    arrow = Arrow(at + side * 0.56, at + side * 0.08, buff=0, color=color, stroke_width=4, tip_length=0.2)
    label = code(name, LABEL, color).next_to(arrow, side, buff=0.08)
    return VGroup(label, arrow)


class Options(VGroup):
    """Answer options A to D. ``items`` are (letter, value, is_code)."""

    def __init__(self, items, size=LABEL, across=False):
        super().__init__()
        self.rows = {}
        for letter, value, is_code in items:
            row = VGroup(text(letter + ".", size, BLUE, BOLD), (code if is_code else text)(value, size, INK))
            row.arrange(RIGHT, buff=0.3)
            self.rows[letter] = row
            self.add(row)
        self.across = across
        if across:
            self.arrange(RIGHT, buff=0.8)
        else:
            self.arrange(DOWN, buff=0.3, aligned_edge=LEFT)

    def right(self, letter):
        """The answer turns green with a tick; the other options go grey."""
        row = self.rows[letter]
        mark = tick().next_to(row, UP, buff=0.14) if self.across else tick().next_to(row, RIGHT, buff=0.22)
        return ([row.animate.set_color(GOOD), FadeIn(mark, scale=0.6)]
                + [r.animate.set_color(MUTED) for name, r in self.rows.items() if name != letter])

    def strike(self, letter):
        row = self.rows[letter]
        return Create(Line(row.get_left() + LEFT * 0.08, row.get_right() + RIGHT * 0.08, color=BAD, stroke_width=3))


# ============================================================ the cast ====

SKIN = "#F2D0B0"               # characters use neutral tones plus their shirt colour
HAIR = "#4E3B2A"
LIPS = "#3A1F1F"
SHIRT_T = "#8C6239"            # the teacher wears brown
SHIRT_S = "#1C758A"            # the student wears blue
RING_ON = INK
RING_OFF = "#3A3A3A"


class Face(VGroup):
    """A drawn character: head, hair, eyes, brows, mouth and shoulders.

    ``look_to(name)`` returns the animations for a change of expression;
    ``talk(on)`` lights the ring of the speaker."""

    LOOKS = {"neutral": ("soft", "flat"), "smile": ("smile", "flat"), "happy": ("open", "up"),
             "ask": ("small", "one_up"), "think": ("flat", "down"), "confused": ("wavy", "tilt"),
             "surprised": ("o", "up"), "oops": ("frown", "tilt")}

    def __init__(self, r=FACE_R, kind="teacher", look="neutral"):
        super().__init__()
        self.r, self.kind = r, kind
        shirt = SHIRT_T if kind == "teacher" else SHIRT_S
        self.head = Circle(radius=r, stroke_color="#B89A7C", stroke_width=2, fill_color=SKIN, fill_opacity=1)
        self.body = Arc(radius=r * 1.3, start_angle=0, angle=PI, stroke_color=shirt, stroke_width=2,
                        fill_color=shirt, fill_opacity=1)
        self.body.next_to(self.head, DOWN, buff=-r * 0.3)
        self.ring = Circle(radius=r * 1.2, stroke_color=RING_OFF, stroke_width=3)
        hair = Arc(radius=r, start_angle=PI * 0.1, angle=PI * 0.8, stroke_width=0, fill_color=HAIR, fill_opacity=1)
        extras = VGroup(hair)
        if kind == "teacher":           # short hair and glasses
            for sx in (-1, 1):
                extras.add(Circle(radius=r * 0.2, stroke_color=HAIR, stroke_width=2).move_to(self.at(sx * 0.34, 0.06)))
            extras.add(Line(self.at(-0.14, 0.06), self.at(0.14, 0.06), stroke_color=HAIR, stroke_width=2))
        else:                           # a ponytail
            extras.add(Ellipse(width=r * 0.5, height=r * 0.95, stroke_width=0, fill_color=HAIR,
                               fill_opacity=1).move_to(self.at(0.95, 0.35)))
        self.eyes = VGroup(*[Dot(self.at(sx * 0.34, 0.06), radius=r * 0.085, color=LIPS) for sx in (-1, 1)])
        self.mouth = self._mouth("soft")
        self.brow_l, self.brow_r = self._brows("flat")
        self.add(self.body, self.ring, self.head, extras, self.eyes, self.brow_l, self.brow_r, self.mouth)
        self.now = None
        self.play_look(look)

    def at(self, x, y):
        """A point on the face, in head radii from its centre."""
        return self.head.get_center() + self.r * np.array([x, y, 0.0])

    def _mouth(self, kind):
        a, b = self.at(-0.32, -0.42), self.at(0.32, -0.42)
        if kind == "smile":
            m = ArcBetweenPoints(a, b, angle=PI / 2)
        elif kind == "soft":
            m = ArcBetweenPoints(self.at(-0.22, -0.44), self.at(0.22, -0.44), angle=PI / 4)
        elif kind == "open":
            m = ArcBetweenPoints(a, b, angle=PI * 0.85).set_fill(LIPS, 1)
        elif kind == "frown":
            m = ArcBetweenPoints(self.at(-0.26, -0.56), self.at(0.26, -0.56), angle=-PI / 2)
        elif kind == "o":
            m = Circle(radius=self.r * 0.15).move_to(self.at(0, -0.5)).set_fill(LIPS, 1)
        elif kind == "wavy":
            m = VMobject().set_points_smoothly([a, self.at(-0.1, -0.36), self.at(0.1, -0.5), b])
        elif kind == "small":
            m = Line(self.at(-0.14, -0.46), self.at(0.14, -0.46))
        else:
            m = Line(self.at(-0.24, -0.46), self.at(0.24, -0.46))
        return m.set_stroke(LIPS, 3)

    def _brows(self, kind):
        lift = 0.12 if kind == "up" else 0.0
        inner = {"down": -0.08, "tilt": 0.1}.get(kind, 0.0)
        y = 0.4 + lift
        left = Line(self.at(-0.52, y), self.at(-0.18, y + inner))
        right = Line(self.at(0.18, y + inner + (0.06 if kind == "one_up" else 0)),
                     self.at(0.52, y + (0.2 if kind == "one_up" else 0)))
        return left.set_stroke(HAIR, 3), right.set_stroke(HAIR, 3)

    def play_look(self, name):
        """Set the expression at once (before the face is on screen)."""
        mouth, brows = self.LOOKS[name]
        left, right = self._brows(brows)
        self.mouth.become(self._mouth(mouth))
        self.brow_l.become(left)
        self.brow_r.become(right)
        self.now = name
        return self

    def look_to(self, name):
        if self.now == name:
            return []
        mouth, brows = self.LOOKS[name]
        left, right = self._brows(brows)
        self.now = name
        return [self.mouth.animate.become(self._mouth(mouth)), self.brow_l.animate.become(left),
                self.brow_r.animate.become(right)]

    def talk(self, on):
        return self.ring.animate.set_stroke(RING_ON if on else RING_OFF, width=6 if on else 3)


# ============================================================= lesson ====

PROGRAM = """
struct node {
    int data;
    struct node *next;
};

struct node c = {30, NULL};
struct node b = {20, &c};
struct node a = {10, &b};

struct node *head = &a;
printf("%d", head->next->data);
"""
P_NEXT, P_HEAD, P_PRINT = 2, 7, 8           # line numbers in PROGRAM (blank lines not counted)

STRUCT = """
struct node {
    int data;
    struct node *next;
};
"""

LOOP = """
struct node *p = head;
int count = 0;

while (p->next != NULL) {
    count++;
    p = p->next;
}

printf("%d", count);
"""
L_P, L_COUNT, L_WHILE, L_INC, L_STEP, L_CLOSE, L_PRINT = range(7)

VALUES = (10, 20, 30)
MARKS = [72, 85, 91, 64, 78]                # the array of the opening problem
ROLLS = [101, 102, 104, 105, 106]
NEW_ROLL, NEW_MARK = 103, 88

# the two questions, worked out
assert VALUES[1] == 20                      # head->next->data: one link from the first node, then its data
_count, _at = 0, 0
while _at + 1 < len(VALUES):                # while (p->next != NULL)
    _count, _at = _count + 1, _at + 1
assert _count == 2 and _at == len(VALUES) - 1
assert sorted(ROLLS + [NEW_ROLL]).index(NEW_ROLL) == 2 and len(ROLLS) - 2 == 3     # slot 2, three records shift


class ListsClassroomMovie(LMSScene):
    lesson_title = "Lists - The Classroom Movie"

    def construct(self):
        self.camera.background_color = BG
        self.cast = None
        self.title_bar = None
        self.spoken = None
        self.talking = None

        self.connection()
        self.why_ccat()
        self.what_is_a_list()
        self.the_chain()
        self.loop_challenge()
        self.null_link()
        self.real_life()
        self.takeaway()
        self.summary()
        self.next_session()

    # ------------------------------------------------------ stage helpers --

    def kept(self):
        """Family of what stays through a scene change: the two characters and the heading."""
        keep = set()
        for mob in (self.cast, self.title_bar):
            if mob is not None:
                keep.update(mob.get_family())
        return keep

    def wipe(self, run_time=0.6):
        """Clear the board and the spoken line."""
        keep = self.kept()
        parts = [p for m in self.mobjects for p in m.family_members_with_points() if p not in keep]
        if parts:
            self.play(FadeOut(Group(*parts)), run_time=run_time)
        for mob in list(self.mobjects):
            if mob not in keep and not any(p in keep for p in mob.get_family()):
                self.remove(mob)
        self.spoken = None

    def heading(self, s):
        """The scene heading: a title with a blue rule, between the two characters."""
        title = text(s, HEAD, INK, BOLD)
        if title.width > HEAD_W:
            raise ValueError(f"Heading {s!r} is {title.width:.2f} wide; the top band has {HEAD_W:.2f}.")
        rule = Line(LEFT, RIGHT, color=BLUE, stroke_width=3).set_width(title.width).next_to(title, DOWN, buff=0.14)
        bar = VGroup(title, rule).move_to(UP * HEAD_Y)
        anims = [FadeIn(bar, shift=DOWN * 0.2)]
        if self.title_bar is not None:
            anims.append(FadeOut(self.title_bar, shift=DOWN * 0.2))
        self.play(*anims, run_time=0.6)
        self.title_bar = bar

    def begin(self, sid, title, head):
        self.scene_start(sid, title=title)
        self.heading(head)

    def finish(self, sid):
        self.wipe()
        self.scene_end(sid)

    def fit(self, *mobs, top=BOARD_TOP):
        """Layout guard: every mobject must lie on the board."""
        for mob in mobs:
            if (mob.get_left()[0] < -EDGE_X - 1e-6 or mob.get_right()[0] > EDGE_X + 1e-6
                    or mob.get_bottom()[1] < FLOOR - 1e-6 or mob.get_top()[1] > top + 1e-6):
                raise ValueError(f"{mob!r} leaves the board: x {mob.get_left()[0]:.2f}..{mob.get_right()[0]:.2f}, "
                                 f"y {mob.get_bottom()[1]:.2f}..{mob.get_top()[1]:.2f} (top allowed {top:.2f}).")
        return mobs[0]

    def apart(self, *mobs, gap=0.05):
        """Layout guard: the bounding boxes of ``mobs`` must not touch."""
        for i, a in enumerate(mobs):
            for b in mobs[i + 1:]:
                if (a.get_right()[0] + gap > b.get_left()[0] and b.get_right()[0] + gap > a.get_left()[0]
                        and a.get_top()[1] + gap > b.get_bottom()[1] and b.get_top()[1] + gap > a.get_bottom()[1]):
                    raise ValueError(f"{a!r} and {b!r} overlap.")

    # ------------------------------------------------------------ the cast --

    def enter_cast(self):
        """The teacher (top left) and the student (top right) come in and stay for the whole video."""
        t, s = Face(FACE_R, "teacher"), Face(FACE_R, "student")
        t.shift(UP * (TOP - t.get_top()[1]) + RIGHT * (-EDGE_X - t.get_left()[0]))
        s.shift(UP * (TOP - s.get_top()[1]) + RIGHT * (EDGE_X - s.get_right()[0]))
        self.cast, self.teacher_face, self.student_face = VGroup(t, s), t, s
        self.play(FadeIn(t, shift=RIGHT * 0.4), FadeIn(s, shift=LEFT * 0.4), run_time=0.6)

    def face(self, who):
        return self.teacher_face if who == "T" else self.student_face

    def react(self, who, look):
        """Animations that change one character's expression (use inside a cue)."""
        return self.face(who).look_to(look)

    def speaker(self, who, look=None, other=None):
        """Show who speaks: "N" narrator (both listen), "T" teacher, "S" student.

        ``look`` is the speaker's expression, ``other`` the listener's."""
        t, s = self.teacher_face, self.student_face
        t_look = (look or "smile") if who == "T" else (other or "neutral") if who == "S" else "neutral"
        s_look = (look or "smile") if who == "S" else (other or "neutral") if who == "T" else "neutral"
        anims = [*t.look_to(t_look), *s.look_to(s_look)]
        if self.talking != who:
            anims += [t.talk(who == "T"), s.talk(who == "S")]
            self.talking = who
        if anims:
            self.play(*anims, run_time=0.25)

    def show_line(self, who, s):
        """The strip under the heading: a teacher question or a student line (None clears it)."""
        new = None
        if s:
            tag = text("Teacher" if who == "T" else "Student", SMALL, BROWN if who == "T" else BLUE, BOLD)
            body = fitted_text(s, STRIP_W - tag.width - 0.35, LABEL, INK, max_lines=2,
                               slant=ITALIC if who == "S" else NORMAL)
            new = VGroup(tag, body).arrange(RIGHT, buff=0.35, aligned_edge=UP).move_to(UP * STRIP_Y)
            if new.height > STRIP_TOP - STRIP_BOTTOM + 1e-6:
                raise ValueError(f"Spoken line {s!r} is too tall for the strip ({new.height:.2f}); shorten it.")
            self.keep_clear(new, f"spoken line {s!r}")
        anims = ([FadeOut(self.spoken)] if self.spoken is not None else []) + ([FadeIn(new)] if new is not None else [])
        if anims:
            self.play(*anims, run_time=0.3)
        self.spoken = new

    def keep_clear(self, mob, what):
        """Fail if anything on the board reaches into ``mob``'s area."""
        l, r = mob.get_left()[0], mob.get_right()[0]
        b, t = mob.get_bottom()[1], mob.get_top()[1]
        skip = self.kept()
        if self.spoken is not None:
            skip.update(self.spoken.get_family())
        for top in self.mobjects:
            for part in top.family_members_with_points():
                if part in skip:
                    continue
                if (part.get_right()[0] > l + 0.02 and part.get_left()[0] < r - 0.02
                        and part.get_top()[1] > b + 0.02 and part.get_bottom()[1] < t - 0.02):
                    raise ValueError(f"The {what} would cover {part!r}.")

    def countdown(self, seconds):
        """Thinking time: a bar under the heading runs out."""
        bar = Line(LEFT * 1.6, RIGHT * 1.6, color=FLASH, stroke_width=5).move_to(UP * TIMER_Y)
        self.play(FadeIn(bar), run_time=0.3)
        self.play(Uncreate(bar), run_time=max(0.5, seconds - 0.3), rate_func=linear)

    # ------------------------------------------------- narration drivers --

    def cue(self, n, word):
        """Wait for ``word`` (or ``(word, occurrence)``) in narration ``n``."""
        spoken, occ = (word, 1) if isinstance(word, str) else word
        if n.estimated and not spoken.replace(" ", "").isalpha():
            raise ValueError(f"Anchor {spoken!r} must be plain words (no apostrophes, hyphens or digits).")
        try:
            self.at_word(n, spoken, occ)
        except ValueError:
            if n.estimated:
                raise                     # dry run: a wrong anchor is a bug in this file
            # with real audio the aligner may spell a word differently: just carry on

    def run(self, n, cues, think=0.0):
        """Play ``(word, what)`` pairs in spoken order, then hold until ``n`` ends.

        ``what`` is an animation, a list of animations, or a function that returns
        one (or plays things itself and returns None). ``think`` seconds of the
        pause after ``n`` are shown as a countdown."""
        for word, what in cues:
            if word:
                self.cue(n, word)
            if isinstance(what, (types.FunctionType, types.MethodType)):
                what = what()
            anims = self.flat(what) if what is not None else []
            if anims:
                self.play(*anims)
        if think:
            self.wait_for_narration(n, include_pause=False)
            self.countdown(think)
        self.wait_for_narration(n)
        return n

    @classmethod
    def flat(cls, what):
        """Animations from a single animation or a (nested) list of them."""
        if not isinstance(what, (list, tuple)):
            return [what]
        return [a for item in what for a in cls.flat(item)]

    def say(self, who, nid, spoken, cues, look=None, other=None, shown=None, think=0.0):
        self.speaker(who, look, other)
        self.show_line(who, shown)
        n = self.narrate(id=nid, text=spoken, voice=VOICES[who], subtitle=True,
                         pause_after=think if think else TURN_PAUSE)
        return self.run(n, cues, think)

    def N(self, nid, spoken, *cues):
        """Narrator: introduces, connects, explains. Both characters listen."""
        return self.say("N", nid, spoken, cues)

    def T(self, nid, spoken, *cues, look="smile", other=None, think=0.0):
        """Teacher statement."""
        return self.say("T", nid, spoken, cues, look, other, None, think)

    def Q(self, nid, spoken, *cues, shown=None, look="ask", other="think", think=0.0):
        """Teacher question: spoken, and shown in the strip."""
        return self.say("T", nid, spoken, cues, look, other, shown or spoken, think)

    def S(self, nid, spoken, *cues, shown=None, look="smile", other=None):
        """Student line: own voice, shown in the strip."""
        return self.say("S", nid, spoken, cues, look, other, shown or spoken)

    def hop(self, dot, nodes, run_time=0.55):
        """A marker under the nodes follows the links, one node at a time."""
        for a, b in zip(nodes, nodes[1:]):
            self.play(dot.animate(path_arc=PI / 2).shift(RIGHT * (b.data.get_x() - a.data.get_x())), run_time=run_time)

    # ============================================ 1. THE CONNECTION ========

    def connection(self):
        self.scene_start("S01_connection", title="The Connection")

        crumb = text("CDAC C-CAT Preparation  ›  Data Structures  ›  Lists", SMALL, MUTED)
        title = text("Lists", TITLE, INK, BOLD)
        rule = Line(LEFT * 1.3, RIGHT * 1.3, color=BLUE, stroke_width=4)
        before = text("Previous topic:  Arrays", LABEL, BROWN)
        card = VGroup(crumb, title, rule, before).arrange(DOWN, buff=0.4).move_to(DOWN * 0.6)
        self.fit(card)
        self.play(FadeIn(crumb), FadeIn(title, shift=UP * 0.2), Create(rule), run_time=1.0)
        self.play(FadeIn(before, shift=UP * 0.15), run_time=0.6)
        self.enter_cast()
        self.heading("From arrays to lists")

        # the array of marks: six boxes, five in use, kept in roll-number order
        boxes = VGroup(*[Square(1.0, stroke_color=BLUE, stroke_width=3, fill_color=FILL, fill_opacity=1)
                         for _ in range(6)]).arrange(RIGHT, buff=0).move_to(RIGHT * 0.6 + DOWN * 1.0)
        index = VGroup(*[code(str(k), SMALL, MUTED).next_to(b, DOWN, buff=0.18) for k, b in enumerate(boxes)])
        marks = [code(str(m), BODY, INK).move_to(b) for m, b in zip(MARKS, boxes)]
        rolls = [code(str(r), SMALL, MUTED).next_to(b, UP, buff=0.18) for r, b in zip(ROLLS, boxes)]
        records = [VGroup(r, m) for r, m in zip(rolls, marks)]
        tags = [text(s, SMALL, MUTED).next_to(boxes, LEFT, buff=0.4).set_y(ref.get_y())
                for s, ref in (("Roll no.", rolls[0]), ("Marks", boxes), ("Index", index))]
        new = VGroup(code(str(NEW_ROLL), SMALL, BROWN).next_to(boxes[2], UP, buff=0.18),
                     code(str(NEW_MARK), BODY, BROWN).move_to(boxes[2])).shift(LEFT * 0.5 + UP * 1.25)
        point = Arrow(new.get_bottom() + DOWN * 0.08, np.array([new.get_x(), boxes.get_top()[1] + 0.06, 0.0]), buff=0,
                      color=BROWN, stroke_width=4, tip_length=0.18)
        note_a = text("3 records shifted to insert 1", LABEL, BROWN).move_to(DOWN * 2.8)
        note_b = text("5,000 records shifted to insert 1", LABEL, BROWN, BOLD).move_to(DOWN * 2.8)
        decl = phrase(code("int marks[6];", LABEL), text("Fixed size: 6 elements, no more", LABEL, BROWN),
                      buff=0.5).move_to(DOWN * 2.8)
        ghost = VGroup(DashedVMobject(Square(1.0, stroke_color=BAD, stroke_width=3), num_dashes=20))
        ghost.add(Line(UL * 0.22, DR * 0.22, color=BAD, stroke_width=4),
                  Line(UR * 0.22, DL * 0.22, color=BAD, stroke_width=4))
        ghost.next_to(boxes, RIGHT, buff=0.25)
        needs = phrase(text("It must be able to grow", LABEL, BLUE, BOLD),
                       text("Insert without shifting the rest", LABEL, BLUE, BOLD), buff=0.9).move_to(DOWN * 2.8)
        hint_y = rolls[0].get_top()[1] + 0.25
        hints = [CurvedArrow(np.array([a.get_x(), hint_y, 0.0]), np.array([b.get_x(), hint_y, 0.0]), angle=-PI / 2,
                             color=BROWN, stroke_width=3, tip_length=0.16) for a, b in zip(boxes, boxes[1:])]
        big = text("Lists", TITLE, BLUE, BOLD).move_to(DOWN * 0.9)
        under = Line(LEFT, RIGHT, color=BROWN, stroke_width=4).set_width(big.width).next_to(big, DOWN, buff=0.2)
        self.fit(boxes, index, new, tags[0], ghost, note_b, decl, needs, *rolls)

        def make_room():
            self.play(FadeOut(point), run_time=0.3)
            for rec in reversed(records[2:]):
                self.play(rec.animate.shift(RIGHT * 1.0), run_time=0.45)
            self.play(new.animate.shift(RIGHT * 0.5 + DOWN * 1.25), run_time=0.6)

        self.T("s1_01", "Last time, we learned about arrays. One name, many same-type elements, and an index that takes "
                        "us directly to any element.",
               ("arrays", lambda: [FadeOut(card), FadeIn(VGroup(*boxes[:5], *marks, *index[:5]), shift=UP * 0.2)]),
               ("index", lambda: hl(VGroup(*index[:5]))),
               ("directly", lambda: [ring(boxes[3]), hl(index[3])]))
        self.T("s1_02", "But let me ask you something. Remember our college management system? We stored the students' "
                        "marks in an array, in roll-number order.",
               ("college", lambda: FadeIn(VGroup(tags[1], tags[2]))),
               ("order", lambda: [FadeIn(VGroup(*rolls, tags[0]), shift=DOWN * 0.15), FadeIn(VGroup(boxes[5], index[5]))]),
               look="ask")
        self.T("s1_03", "Now a new student joins in the middle of the semester. Their roll number falls right between "
                        "two existing students.",
               ("joins", lambda: FadeIn(new, shift=DOWN * 0.3)),
               ("between", lambda: [hl(rolls[1]), hl(rolls[2])]))
        self.Q("s1_04", "Where does the new record go?")
        self.S("s1_05", "In the middle? But the middle is already occupied.",
               ("middle", lambda: GrowArrow(point)),
               ("occupied", lambda: [self.react("S", "confused"), ring(boxes[2])]), look="ask")
        self.Q("s1_06", "Exactly. So what must happen to every element after that position?",
               ("after", lambda: hl(VGroup(*marks[2:]))),
               shown="What must happen to every element after that position?")
        self.S("s1_07", "They all have to move one place to the right.",
               ("move", make_room), (None, lambda: FadeIn(note_a, shift=UP * 0.15)))
        self.Q("s1_08", "And if there are five thousand records after that position?",
               shown="And if 5,000 records come after that position?")
        self.S("s1_09", "Then we shift five thousand records just to add one student? That sounds like a lot of work!",
               ("thousand", lambda: [FadeOut(note_a), FadeIn(note_b)]),
               shown="We shift 5,000 records just to add one student?", look="surprised")
        self.T("s1_10", "And here is a second problem. What if the array is already full? In C, a declared array has a "
                        "fixed number of elements. There is no empty box waiting at the end.",
               ("full", lambda: ring(boxes)),
               ("fixed", lambda: [FadeOut(note_b), FadeIn(decl)]),
               ("empty", lambda: FadeIn(ghost)), other="think")
        self.T("s1_11", "So we need a way to organize a sequence that can grow, and that lets us insert an element "
                        "without moving all the others.",
               ("grow", lambda: [FadeOut(VGroup(decl, ghost)), FadeIn(needs[0])]),
               ("insert", lambda: FadeIn(needs[1])))
        self.S("s1_12", "Can the elements stay where they are, and simply tell us who comes next?",
               ("next", lambda: LaggedStart(*[Create(h) for h in hints], lag_ratio=0.3)), look="think")
        self.N("s1_13", "That is the question that leads us to today's concept: lists.",
               (None, self.wipe),
               ("lists", lambda: [FadeIn(big, scale=1.15), Create(under)]))

        self.finish("S01_connection")

    # ================================== 2. WHY LISTS MATTER IN C-CAT =======

    def why_ccat(self):
        self.begin("S02_why_ccat", "Why Lists Matter in C-CAT", "A C-CAT style question")

        mini = chain(VALUES, y=0.35, gap=0.7, dw=0.8, lw=0.95, h=0.75, size=LABEL)
        skills = column(*[phrase(text(f"{k}.", BODY, BLUE, BOLD), text(s, BODY)) for k, s in
                          enumerate(("Read the program", "Follow the links", "Predict the output"), 1)], buff=0.32)
        place(skills, x=0.0, top=-0.9)
        self.fit(mini, skills)

        prog = Listing(PROGRAM)
        place(prog, left=-EDGE_X + 0.3, top=BOARD_HIGH - 0.35)
        ask = text("What will it print?", BODY, INK, BOLD)
        opts = Options([("A", "10", True), ("B", "20", True), ("C", "30", True), ("D", "A memory address", False)], BODY)
        side = column(ask, opts, buff=0.5)
        place(side, left=1.3, y=-0.4)
        self.fit(prog, side, top=BOARD_HIGH)
        self.apart(prog, side)

        todo = column(*[text(s, BODY) for s in ("What is a list?", "What does a node contain?",
                                                "How does one node lead to the next?")], buff=0.4)
        place(todo, x=0.0, y=-1.0)

        self.N("s2_01", "Now, here is something important for your C-DAC C-CAT preparation. Knowing that a list is a "
                        "chain of nodes is not enough. You should also be able to read a short program, follow the "
                        "links from one node to the next, and predict the output.",
               ("chain", lambda: FadeIn(mini, shift=UP * 0.2)),
               ("read", lambda: FadeIn(skills[0], shift=RIGHT * 0.2)),
               ("follow", lambda: [FadeIn(skills[1], shift=RIGHT * 0.2), hl(mini.arrows)]),
               ("predict", lambda: FadeIn(skills[2], shift=RIGHT * 0.2)))
        self.T("s2_02", "Let's try a question. Consider this C program.",
               (None, self.wipe),
               ("Consider", lambda: LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in prog.lines], lag_ratio=0.15,
                                                run_time=2.4)))
        self.T("s2_03", "What will it print? Take a moment before answering.",
               ("print", lambda: FadeIn(ask)),
               ("moment", lambda: LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in opts], lag_ratio=0.4,
                                              run_time=1.6)),
               look="ask", other="think", think=6.0)
        self.T("s2_04", "It is tempting to choose ten, because head points to the first node. Another possibility is a "
                        "memory address, because next stores an address.",
               ("tempting", lambda: hl(opts.rows["A"])),
               ("head", lambda: prog.focus(P_HEAD)),
               ("memory", lambda: [prog.focus(None), hl(opts.rows["D"])]),
               ("next", lambda: prog.focus(P_NEXT, BROWN)), other="think")
        self.T("s2_05", "But which option is actually correct?",
               ("correct", lambda: [prog.focus(None), hl(ask, 1.06)]), look="ask", other="confused")
        self.N("s2_06", "To solve this confidently, we need to understand what a list is, what a node contains, and "
                        "how one node leads us to the next. Let's build that understanding from the beginning.",
               (None, self.wipe),
               ("list", lambda: FadeIn(todo[0], shift=UP * 0.15)),
               ("contains", lambda: FadeIn(todo[1], shift=UP * 0.15)),
               ("leads", lambda: FadeIn(todo[2], shift=UP * 0.15)))

        self.finish("S02_why_ccat")

    # ============================================ 3. WHAT IS A LIST? =======

    def what_is_a_list(self):
        self.begin("S03_what_is_a_list", "What Is a List?", "What is a list?")

        nodes = [Node(v, link=False) for v in VALUES]
        for k, n in enumerate(nodes):
            n.move_to(RIGHT * (k - 1) + UP * 0.3)
        extra = Node(40, link=False).move_to(RIGHT * 2 + UP * 0.3)
        spots = [LEFT * 4.6 + UP * 0.3, LEFT * 0.3 + DOWN * 0.7, RIGHT * 4.0 + UP * 0.3]     # where the nodes land
        defn = VGroup(text("List", BODY, BLUE, BOLD),
                      text("A linear sequence of elements that can grow and shrink", LABEL)).arrange(DOWN, buff=0.2)
        defn.move_to(DOWN * 2.4)
        side_by_side = text("Stored in an array: side by side", LABEL, MUTED).move_to(DOWN * 0.75)
        struct = Listing(STRUCT)
        place(struct, left=-EDGE_X + 0.35, top=-1.5)
        memory = column(text("Array:  consecutive memory locations", LABEL, MUTED),
                        text("Linked list:  nodes anywhere in memory", LABEL, BLUE), buff=0.3)
        place(memory, left=-0.9, top=-1.95)
        self.fit(defn, struct, memory)
        self.apart(struct, memory)
        made = {}                                       # things that exist only once the nodes have landed

        def drift():
            return [FadeOut(side_by_side)] + [n.animate.move_to(p) for n, p in zip(nodes, spots)]

        def two_parts():
            made["tag"] = text("Node", LABEL, INK, BOLD).next_to(nodes[0].data, UP, buff=0.16)
            return [n.grow() for n in nodes]

        def name_data():
            made["data"] = text("Data", SMALL, BLUE, BOLD).next_to(nodes[0].data, DOWN, buff=0.15)
            return [FadeIn(made["data"]), ring(nodes[0].data)]

        def name_link():
            made["link"] = text("Link", SMALL, BROWN, BOLD).next_to(nodes[0].link, DOWN, buff=0.15)
            return [FadeIn(made["link"]), ring(nodes[0].link)]

        def connect():
            made["arrows"] = [link_arrow(a, b) for a, b in zip(nodes, nodes[1:])]
            return ([FadeIn(nodes[0].set_mark("dot")), FadeIn(nodes[1].set_mark("dot"))]
                    + [GrowArrow(a) for a in made["arrows"]])

        def addresses():
            made["where"] = VGroup(*[code(f"Address {a}", SMALL, MUTED).next_to(n, UP, buff=0.15)
                                     for a, n in zip((500, 120, 860), nodes)])
            self.fit(made["where"])
            return [FadeOut(made["tag"]), FadeIn(made["where"], shift=UP * 0.1)]

        def where_first():
            made["q1"] = text("?", TITLE, FLASH, BOLD).next_to(nodes[0], LEFT, buff=0.3)
            self.fit(made["q1"])
            return FadeIn(made["q1"], scale=1.3)

        def where_end():
            made["q2"] = text("?", BODY, FLASH, BOLD).move_to(nodes[2].link)
            return FadeIn(made["q2"], scale=1.3)

        self.play(LaggedStart(*[FadeIn(n, shift=UP * 0.2) for n in nodes], lag_ratio=0.2), run_time=0.8)
        self.T("s3_01", "A list is a linear collection of elements arranged in a sequence, where elements can be "
                        "inserted or removed, so the collection can grow and shrink.",
               ("sequence", lambda: FadeIn(defn, shift=UP * 0.15)),
               ("inserted", lambda: FadeIn(extra, shift=LEFT * 0.3)),
               ("shrink", lambda: FadeOut(extra, shift=RIGHT * 0.3)))
        self.T("s3_02", "There is more than one way to store a list. We could keep it inside an array. Or we could "
                        "store it as a linked list, and that is the form we will study today.",
               ("array", lambda: FadeIn(side_by_side)),
               ("linked", drift))
        self.T("s3_03", "In a linked list, each element lives in its own small unit called a node. And every node has "
                        "two parts.",
               ("two", two_parts),
               (None, lambda: FadeIn(made["tag"])))
        self.T("s3_04", "The first part stores the data, the actual value. The second part stores a link, the address "
                        "of the next node in the sequence.",
               ("data", name_data), ("link", name_link), ("address", connect))
        self.T("s3_05", "Look at the structure from our question. The member data holds the value. The member next is "
                        "a pointer that can hold the address of another node of the same type.",
               ("structure", lambda: [FadeOut(defn), FadeIn(struct, shift=UP * 0.15)]),
               ("data", lambda: struct.focus(1, BLUE)),
               ("next", lambda: struct.focus(2, BROWN)))
        self.S("s3_06", "So the nodes don't need to sit side by side in memory?",
               (None, addresses), look="ask")
        self.T("s3_07", "That is right. In an array, the elements occupy consecutive memory locations. In a linked "
                        "list, the nodes can be anywhere in memory, because each node remembers where the next one is.",
               ("consecutive", lambda: [struct.focus(None), FadeIn(memory[0], shift=UP * 0.15)]),
               ("anywhere", lambda: [FadeIn(memory[1], shift=UP * 0.15), hl(made["where"], 1.05)]),
               ("remembers", lambda: [hl(a) for a in made["arrows"]]), look="happy")
        self.Q("s3_08", "But here is the next question. If the nodes are scattered, how do we find the first one? And "
                        "how do we know where the list ends?",
               ("first", where_first), ("ends", where_end),
               shown="How do we find the first node? And where does the list end?")

        self.finish("S03_what_is_a_list")

    # ================================ 4. THE CHAIN: HEAD, NEXT, NULL =======

    def the_chain(self):
        self.begin("S04_chain", "The Chain: Head, Next and NULL", "The chain: head, next and NULL")

        row = chain(VALUES, y=-0.1, last=None)
        n1, n2, n3 = row.nodes
        a12, a23 = row.arrows
        head = pointer("head", n1)
        names = VGroup(*[code(s, SMALL, MUTED).next_to(n.data, DOWN, buff=0.15) for s, n in zip("abc", row.nodes)])
        facts = column(phrase(code("head", LABEL, BLUE), text("stores the address of the first node", LABEL)),
                       phrase(code("NULL", LABEL, BROWN), text("means this pointer points to no node", LABEL)), buff=0.32)
        place(facts, x=0.0, top=-1.25)
        end_tag = text("End of the list", SMALL, BROWN).next_to(n3, DOWN, buff=0.18)
        jump = CurvedArrow(n1.data.get_bottom() + DOWN * 0.1, n3.data.get_bottom() + DOWN * 0.1, angle=PI / 3,
                           color=MUTED, stroke_width=4)
        jump_tag = phrase(code("a[2]", LABEL, MUTED), text("jump straight there?", SMALL, MUTED)).move_to(DOWN * 1.85)
        walker = Dot(radius=0.12, color=FLASH).next_to(n1.data, DOWN, buff=0.2)
        no_index = text("No index: start at head and follow the links", LABEL, BLUE, BOLD).move_to(DOWN * 2.2)

        stmt = code('printf("%d", head->next->data);', LABEL)
        steps = [phrase(code("head", SMALL, BLUE), text("points to the first node, holding 10", SMALL)),
                 phrase(code("head->next", SMALL, BLUE), text("points to the second node", SMALL)),
                 phrase(code("head->next->data", SMALL, BLUE), text("is its data:  20", SMALL))]
        work = column(stmt, *steps, buff=0.26)
        place(work, left=-EDGE_X + 0.35, top=-1.1)
        arrow_note = phrase(code("->", LABEL, FLASH), text("go to the node, then pick one of its members", SMALL))
        place(arrow_note, left=-EDGE_X + 0.35, y=steps[0].get_y())
        opts = Options([("A", "10", True), ("B", "20", True), ("C", "30", True), ("D", "A memory address", False)])
        place(opts, left=2.2, top=-1.15)
        self.fit(row, head, facts, jump_tag, no_index, work, arrow_note, opts)
        self.apart(work, opts)
        self.apart(arrow_note, opts)
        self.apart(names, work)

        self.play(LaggedStart(*[FadeIn(n, shift=UP * 0.2) for n in row.nodes], *[GrowArrow(a) for a in row.arrows],
                              lag_ratio=0.15), run_time=1.2)
        self.N("s4_01", "This is where head and null come in.",
               ("head", lambda: FadeIn(head, shift=DOWN * 0.2)),
               ("null", lambda: FadeIn(n3.set_mark("null"))))
        self.T("s4_02", "The head is a pointer that stores the address of the first node. It is our entry point into "
                        "the list.",
               ("address", lambda: hl(head)),
               ("entry", lambda: FadeIn(facts[0], shift=UP * 0.15)))
        self.T("s4_03", "And the last node has nothing after it, so its link stores null, a special value meaning this "
                        "pointer points to no node.",
               ("last", lambda: ring(n3)),
               ("special", lambda: FadeIn(facts[1], shift=UP * 0.15)))
        self.T("s4_04", "Watch carefully. The first node holds ten, and its link points to the node holding twenty. "
                        "The second node holds twenty, and its link points to the node holding thirty. The third node "
                        "holds thirty, and its link is null. The list ends here.",
               ("first", lambda: ring(n1)), ("twenty", lambda: hl(a12)),
               ("second", lambda: ring(n2)), ("thirty", lambda: hl(a23)),
               ("third", lambda: ring(n3)), ("ends", lambda: [hl(n3.mark), FadeIn(end_tag)]))
        self.S("s4_05", "Wait a minute. In an array we could write A with index two, and jump straight to the third "
                        "element. Can we do that here?",
               ("jump", lambda: [FadeOut(VGroup(facts, end_tag)), Create(jump), FadeIn(jump_tag)]),
               shown="In an array we wrote a[2] and jumped to the third element. Can we do that here?", look="confused")
        self.T("s4_06", "No. A linked list has no index. To reach the third node, we must start at the head and follow "
                        "the links, one node at a time.",
               ("index", lambda: [jump.animate.set_color(BAD), jump_tag.animate.set_color(BAD)]),
               ("start", lambda: [FadeOut(VGroup(jump, jump_tag)), FadeIn(walker), hl(head)]),
               ("follow", lambda: self.hop(walker, row.nodes)),
               (None, lambda: FadeIn(no_index, shift=UP * 0.15)))
        self.T("s4_07", "Now let's return to our original question.",
               (None, lambda: FadeOut(VGroup(walker, no_index))),
               ("question", lambda: [FadeIn(stmt, shift=UP * 0.15), FadeIn(opts, shift=UP * 0.15), FadeIn(names)]))
        self.T("s4_08", "The arrow operator means: go to the node this pointer points to, and pick one of its members.",
               ("arrow", lambda: FadeIn(arrow_note, shift=RIGHT * 0.2)))
        self.T("s4_09", "Head points to the first node, the one holding ten.",
               ("first", lambda: [FadeOut(arrow_note), FadeIn(steps[0], shift=RIGHT * 0.2), ring(n1.data)]))
        self.T("s4_10", "Head arrow next is the link stored in that first node. It points to the second node.",
               ("link", lambda: [FadeIn(steps[1], shift=RIGHT * 0.2), ring(n1.link)]),
               ("second", lambda: [hl(a12), ring(n2)]))
        self.T("s4_11", "Head arrow next arrow data is the data stored in that second node. And the data in the second "
                        "node is twenty.",
               ("stored", lambda: FadeIn(steps[2], shift=RIGHT * 0.2)),
               ("twenty", lambda: [n2.data.animate.set_stroke(FLASH, 5), hl(n2.val, 1.3)]), other="think")
        self.T("s4_12", "The correct answer is option B: twenty.",
               ("answer", lambda: opts.right("B")), look="happy", other="happy")
        self.T("s4_13", "It is not an address, because the expression ends with data, not with next. We followed one "
                        "link and then read a value.",
               ("address", lambda: opts.strike("D")),
               ("ends", lambda: hl(steps[2][0], 1.06)),
               ("followed", lambda: hl(a12)),
               ("read", lambda: hl(n2.val, 1.3)))
        self.N("s4_14", "See what just happened? We did not need to memorize the answer. We followed the chain.",
               ("chain", lambda: [hl(a12), hl(a23)]))

        self.finish("S04_chain")

    # ==================================== 5. ANOTHER C-CAT CHALLENGE =======

    def loop_challenge(self):
        self.begin("S05_loop", "Another C-CAT Challenge", "Tracing a loop")

        loop = Listing(LOOP)
        place(loop, left=-EDGE_X + 0.25, top=1.2)
        opts = Options([("A", "2", True), ("B", "3", True), ("C", "4", True), ("D", "0", True)], across=True)
        place(opts, left=-EDGE_X + 0.25, y=-2.95)
        row = chain(VALUES, x=2.9, y=-0.1, gap=0.7, dw=0.8, lw=0.95)
        n1, n2, n3 = row.nodes
        a12, a23 = row.arrows
        col_x = row.get_left()[0]
        p = pointer("p", n1, FLASH)
        hop_x = n2.data.get_x() - n1.data.get_x()
        counts = [place(code(s, BODY), left=col_x, y=-1.35) for s in ("count = 0", "count = 0 + 1 = 1",
                                                                      "count = 1 + 1 = 2")]
        check = place(code("p->next != NULL ?", LABEL), left=col_x, y=-2.15)
        yes = text("Yes", LABEL, GOOD, BOLD).next_to(check, RIGHT, buff=0.4)
        no = text("No", LABEL, BROWN, BOLD).next_to(check, RIGHT, buff=0.4)
        out = place(phrase(text("Output:", BODY), code("2", BODY, FLASH)), left=col_x, y=-2.95)
        nums = VGroup(*[code(s, SMALL, FLASH).move_to([(a.link.get_right()[0] + b.data.get_left()[0]) / 2,
                                                        a.get_y() + 0.26, 0.0])
                        for s, a, b in zip("12", row.nodes, row.nodes[1:])])
        compare = VGroup(code("p->next != NULL", SMALL), text("counts the links:  2", SMALL),
                         code("p != NULL", SMALL), text("counts the nodes:  3", SMALL))
        for k, y in ((0, -1.55), (2, -2.3)):
            place(compare[k], left=col_x, y=y)
            place(compare[k + 1], left=col_x + 3.45, y=y)
        self.fit(loop, opts, row, p, check, yes, out, compare, *counts)
        self.apart(loop, row)
        self.apart(loop, opts)
        self.apart(opts, out)
        self.apart(compare[0], compare[1])
        self.apart(loop, VGroup(*counts, check, compare))

        self.T("s5_01", "Let's increase the challenge a little. We keep the same list, ten, then twenty, then thirty, "
                        "and add this code.",
               ("same", lambda: FadeIn(row, shift=UP * 0.2)),
               ("code", lambda: LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in loop.lines], lag_ratio=0.2,
                                            run_time=2.0)))
        self.Q("s5_02", "What will this program print? Don't rush. Follow the pointer.",
               ("print", lambda: FadeIn(opts, shift=UP * 0.15)),
               shown="What will this program print?", think=8.0)     # "Don't rush": time to trace the loop
        self.T("s5_03", "At the beginning, count is zero and p points to the first node, the one holding ten.",
               ("count", lambda: [loop.focus(L_COUNT), FadeIn(counts[0])]),
               ("points", lambda: [loop.focus(L_P), FadeIn(p, shift=DOWN * 0.2)]))
        self.T("s5_04", "Now read the condition carefully. It does not ask whether p is null. It asks whether p arrow "
                        "next is null, whether there is another node after the current one.",
               ("condition", lambda: loop.focus(L_WHILE)),
               ("arrow", lambda: [FadeIn(check), ring(n1.link)]),
               ("another", lambda: hl(a12)), other="think")
        self.Q("s5_05", "Is there a node after the first node?")
        self.S("s5_06", "Yes, the node holding twenty.",
               (None, lambda: [ring(n2), FadeIn(yes)]))
        self.T("s5_07", "So the condition is true. The count becomes one. And p moves to the second node.",
               ("count", lambda: [loop.focus(L_INC), FadeOut(counts[0]), FadeIn(counts[1])]),
               ("moves", lambda: [loop.focus(L_STEP), p.animate.shift(RIGHT * hop_x), FadeOut(yes)]))
        self.Q("s5_08", "Is there a node after the second node?",
               (None, lambda: [loop.focus(L_WHILE), ring(n2.link)]))
        self.S("s5_09", "Yes, the node holding thirty.",
               (None, lambda: [ring(n3), FadeIn(yes)]))
        self.T("s5_10", "The count becomes two. And p moves to the third node.",
               ("count", lambda: [loop.focus(L_INC), FadeOut(counts[1]), FadeIn(counts[2])]),
               ("moves", lambda: [loop.focus(L_STEP), p.animate.shift(RIGHT * hop_x), FadeOut(yes)]))
        self.Q("s5_11", "Is there a node after the third node?",
               (None, lambda: [loop.focus(L_WHILE), ring(n3.link)]))
        self.S("s5_12", "No. Its link is null.",
               (None, lambda: [hl(n3.mark), FadeIn(no)]))
        self.T("s5_13", "The condition, p arrow next not equal to null, is false, so the loop stops. The final output "
                        "is two.",
               ("false", lambda: loop.focus(L_CLOSE)),
               ("output", lambda: [loop.focus(L_PRINT), FadeIn(out, shift=UP * 0.15)]))
        self.T("s5_14", "The correct answer is option A: two.",
               ("answer", lambda: [opts.right("A"), loop.focus(None), a12.animate.set_color(FLASH),
                                   a23.animate.set_color(FLASH)]), look="happy")
        self.S("s5_15", "But the list has three nodes. Why isn't the answer three?",
               shown="But the list has 3 nodes. Why isn't the answer 3?", look="confused")
        self.T("s5_16", "Notice what the loop did. It stopped at the last node without counting it. In effect, it "
                        "counted the two links, not the three nodes.",
               ("stopped", lambda: hl(p)),
               ("links", lambda: FadeIn(nums, shift=DOWN * 0.1)),
               ("nodes", lambda: ring(row.nodes)), other="think")
        self.T("s5_17", "If the condition had been p not equal to null, the loop would have run three times and "
                        "printed three.",
               ("condition", lambda: [FadeOut(VGroup(counts[2], check, no, out)), FadeIn(compare[:2])]),
               ("three", lambda: FadeIn(compare[2:], shift=UP * 0.15)), other="happy")
        self.N("s5_18", "One small change in the condition, and the output changes. This is why tracing the pointer "
                        "step by step is so useful when solving list questions.",
               ("change", lambda: [hl(compare[0], 1.06), hl(compare[2], 1.06)]),
               ("tracing", lambda: hl(p)))

        self.finish("S05_loop")

    # =============================== 6. FOLLOWING A NULL LINK ==============

    def null_link(self):
        self.begin("S06_null", "What Happens If We Follow a NULL Link?", "What if we follow a NULL link?")

        row = chain(VALUES, x=-1.6, y=-0.1)
        n1, n2, n3 = row.nodes
        a12, a23 = row.arrows
        p = pointer("p", n3, FLASH)
        ghost = VGroup(DashedVMobject(Rectangle(width=2.5, height=0.85, stroke_color=MUTED, stroke_width=3), num_dashes=28),
                       text("No node here", SMALL, MUTED)).move_to(RIGHT * 4.85)
        ghost[1].move_to(ghost[0])
        step_out = ghost.get_x() - n3.data.get_x()
        code1 = place(code("p = p->next;", LABEL), left=-EDGE_X + 0.35, y=-1.35)
        code2 = place(phrase(code("p->data", LABEL), text("?", LABEL, FLASH, BOLD)), left=-EDGE_X + 0.35, y=-2.05)
        danger = column(text("Null pointer access: undefined behavior", LABEL, BAD, BOLD),
                        text("No guaranteed error message. Often a crash.", SMALL, MUTED), buff=0.3)
        place(danger, left=-2.5, top=-1.15)
        head = pointer("head", n1)
        rules = VGroup()
        for k, (who, how) in enumerate((("First node", "reached through head"),
                                        ("Every other node", "reached through the next of the node before it"),
                                        ("Last node", "its next is NULL, so stop there"))):
            rules.add(VGroup(place(text(who, LABEL, BLUE, BOLD), left=-6.1, y=-1.25 - 0.6 * k),
                             place(text(how, LABEL), left=-2.3, y=-1.25 - 0.6 * k)))
        habits = phrase(text("Check before you follow", SMALL, BROWN, BOLD),
                        text("Walk with a separate pointer", SMALL, BROWN, BOLD), buff=1.2).move_to(DOWN * 3.1)
        self.fit(row, ghost, p, code1, code2, danger, rules, habits, head)
        self.apart(code1, danger)
        self.apart(code2, danger)
        self.apart(rules, habits)
        for rule in rules:
            self.apart(*rule, gap=0.3)

        def lose_start():
            for m in (n1, n2, a12):
                m.save_state()
            return [m.animate.set_opacity(0.2) for m in (n1, n2, a12)]

        def move_head():
            for a, b in zip(row.nodes, row.nodes[1:]):
                self.play(head.animate.shift(RIGHT * (b.data.get_x() - a.data.get_x())), run_time=0.5)

        self.play(FadeIn(row, shift=UP * 0.2), run_time=0.7)
        self.T("s6_01", "Let's test one more idea. Suppose p points to the last node, and we execute this statement: "
                        "p equals p arrow next.",
               ("last", lambda: FadeIn(p, shift=DOWN * 0.2)),
               ("statement", lambda: FadeIn(code1, shift=RIGHT * 0.2)))
        self.Q("s6_02", "What does p hold now?")
        self.S("s6_03", "Null. The last node's link was null, so p no longer points to any node.",
               ("link", lambda: hl(n3.mark)),
               ("longer", lambda: [FadeIn(ghost), p.animate.shift(RIGHT * step_out)]),
               shown="NULL. So p no longer points to any node.")
        self.Q("s6_04", "Right. Now what would happen if we tried to read p arrow data? Is there a node there to read from?",
               ("read", lambda: FadeIn(code2, shift=RIGHT * 0.2)),
               shown="What if we now read p->data? Is there a node to read from?")
        self.S("s6_05", "No. There is no node at all.",
               (None, lambda: hl(ghost, 1.06)), look="oops")
        self.T("s6_06", "In C, accessing a member through a null pointer causes undefined behavior. The program is not "
                        "guaranteed to give a neat error message or a predictable result. Very often it simply crashes.",
               ("undefined", lambda: FadeIn(danger[0], shift=UP * 0.15)),
               ("crashes", lambda: [FadeIn(danger[1], shift=UP * 0.15), code2[0].animate.set_color(BAD)]), other="oops")
        self.Q("s6_07", "And there is a second mistake to watch for. What if we move head itself forward while walking "
                        "through the list?",
               (None, lambda: [FadeOut(VGroup(p, ghost, code1, code2, danger)), FadeIn(head, shift=DOWN * 0.2)]),
               ("forward", move_head),
               shown="What if we move head itself forward?")
        self.S("s6_08", "Then we lose the address of the first node, and with it, our only way back to the start.",
               ("lose", lose_start),
               shown="Then we lose the first node, and our only way back to the start.", look="oops")
        self.T("s6_09", "Exactly. So remember this relationship. The first node is reached through head. Every other node is "
                        "reached through the next of the node before it. And the last node's next is null, so stop "
                        "there.",
               (None, lambda: [Restore(n1), Restore(n2), Restore(a12),
                               head.animate.shift(LEFT * (n3.data.get_x() - n1.data.get_x()))]),
               ("first", lambda: [FadeIn(rules[0], shift=RIGHT * 0.2), hl(head)]),
               ("other", lambda: [FadeIn(rules[1], shift=RIGHT * 0.2), hl(a12), hl(a23)]),
               ("stop", lambda: [FadeIn(rules[2], shift=RIGHT * 0.2), hl(n3.mark)]))
        self.N("s6_10", "Check a pointer before following it, and walk the list with a separate pointer such as p. "
                        "Those two habits help you avoid the most common list mistakes.",
               ("Check", lambda: FadeIn(habits[0], shift=UP * 0.15)),
               ("separate", lambda: FadeIn(habits[1], shift=UP * 0.15)))

        self.finish("S06_null")

    # =============================== 7. WHY LISTS MATTER IN REAL LIFE ======

    def real_life(self):
        self.begin("S07_real_life", "Why Lists Matter in Real Life", "Insert without shifting")

        n1, n2, n3 = Node(10), Node(20), Node(30, "null")
        for n, left in ((n1, -5.6), (n2, -2.6), (n3, 2.0)):
            place(n, left=left, y=0.3)
        new = place(Node(25, None), x=(n2.get_right()[0] + n3.get_left()[0]) / 2, y=-1.3)
        new_tag = text("New node", SMALL, MUTED).next_to(new, DOWN, buff=0.14)
        a12, a23 = link_arrow(n1, n2), link_arrow(n2, n3)
        straight = a23.copy()
        a_new = Arrow(new.link.get_center(), n3.data.get_bottom() + DOWN * 0.06, buff=0, color=BROWN, stroke_width=4,
                      tip_length=0.22)
        a_down = Arrow(n2.link.get_center(), new.data.get_top() + UP * 0.06, buff=0, color=BROWN, stroke_width=4,
                       tip_length=0.22)
        st1 = place(text("1.  The new node's link points to 30", LABEL), left=-6.2, y=-2.65)
        st2 = place(text("2.  Then the link of 20 points to the new node", LABEL), left=-6.2, y=-3.2)
        tally = place(text("0 nodes move,  2 links change", SMALL, BLUE, BOLD), left=1.2, y=-2.65)
        warn = text("Wrong order: the address of 30 is lost", LABEL, BAD, BOLD).move_to(DOWN * 2.9)
        delete = text("Delete:  change one link so the chain skips the node", LABEL, BLUE, BOLD).move_to(DOWN * 2.9)
        self.fit(n1, n3, new, new_tag, st1, st2, tally, warn, delete)
        self.apart(st1, tally)
        self.apart(new_tag, st1)

        points = bullets(["Grows and shrinks while the program runs",
                          "Nodes are usually created with dynamic memory allocation",
                          "Insert and delete by adjusting links, not by shifting"], buff=0.42)
        place(points, x=0.0, y=-0.9)

        widths, top, row_h = (4.0, 3.9, 4.9), 1.0, 0.72
        table_rows = [("", "Array", "Linked list"), ("Extra memory", "None", "One link in every node"),
                      ("Access", "Direct, by index", "Step by step from head"),
                      ("Size", "Fixed", "Can grow and shrink"),
                      ("Insert in the middle", "Shift the elements", "Change two links")]
        table = VGroup()
        for r, cells in enumerate(table_rows):
            line, x = VGroup(), -sum(widths) / 2
            for c, s in enumerate(cells):
                if s:
                    style = (BODY, (INK, BROWN, BLUE)[c], BOLD) if r == 0 else (LABEL, MUTED if c == 0 else INK, NORMAL)
                    cell = place(text(s, *style), left=x, y=top - r * row_h)
                    if cell.width > widths[c] - 0.2:
                        raise ValueError(f"Table cell {s!r} does not fit a column of {widths[c]:.2f}.")
                    line.add(cell)
                x += widths[c]
            if r == 0:
                line.add(Line(LEFT * sum(widths) / 2, RIGHT * sum(widths) / 2, color=MUTED, stroke_width=2).move_to(
                    UP * (top - 0.4)))
            table.add(line)
        choose = text("Choose by what the program does most often", LABEL, BLUE, BOLD).move_to(DOWN * 2.85)
        self.fit(points, table, choose)
        self.apart(table, choose)

        self.T("s7_01", "Let's return to the new student from our opening scene. Our records hold the values ten, "
                        "twenty, and thirty, and we want to insert twenty-five between twenty and thirty.",
               ("records", lambda: [FadeIn(VGroup(n1, n2, n3), shift=UP * 0.2), GrowArrow(a12), GrowArrow(a23)]),
               ("insert", lambda: [FadeIn(new, shift=LEFT * 1.2), FadeIn(new_tag, shift=LEFT * 1.2)]))
        self.Q("s7_02", "In an array, we would shift every later element. In a linked list, how many nodes need to "
                        "move?",
               shown="In a linked list, how many nodes need to move?")
        self.S("s7_03", "None?", look="ask")
        self.T("s7_04", "None. We only change two links.",
               ("two", lambda: FadeIn(tally, shift=UP * 0.15)), look="happy")
        self.T("s7_05", "First, the new node's link is set to point to the node holding thirty.",
               ("First", lambda: FadeIn(st1, shift=RIGHT * 0.2)),
               ("point", lambda: [FadeIn(new.set_mark("dot")), GrowArrow(a_new)]))
        self.T("s7_06", "Then, the link of the node holding twenty is changed to point to the new node.",
               ("Then", lambda: FadeIn(st2, shift=RIGHT * 0.2)),
               ("changed", lambda: Transform(a23, a_down)))
        self.S("s7_07", "Does the order of those two steps matter?", look="ask")
        self.T("s7_08", "It does. If we change the link of twenty first, we overwrite the only place where the address "
                        "of thirty was stored, and the rest of the list is lost.",
               ("overwrite", lambda: [FadeOut(VGroup(tally, st1, st2)), FadeIn(warn), ring(n2.link)]),
               ("lost", lambda: Circumscribe(n3, color=BAD, buff=0.1, fade_out=True, stroke_width=5)), other="oops")
        self.T("s7_09", "Deleting a node works on the same idea. We change a link so that the chain skips over that "
                        "node.",
               ("Deleting", lambda: [FadeOut(warn), FadeIn(delete, shift=UP * 0.15)]),
               ("skips", lambda: [Transform(a23, straight), new.animate.set_opacity(0.25),
                                  a_new.animate.set_opacity(0.25), new_tag.animate.set_opacity(0.25)]))
        self.N("s7_10", "So a linked list can grow and shrink while the program runs, usually by creating each node "
                        "with dynamic memory allocation, and it can insert or delete by adjusting links instead of "
                        "shifting elements.",
               (None, self.wipe),
               ("grow", lambda: FadeIn(points[0], shift=RIGHT * 0.2)),
               ("dynamic", lambda: FadeIn(points[1], shift=RIGHT * 0.2)),
               ("adjusting", lambda: FadeIn(points[2], shift=RIGHT * 0.2)))
        self.S("s7_11", "Is a list always better than an array, then?", look="ask")
        self.T("s7_12", "No. Each node needs extra memory for its link. And we give up direct access. Reaching a node "
                        "means walking from the head.",
               (None, self.wipe),
               (None, lambda: FadeIn(table[0])),
               ("extra", lambda: FadeIn(table[1], shift=RIGHT * 0.2)),
               ("direct", lambda: FadeIn(table[2], shift=RIGHT * 0.2)))
        self.T("s7_13", "An array gives us fast direct access with a fixed size. A linked list gives us flexible size "
                        "and easy insertion, with step by step access.",
               ("fixed", lambda: FadeIn(table[3], shift=RIGHT * 0.2)),
               ("insertion", lambda: FadeIn(table[4], shift=RIGHT * 0.2)),
               ("step", lambda: hl(table[2][2], 1.06)))
        self.N("s7_14", "Choosing between them depends on what the program needs to do most often.",
               ("depends", lambda: FadeIn(choose, shift=UP * 0.15)))

        self.finish("S07_real_life")

    # ======================================== 8. THE C-CAT TAKEAWAY ========

    def takeaway(self):
        self.begin("S08_takeaway", "The C-CAT Takeaway", "The C-CAT method")

        solved = []
        for label, line, answer, left in (("Question 1", "head->next->data", "B.  20", -6.0),
                                          ("Question 2", "while (p->next != NULL)", "A.  2", 0.6)):
            block = column(text(label, SMALL, MUTED, BOLD), code(line, LABEL),
                           phrase(text("Answer:", LABEL), text(answer, LABEL, GOOD, BOLD)), buff=0.3)
            solved.append(place(block, left=left, top=0.6))
        trace = text("Do not guess from the first value you see. Trace it.", LABEL, BROWN, BOLD).move_to(DOWN * 2.4)
        self.fit(*solved, trace)
        self.apart(*solved)

        row = chain(VALUES, y=-0.1, last=None)
        n1, n2, n3 = row.nodes
        head, p = pointer("head", n1), pointer("p", n2, FLASH)
        c_p, c_next = code("p", LABEL, FLASH), code("p->next", LABEL, FLASH)
        steps = column(text("1.  Draw the nodes as boxes: a data part and a link part", LABEL),
                       text("2.  Draw an arrow for every link; the last link is NULL", LABEL),
                       text("3.  Place each pointer on the node it points to", LABEL),
                       text("4.  In a loop, move the pointer one node at a time", LABEL),
                       phrase(text("5.  Check the loop condition:  does it test", LABEL), c_p, text("or", LABEL), c_next,
                              text("?", LABEL)), buff=0.17)
        place(steps, left=-6.2, top=-0.8)
        self.fit(row, head, p, steps)

        ideas = bullets(["A list is a linear sequence that can grow and shrink",
                         "Each node stores a data value and a link to the next node",
                         "Head gives the first node; the last link is NULL",
                         "No consecutive memory, so no index and no direct access",
                         "Insertion and deletion change links instead of shifting",
                         phrase(code("p != NULL", LABEL, BLUE), text("and", LABEL), code("p->next != NULL", LABEL, BLUE),
                                text("stop at different places", LABEL))], buff=0.27)
        key = text("Key ideas", BODY, BLUE, BOLD)
        board = column(key, ideas, buff=0.35)
        place(board, x=0.0, top=BOARD_TOP - 0.05)
        self.fit(board)

        self.N("s8_01", "Before we finish, let's connect everything back to our exam preparation. When you see a list "
                        "question in C-CAT practice, don't guess from the first value you notice in the code.",
               ("connect", lambda: [FadeIn(b, shift=UP * 0.2) for b in solved]),
               ("guess", lambda: FadeIn(trace, shift=UP * 0.15)))
        self.T("s8_02", "First, draw the nodes as boxes, each with a data part and a link part. Next, draw an arrow "
                        "for every link, and mark the last link as null. Then place each pointer, head, p, or any "
                        "other, on the node it points to.",
               (None, self.wipe),
               ("draw", lambda: [FadeIn(steps[0], shift=RIGHT * 0.2), FadeIn(row.nodes, shift=UP * 0.2)]),
               ("arrow", lambda: [FadeIn(steps[1], shift=RIGHT * 0.2)] + [GrowArrow(a) for a in row.arrows]),
               ("null", lambda: FadeIn(n3.set_mark("null"))),
               ("pointer", lambda: [FadeIn(steps[2], shift=RIGHT * 0.2), FadeIn(head, shift=DOWN * 0.2),
                                    FadeIn(p, shift=DOWN * 0.2)]))
        self.T("s8_03", "If the question contains a loop, move the pointer one node at a time and record what changes "
                        "at each step. Finally, check the loop condition carefully. Does it test the pointer itself, "
                        "or the next of the pointer?",
               ("loop", lambda: [FadeIn(steps[3], shift=RIGHT * 0.2),
                                 p.animate.shift(RIGHT * (n3.data.get_x() - n2.data.get_x()))]),
               ("Finally", lambda: FadeIn(steps[4], shift=RIGHT * 0.2)),
               ("itself", lambda: hl(c_p, 1.4)),
               ("next", lambda: hl(c_next, 1.2)))
        self.N("s8_04", "The key ideas are these. A list is a linear sequence of elements that can grow and shrink. In "
                        "a linked list, each node stores a data value and a link to the next node. The head pointer "
                        "gives access to the first node, and the last node's link is null.",
               (None, self.wipe),
               ("key", lambda: FadeIn(key)),
               ("sequence", lambda: FadeIn(ideas[0], shift=RIGHT * 0.2)),
               ("stores", lambda: FadeIn(ideas[1], shift=RIGHT * 0.2)),
               ("head", lambda: FadeIn(ideas[2], shift=RIGHT * 0.2)))
        self.N("s8_05", "Nodes need not occupy consecutive memory locations, so there is no index and no direct "
                        "access. Insertion and deletion change links instead of shifting elements. And the conditions "
                        "p not equal to null, and p arrow next not equal to null, stop a loop at different places.",
               ("consecutive", lambda: FadeIn(ideas[3], shift=RIGHT * 0.2)),
               ("Insertion", lambda: FadeIn(ideas[4], shift=RIGHT * 0.2)),
               ("conditions", lambda: FadeIn(ideas[5], shift=RIGHT * 0.2)))
        self.T("s8_06", "Now those two questions should feel much easier, not because you memorized the options, but "
                        "because you understand the logic behind them.",
               ("logic", lambda: hl(key)), other="happy")

        self.finish("S08_takeaway")

    # ================================================== 9. SUMMARY =========

    def summary(self):
        self.begin("S09_summary", "Summary", "Summary")

        flow = VGroup(text("LIST", BODY, BLUE, BOLD))
        for s in ("Head pointer", "Nodes: data + link", "Each link leads to the next node", "Last link is NULL",
                  "Insert and delete by changing links"):
            flow.add(Arrow(UP * 0.22, DOWN * 0.22, buff=0, color=BROWN, stroke_width=4, tip_length=0.18), text(s, LABEL))
        flow.arrange(DOWN, buff=0.1).move_to(LEFT * 3.2)
        place(flow, top=BOARD_HIGH - 0.1)
        asked = column(text("The opening question", SMALL, MUTED, BOLD),
                       fitted_text("How do we add a record in the middle without shifting thousands of others?", 5.6,
                                   LABEL, max_lines=3), buff=0.25)
        answer = VGroup(tick(), fitted_text("Use a linked list: change two links, move nothing", 5.0, LABEL, GOOD, BOLD,
                                            max_lines=2)).arrange(RIGHT, buff=0.3)
        right = column(asked, answer, buff=0.6)
        place(right, left=0.9, y=-0.6)
        self.fit(flow, right, top=BOARD_HIGH)
        self.apart(flow, right)

        self.play(LaggedStart(*[FadeIn(m, shift=DOWN * 0.15) for m in flow], lag_ratio=0.35), run_time=4.0)
        self.N("s9_01", "That is the foundation of lists.",
               ("foundation", lambda: hl(flow[0])))
        self.T("s9_02", "And remember the question that started our class: how do we add a new record in the middle "
                        "without shifting thousands of others?",
               ("question", lambda: FadeIn(asked, shift=UP * 0.15)), look="ask")
        self.T("s9_03", "Now we have one answer.",
               ("answer", lambda: FadeIn(answer, shift=UP * 0.15)), look="happy", other="happy")

        self.finish("S09_summary")

    # ============================== 10. NEXT SESSION: TYPES OF LIST ========

    def next_session(self):
        self.begin("S10_next", "Next Session: Types of List", "What comes next?")

        row = chain(VALUES, y=-0.1)
        n1, n2, n3 = row.nodes
        head = pointer("head", n1)
        walker = Dot(radius=0.12, color=FLASH).next_to(n1.data, DOWN, buff=0.2)
        one_way = text("One direction only: from head to the end", LABEL, MUTED).move_to(DOWN * 2.7)
        back = CurvedArrow(n2.data.get_bottom() + DOWN * 0.1, n1.link.get_bottom() + DOWN * 0.1, angle=-PI / 2,
                           color=BLUE, stroke_width=4)
        around = CurvedArrow(n3.link.get_bottom() + DOWN * 0.1, n1.data.get_bottom() + DOWN * 0.1, angle=-PI / 2,
                             color=BROWN, stroke_width=4)
        nxt = VGroup(text("NEXT", LABEL, MUTED, BOLD), text("Types of List", TITLE, BLUE, BOLD),
                     Line(LEFT * 1.6, RIGHT * 1.6, color=BROWN, stroke_width=4),
                     text("Different ways of linking nodes together", LABEL)).arrange(DOWN, buff=0.35).move_to(DOWN * 0.9)
        self.fit(row, head, one_way, around, nxt)
        self.apart(around, one_way)

        self.play(FadeIn(row, shift=UP * 0.2), FadeIn(head), run_time=0.8)
        self.N("s10_01", "But the list we built today can only be walked in one direction, from the head toward the "
                         "end.",
               ("walked", lambda: FadeIn(walker)),
               ("direction", lambda: self.hop(walker, row.nodes)),
               (None, lambda: [FadeOut(walker), FadeIn(one_way, shift=UP * 0.15)]))
        self.Q("s10_02", "What if we are standing at a node and want to go back to the one before it?",
               ("back", lambda: Create(back)),
               shown="What if we want to go back to the node before?")
        self.Q("s10_03", "And what if the last node, instead of ending at null, pointed somewhere useful?",
               ("pointed", lambda: [Create(around), hl(n3.mark)]),
               shown="What if the last node pointed somewhere useful?")
        self.S("s10_04", "Could changing the way nodes are linked change what a list can do?", look="think")
        self.N("s10_05", "That is where we are heading next. In our next session, we will explore the types of list, "
                         "different ways of linking nodes together, and see what each one makes easier.",
               ("heading", self.wipe),
               ("types", lambda: [FadeIn(nxt[0]), FadeIn(nxt[1], scale=1.1), Create(nxt[2])]),
               ("linking", lambda: FadeIn(nxt[3], shift=UP * 0.15)))

        # the end: the characters and the heading leave with everything else
        self.cast = self.title_bar = None
        if self.mobjects:
            self.play(FadeOut(Group(*self.mobjects)), run_time=1.0)
        self.scene_end("S10_next")
