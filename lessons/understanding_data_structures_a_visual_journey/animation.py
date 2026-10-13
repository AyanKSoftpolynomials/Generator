"""
animation.py for the LMS video generator.

Video  : Understanding Data Structures: A Visual Journey
Source : the "Manim-ready script with scene-by-scene breakdown" (10 scenes, about 10 minutes).

Roles: the script labels EVERY spoken line "NARRATOR", so this video has one voice and no
classroom characters. The pictures are the ones the script asks for, scene by scene.
  NARRATOR   self.N   voice "vijay"
  Spoken text uses words ("O of one"); the board shows the notation (O(1)).

Look (3Blue1Brown style):
  - near-black background, white text, ONE blue and ONE brown accent;
    yellow only for a passing highlight, green / red only for right / wrong
  - text in Latin Modern Roman (taken from the MiKTeX folder on this machine; Cambria if it is missing)
  - code in Consolas
  - sizes: title 54, heading 38, body 32, label 28, small 24; nothing below 22

Screen zones:
  top band   the scene heading
  board      everything else (BOARD_TOP down to FLOOR)

Section map:
  S01 Why do we need data structures?   S02 Arrays   S03 Linked lists   S04 Stacks   S05 Queues
  S06 Hash tables   S07 Trees   S08 Graphs   S09 Choosing the right tool   S10 Closing thoughts

Changes from the script, all small:
  - the coloured plates of the stack scene are numbered plates in the two accent colours
  - the long listings (linked list, tree, graph) are shown in columns or pages so that the text stays readable
  - two long comments inside the listings are shortened to fit the board
"""

import math
import os
import random
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
BROWN = "#CD853F"          # accent 2: links, pointers
FLASH = "#FFFF00"          # a passing highlight only
GOOD = "#83C167"           # right / strength
BAD = "#FC6255"            # wrong / weakness

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
MIN_FONT = 22              # readable floor
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
HEAD_Y = 3.02                                 # centre of the scene heading
BOARD_TOP = 2.4                               # top of the board

NARRATOR_VOICE = "vijay"
TURN_PAUSE = 0.6               # silence after each narration


# ======================================================= text helpers ====

def text(s, size=BODY, color=INK, weight=NORMAL, slant=NORMAL, font=FONT):
    return Text(s, font=font, font_size=size, color=color, weight=weight, slant=slant, disable_ligatures=True)


def code(s, size=CODE, color=INK, weight=NORMAL):
    """Program text, names and values."""
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


def fitted_text(s, max_width, size=BODY, color=INK, weight=NORMAL, max_lines=2):
    """Text no wider than ``max_width``: as written, else wrapped, else a little smaller."""
    for lines in range(1, max_lines + 1):
        mob = text(s if lines == 1 else wrap_lines(s, lines), size, color, weight)
        if mob.width <= max_width:
            return mob
    return mob.scale(max_width / mob.width)


def phrase(*parts, buff=0.22):
    """Text and code pieces on one line."""
    return VGroup(*parts).arrange(RIGHT, buff=buff)


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


def P(x, y):
    return np.array([x, y, 0.0])


def hl(mob, scale=1.12):
    """Highlight a text or an arrow for a moment."""
    return Indicate(mob, color=FLASH, scale_factor=scale)


def ring(mob):
    """Highlight a box for a moment (a frame that draws itself and fades)."""
    return Circumscribe(mob, color=FLASH, buff=0.1, fade_out=True, stroke_width=5)


def tick(size=0.3, color=GOOD):
    t = VMobject(stroke_color=color, stroke_width=6)
    t.set_points_as_corners([P(-0.5, 0.0), P(-0.12, -0.4), P(0.5, 0.45)])
    return t.scale(size)


def cross_mark(size=0.3, color=BAD):
    return VGroup(Line(UL, DR, stroke_color=color, stroke_width=6),
                  Line(UR, DL, stroke_color=color, stroke_width=6)).scale(size * 0.45)


def verdict(good, bad, size=LABEL):
    """The last word on a structure: its strength (tick) and its weakness (cross)."""
    rows = VGroup(VGroup(tick(), text(good, size)).arrange(RIGHT, buff=0.25),
                  VGroup(cross_mark(), text(bad, size)).arrange(RIGHT, buff=0.25))
    rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
    rows.good, rows.bad = rows[0], rows[1]
    return rows


# ==================================================== diagram pieces ====

class Listing(VGroup):
    """A program listing: one Text per line, indentation kept, blank lines as part gaps, comments in grey."""

    def __init__(self, src, size=CODE, gap=0.4):
        super().__init__()
        unit = code("M" * 10, size).width / 10
        step, y = size * 0.0175, 0.0
        self.lit, self.tones = None, []
        for raw in src.strip("\n").split("\n"):
            if not raw.strip():
                y -= step * gap
                continue
            tone = MUTED if raw.strip().startswith("#") else INK
            line = code(raw.strip() + "|", size, tone)         # the bar gives every line the same height
            line.move_to(UP * y).align_to(RIGHT * (len(raw) - len(raw.lstrip())) * unit, LEFT)
            line.remove(line[-1])
            self.add(line)
            self.tones.append(tone)
            y -= step
        self.lines = list(self.submobjects)

    def focus(self, i, color=FLASH):
        """Animations that light line ``i`` (None: no line) and put the last lit line back."""
        anims = []
        if self.lit is not None and self.lit != i:
            anims.append(self.lines[self.lit].animate.set_color(self.tones[self.lit]))
        if i is not None and self.lit != i:
            anims.append(self.lines[i].animate.set_color(color))
        self.lit = i
        return anims

    def typed(self, run_time=1.6):
        return LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in self.lines], lag_ratio=0.15, run_time=run_time)


def cell(side=1.0, color=BLUE, width=None):
    return Rectangle(width=width or side, height=side, stroke_color=color, stroke_width=3, fill_color=FILL,
                     fill_opacity=1)


class Row(VGroup):
    """An array drawn as a row of boxes: the values inside, the indices underneath.

    ``extra`` adds empty boxes at the end; ``index=False`` leaves the indices out."""

    def __init__(self, values, side=1.0, size=BODY, extra=0, index=True):
        super().__init__()
        self.boxes = VGroup(*[cell(side) for _ in range(len(values) + extra)]).arrange(RIGHT, buff=0)
        self.vals = VGroup(*[code(str(v), size).move_to(b) for v, b in zip(values, self.boxes)])
        self.idx = VGroup(*[code(str(k), SMALL, MUTED).next_to(b, DOWN, buff=0.18) for k, b in enumerate(self.boxes)])
        self.add(self.boxes, self.vals)
        if index:
            self.add(self.idx)

    def at(self, x, y):
        """Put the centre of the boxes at (x, y)."""
        return self.shift(RIGHT * x + UP * y - self.boxes.get_center())


class Node(VGroup):
    """A list node: a data part (blue) and a link part (brown). The last node's link is struck through."""

    def __init__(self, value, last=False, dw=0.9, lw=0.7, h=0.85, size=BODY):
        super().__init__()
        self.data = cell(h, BLUE, dw)
        self.link = cell(h, BROWN, lw).next_to(self.data, RIGHT, buff=0)
        self.val = code(str(value), size).move_to(self.data)
        if last:
            self.mark = Line(self.link.get_corner(DL), self.link.get_corner(UR), stroke_color=BROWN, stroke_width=3)
        else:
            self.mark = Dot(self.link.get_center(), radius=0.07, color=BROWN)
        self.add(self.data, self.link, self.val, self.mark)


def link_arrow(a, b):
    """The arrow from the link part of ``a`` to node ``b``."""
    return Arrow(a.link.get_center(), b.data.get_left() + LEFT * 0.06, buff=0, color=BROWN, stroke_width=4,
                 tip_length=0.2)


def chain(values, x=0.0, y=0.0, gap=0.8, **node_args):
    """Nodes in a row with their link arrows. Returns VGroup(nodes, arrows) with ``.nodes`` and ``.arrows``."""
    nodes = VGroup(*[Node(v, k == len(values) - 1, **node_args) for k, v in enumerate(values)])
    nodes.arrange(RIGHT, buff=gap).move_to(RIGHT * x + UP * y)
    arrows = VGroup(*[link_arrow(a, b) for a, b in zip(nodes, nodes[1:])])
    group = VGroup(nodes, arrows)
    group.nodes, group.arrows = nodes, arrows
    return group


def pointer(name, node, color=BLUE, side=UP):
    """A named pointer resting on the data part of ``node``: VGroup(label, arrow)."""
    at = node.data.get_edge_center(side)
    arrow = Arrow(at + side * 0.56, at + side * 0.08, buff=0, color=color, stroke_width=4, tip_length=0.2)
    label = code(name, LABEL, color).next_to(arrow, side, buff=0.08)
    return VGroup(label, arrow)


def plate(label, w=2.4, h=0.55, color=BLUE):
    """One item of a stack."""
    return VGroup(cell(h, color, w), code(str(label), SMALL))


def tub(w, h):
    """The open container of a stack."""
    return VMobject(stroke_color=MUTED, stroke_width=4).set_points_as_corners(
        [P(-w / 2, h / 2), P(-w / 2, -h / 2), P(w / 2, -h / 2), P(w / 2, h / 2)])


def person(color=BLUE, tag=None):
    """Someone waiting in a queue."""
    head = Circle(radius=0.2, stroke_width=0, fill_color=color, fill_opacity=1)
    body = Arc(radius=0.34, start_angle=0, angle=PI, stroke_width=0, fill_color=color, fill_opacity=1)
    body.next_to(head, DOWN, buff=0.04)
    who = VGroup(head, body)
    if tag:
        who.add(text(tag, SMALL, color, BOLD).next_to(head, UP, buff=0.12))
    return who


def disc(label="", r=0.32, size=SMALL, square=False):
    """A tree node or a graph vertex."""
    look = dict(stroke_color=BLUE, stroke_width=3, fill_color=FILL, fill_opacity=1)
    rim = Square(2 * r, **look) if square else Circle(radius=r, **look)
    node = VGroup(rim)
    node.rim, node.label = rim, None
    if str(label):
        node.label = code(str(label), size).move_to(rim)
        node.add(node.label)
    return node


def btree(labels, x, y, dx, dy, r=0.32, size=SMALL):
    """A full binary tree, level by level. ``.nodes`` is the list, ``.edges[k]`` joins node k to its parent."""
    cols = (0, -2, 2, -3, -1, 1, 3)
    tree = VGroup()
    tree.nodes = [disc(s, r, size).move_to(P(x + dx * cols[k], y - dy * (k > 0) - dy * (k > 2)))
                  for k, s in enumerate(labels)]
    tree.edges = {k: Line(tree.nodes[(k - 1) // 2].get_center(), tree.nodes[k].get_center(), buff=r,
                          stroke_color=MUTED, stroke_width=3) for k in range(1, len(labels))}
    tree.add(*tree.edges.values(), *tree.nodes)
    return tree


def graph(points, pairs, r=0.32, size=SMALL, directed=False, weights=None, square=False, labels=None, x=0.0, y=0.0):
    """A graph. ``.nodes[name]``, ``.edges[(a, b)]`` and, with ``weights``, ``.tags[(a, b)]``."""
    g = VGroup()
    g.nodes = {name: disc(name if labels is None else labels.get(name, ""), r, size, square).move_to(P(x + px, y + py))
               for name, (px, py) in points.items()}
    g.edges, g.tags = {}, {}
    for k, (a, b) in enumerate(pairs):
        p, q = g.nodes[a].get_center(), g.nodes[b].get_center()
        if directed:
            g.edges[(a, b)] = Arrow(p, q, buff=r, color=MUTED, stroke_width=3, tip_length=0.2)
        else:
            g.edges[(a, b)] = Line(p, q, buff=r, stroke_color=MUTED, stroke_width=3)
        if weights:
            along = (q - p) / np.linalg.norm(q - p)
            g.tags[(a, b)] = code(str(weights[k]), MIN_FONT, BROWN).move_to((p + q) / 2 + 0.27 * P(-along[1], along[0]))
    g.add(*g.edges.values(), *g.nodes.values(), *g.tags.values())
    return g


def glyph(kind):
    """A small line drawing (about 0.9 units) for a use case or a structure."""
    blue = dict(stroke_color=BLUE, stroke_width=3)
    warm = dict(stroke_color=BROWN, stroke_width=3)
    if kind == "bars":
        g = VGroup(*[Rectangle(width=0.2, height=h, fill_color=BLUE, fill_opacity=0.6, **blue) for h in (0.4, 0.8, 0.6)])
        return g.arrange(RIGHT, buff=0.1, aligned_edge=DOWN)
    if kind == "grid":
        g = VGroup(*[Square(0.28, **blue) for _ in range(9)]).arrange_in_grid(rows=3, cols=3, buff=0)
        for k in (0, 4, 5, 7):
            g[k].set_fill(BLUE, 0.6)
        return g
    if kind == "table":
        return VGroup(Rectangle(width=0.95, height=0.8, **blue), Line(P(-0.475, 0.16), P(0.475, 0.16), **blue),
                      Line(P(-0.475, -0.12), P(0.475, -0.12), **blue), Line(P(-0.15, 0.4), P(-0.15, -0.4), **blue))
    if kind == "layers":
        g = VGroup(*[Rectangle(width=0.9, height=0.2, **(blue if k % 2 == 0 else warm)) for k in range(3)])
        return g.arrange(DOWN, buff=0.1)
    if kind == "lines":
        g = VGroup(*[VGroup(Dot(radius=0.05, color=BROWN), Line(ORIGIN, RIGHT * 0.65, **blue)).arrange(RIGHT, buff=0.12)
                     for _ in range(3)])
        return g.arrange(DOWN, buff=0.22)
    if kind == "back":
        return VGroup(Arrow(RIGHT * 0.5, LEFT * 0.5, buff=0, color=BLUE, stroke_width=5, tip_length=0.25))
    if kind == "undo":
        arc = Arc(radius=0.36, start_angle=-PI / 3, angle=1.5 * PI, **warm)
        arc.add_tip(tip_length=0.2, tip_width=0.2)
        return VGroup(arc)
    if kind == "expr":
        return VGroup(code("3+4×2", MIN_FONT, BLUE))
    if kind == "maze":
        return VGroup(Square(0.9, **blue), Line(P(-0.45, 0.15), P(0.1, 0.15), **blue),
                      Line(P(0.1, 0.15), P(0.1, -0.15), **blue), Line(P(-0.15, -0.45), P(-0.15, -0.15), **blue),
                      Line(P(0.45, -0.15), P(0.25, -0.15), **blue))
    if kind == "tree":
        pts = [P(0, 0.35), P(-0.35, -0.3), P(0.35, -0.3)]
        return VGroup(Line(pts[0], pts[1], **blue), Line(pts[0], pts[2], **blue),
                      *[Dot(p, radius=0.11, color=c) for p, c in zip(pts, (BROWN, BLUE, BLUE))])
    if kind == "calendar":
        return VGroup(Rectangle(width=0.9, height=0.8, **blue), Line(P(-0.45, 0.18), P(0.45, 0.18), **blue),
                      *[Dot(P(px, py), radius=0.05, color=BROWN) for px in (-0.22, 0.0, 0.22) for py in (-0.02, -0.22)])
    if kind == "server":
        g = VGroup(*[VGroup(Rectangle(width=0.9, height=0.3, **blue)) for _ in range(2)]).arrange(DOWN, buff=0.1)
        for unit in g:
            unit.add(Dot(unit.get_right() + LEFT * 0.15, radius=0.05, color=BROWN))
        return g
    if kind == "queue":
        boxes = VGroup(*[Square(0.26, **blue) for _ in range(3)]).arrange(RIGHT, buff=0.06)
        tip = Arrow(ORIGIN, LEFT * 0.3, buff=0, color=BROWN, stroke_width=3, tip_length=0.12)
        return VGroup(tip, boxes, tip.copy()).arrange(RIGHT, buff=0.08)
    if kind == "db":
        return VGroup(*[Ellipse(width=0.85, height=0.3, **blue) for _ in range(3)]).arrange(DOWN, buff=-0.06)
    if kind == "bolt":
        return VGroup(Polygon(P(0.12, 0.45), P(-0.28, -0.05), P(0.0, -0.05), P(-0.12, -0.45), P(0.28, 0.08),
                              P(0.0, 0.08), fill_color=BROWN, fill_opacity=0.7, **warm))
    if kind == "set":
        return VGroup(Circle(radius=0.3, **blue).shift(LEFT * 0.17), Circle(radius=0.3, **warm).shift(RIGHT * 0.17))
    if kind == "folder":
        return VGroup(Polygon(P(-0.45, -0.32), P(-0.45, 0.32), P(-0.12, 0.32), P(-0.02, 0.2), P(0.45, 0.2),
                              P(0.45, -0.32), **warm))
    if kind == "net":
        pts = [P(-0.4, 0.25), P(0.35, 0.38), P(-0.25, -0.38), P(0.42, -0.2)]
        return VGroup(*[Line(pts[a], pts[b], **blue) for a, b in ((0, 1), (0, 2), (1, 3), (2, 3), (0, 3))],
                      *[Dot(p, radius=0.09, color=BROWN) for p in pts])
    if kind == "route":
        pts = [P(-0.45, -0.3), P(-0.12, 0.25), P(0.15, -0.1), P(0.45, 0.32)]
        return VGroup(VMobject(**blue).set_points_as_corners(pts), Dot(pts[0], radius=0.09, color=BROWN),
                      Dot(pts[-1], radius=0.09, color=BROWN))
    if kind == "star":
        return VGroup(Star(n=5, outer_radius=0.45, **warm))
    if kind == "array":
        return VGroup(*[Square(0.27, **blue) for _ in range(4)]).arrange(RIGHT, buff=0)
    if kind == "linked":
        link = Arrow(ORIGIN, RIGHT * 0.32, buff=0, color=BROWN, stroke_width=3, tip_length=0.12)
        return VGroup(Square(0.28, **blue), link, Square(0.28, **blue)).arrange(RIGHT, buff=0.05)
    if kind == "stack":
        can = VMobject(**warm).set_points_as_corners([P(-0.4, 0.4), P(-0.4, -0.4), P(0.4, -0.4), P(0.4, 0.4)])
        plates = VGroup(*[Rectangle(width=0.6, height=0.16, **blue) for _ in range(3)]).arrange(DOWN, buff=0.07)
        return VGroup(can, plates.move_to(P(0, -0.07)))
    if kind == "hash":
        link = Arrow(ORIGIN, RIGHT * 0.3, buff=0, color=BROWN, stroke_width=3, tip_length=0.12)
        cells = VGroup(*[Rectangle(width=0.36, height=0.22, **blue) for _ in range(3)]).arrange(DOWN, buff=0)
        return VGroup(Square(0.26, **warm), link, cells).arrange(RIGHT, buff=0.06)
    raise ValueError(f"No drawing called {kind!r}.")


TOOLS = ["Array", "Linked list", "Stack", "Queue", "Hash table", "Tree", "Graph"]
TOOL_GLYPHS = ["array", "linked", "stack", "queue", "hash", "tree", "net"]
TOOL_SPOTS = [(-4.2 + 2.8 * k, 0.325) for k in range(4)] + [(-2.8 + 2.8 * k, -1.425) for k in range(3)]


def toolbox(filled=False):
    """The toolbox of the seven structures: ``.body``, ``.slots``, ``.items`` (one per slot), ``.lid``.

    Empty: each slot holds only its name, in grey. Filled: a small drawing with the name under it."""
    body = Rectangle(width=11.5, height=3.85, stroke_color=BROWN, stroke_width=4).move_to(DOWN * 0.55)
    bar = Rectangle(width=11.9, height=0.32, stroke_color=BROWN, stroke_width=4, fill_color=FILL, fill_opacity=1)
    bar.next_to(body, UP, buff=0)
    handle = ArcBetweenPoints(bar.get_top() + LEFT * 0.9, bar.get_top() + RIGHT * 0.9, angle=-PI * 0.6, color=BROWN,
                              stroke_width=4)
    slots = VGroup(*[Rectangle(width=2.5, height=1.5, stroke_color=MUTED, stroke_width=2).move_to(P(x, y))
                     for x, y in TOOL_SPOTS])
    items = VGroup()
    for name, kind, slot in zip(TOOLS, TOOL_GLYPHS, slots):
        if filled:
            items.add(VGroup(glyph(kind).move_to(slot.get_center() + UP * 0.22),
                             text(name, SMALL).move_to(slot.get_center() + DOWN * 0.48)))
        else:
            items.add(text(name, LABEL, MUTED).move_to(slot))
    box = VGroup(body, slots, items, bar, handle)
    box.body, box.slots, box.items, box.lid = body, slots, items, VGroup(bar, handle)
    return box


# ============================================================= lesson ====

CHAOS = ["7432", "Asha", "$19.99", "09:41", "Ravi", "3.14", "18.52N", "msg#88",
         "Meera", "$4.50", "42", "23:59", "Kiran", "0xFF", "73.85E", "id:501",
         "Neha", "$120", "12:30", "8,204", "Arjun", "hello", "99.9", "user77",
         "$0.99", "06:15", "Priya", "1,000", "lat:19", "ok", "Zoya", "$58",
         "17:45", "65536", "ping", "Dev", "2.718", "$7.25", "404", "Anil"]
CHAOS_SPOTS = [(-5.75 + 1.64 * c, 1.95 - 1.2 * r) for r in range(5) for c in range(8)]

ARRAY = [10, 20, 30, 40, 50, 60, 70, 80]
SCORES = [85, 92, 78, 95, 88]
LIST = [10, 20, 30, 40, 50]
ADDRESSES = ["0x2A40", "0x91F0", "0x1B08", "0x77C4", "0x4D20"]      # scattered: not in order
HASHES = {"Alice": 3, "Bob": 1, "Charlie": 5, "Diana": 3}           # Diana collides with Alice
BST = [50, 30, 70, 20, 40, 60, 80]                                  # insertion order = level order
ADJ = {"A": "BC", "B": "AD", "C": "AD", "D": "BCE", "E": "D"}       # the graph of the listing

ARRAY_CODE = """
# Creating an array
scores = [85, 92, 78, 95, 88]

# Access by index — O(1)
print(scores[2])  # 78

# Insert in middle — O(n)
scores.insert(2, 100)  # shifts elements right

# Delete from middle — O(n)
scores.pop(2)  # shifts elements left
"""

LIST_CODE_A = """
# Node class
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

# A linked list: 10 -> 20 -> 30
head = Node(10)
head.next = Node(20)
head.next.next = Node(30)
"""

LIST_CODE_B = """
# Insert at head — O(1)
new_node = Node(5)
new_node.next = head
head = new_node

# Traverse — O(n)
current = head
while current:
    print(current.data)
    current = current.next
"""

STACK_CODE = """
# Using a Python list as a stack
stack = []

# Push — O(1)
stack.append(10)
stack.append(20)
stack.append(30)

# Pop — O(1)
top = stack.pop()  # 30

# Peek — O(1)
top = stack[-1]  # 20

# Check if empty
is_empty = len(stack) == 0
"""

QUEUE_CODE = """
from collections import deque

# Creating a queue
queue = deque()

# Enqueue — O(1)
queue.append(10)
queue.append(20)
queue.append(30)

# Dequeue — O(1)
first = queue.popleft()  # 10

# Peek at front — O(1)
front = queue[0]  # 20

# Check if empty
is_empty = len(queue) == 0
"""

HASH_CODE = '''
# A hash table (a dict in Python)
user_ages = {}

# Insert — O(1) average
user_ages["Alice"] = 30
user_ages["Bob"] = 25
user_ages["Charlie"] = 35

# Lookup — O(1) average
age = user_ages["Alice"]  # 30

# Delete — O(1) average
del user_ages["Bob"]

# Check existence — O(1) average
if "Charlie" in user_ages:
    print("Found!")
'''

TREE_CODE_1 = """
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if not self.root:
            self.root = TreeNode(value)
        else:
            self._insert(self.root, value)
"""

TREE_CODE_2 = """
# class BST, continued
def _insert(self, node, value):
    if value < node.value:
        if node.left:
            self._insert(node.left, value)
        else:
            node.left = TreeNode(value)
    else:
        if node.right:
            self._insert(node.right, value)
        else:
            node.right = TreeNode(value)
"""

TREE_CODE_3 = """
# class BST, continued
def search(self, value):
    return self._search(self.root, value)

def _search(self, node, value):
    if not node or node.value == value:
        return node
    if value < node.value:
        return self._search(node.left, value)
    return self._search(node.right, value)
"""

GRAPH_CODE_1 = """
# Graph as an adjacency list
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D'],
    'C': ['A', 'D'],
    'D': ['B', 'C', 'E'],
    'E': ['D']
}
"""

GRAPH_CODE_2 = """
# Add an edge
def add_edge(graph, u, v):
    if u not in graph:
        graph[u] = []
    if v not in graph:
        graph[v] = []
    graph[u].append(v)
    graph[v].append(u)  # undirected
"""

GRAPH_CODE_3 = """
# Breadth-First Search
from collections import deque

def bfs(graph, start):
    visited = set()
    queue = deque([start])
    visited.add(start)
    while queue:
        node = queue.popleft()
        print(node, end=' ')
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

bfs(graph, 'A')  # A B C D E
"""

CHOICES = [("Fast access by index?", "Array"), ("Frequent insertions and deletions?", "Linked list"),
           ("Last in, first out?", "Stack"), ("First in, first out?", "Queue"),
           ("Fast lookups by key?", "Hash table"), ("Hierarchical data?", "Tree"),
           ("Complex relationships?", "Graph")]

STRENGTHS = [("Array", "O(1) access", "O(n) insert and delete"),
             ("Linked list", "O(1) insert and delete", "O(n) access"),
             ("Stack", "O(1) push and pop", "Limited access"),
             ("Queue", "O(1) enqueue and dequeue", "Limited access"),
             ("Hash table", "O(1) average lookup", "Collisions, unordered"),
             ("Tree", "O(log n) search", "Can become unbalanced"),
             ("Graph", "Models any relationship", "Complex, memory heavy")]

ROAD = {"S": (-5.9, 0.0), "A": (-4.2, 1.2), "B": (-4.2, -1.2), "C": (-2.5, 0.0), "T": (-0.9, 0.0)}
ROAD_EDGES = [("S", "A"), ("S", "B"), ("A", "B"), ("A", "C"), ("B", "C"), ("C", "T")]
ROAD_KM = [4, 2, 1, 5, 3, 3]
ROAD_BEST = [("S", "B"), ("B", "C"), ("C", "T")]


def bfs_order(start):
    """The order in which the listing's bfs() prints the vertices."""
    seen, line, k = [start], [start], 0
    while k < len(line):
        for other in ADJ[line[k]]:
            if other not in seen:
                seen.append(other)
                line.append(other)
        k += 1
    return line


# the facts on the board, worked out
assert SCORES[2] == 78
assert SCORES[:2] + [100] + SCORES[2:] == [85, 92, 100, 78, 95, 88]
assert bfs_order("A") == list("ABCDE")
assert BST[0] > BST[1] and BST[1] < BST[4] < BST[0]                 # 40 is found by: left, then right
KM = dict(zip(ROAD_EDGES, ROAD_KM))
assert sum(KM[e] for e in ROAD_BEST) == 8 and 8 < min(4 + 5 + 3, 2 + 1 + 5 + 3, 4 + 1 + 3 + 3)


class DataStructuresVisualJourney(LMSScene):
    lesson_title = "Understanding Data Structures: A Visual Journey"

    def construct(self):
        self.camera.background_color = BG
        self.title_bar = None
        self.cap = None

        self.intro()
        self.arrays()
        self.linked_lists()
        self.stacks()
        self.queues()
        self.hash_tables()
        self.trees()
        self.graphs()
        self.choosing()
        self.closing()

    # ------------------------------------------------------ stage helpers --

    def wipe(self, everything=False, run_time=0.6, shift=None):
        """Clear the board; with ``everything`` the heading goes too."""
        keep = set()
        if self.title_bar is not None and not everything:
            keep.update(self.title_bar.get_family())
        parts = [p for m in self.mobjects for p in m.family_members_with_points() if p not in keep]
        if parts:
            self.play(FadeOut(Group(*parts), shift=ORIGIN if shift is None else shift), run_time=run_time)
        for mob in list(self.mobjects):
            if mob not in keep and not any(p in keep for p in mob.get_family()):
                self.remove(mob)
        self.cap = None
        if everything:
            self.title_bar = None

    def heading(self, s):
        """The scene heading: a title with a blue rule."""
        title = text(s, HEAD, INK, BOLD)
        rule = Line(LEFT, RIGHT, stroke_color=BLUE, stroke_width=3)
        rule.scale_to_fit_width(title.width).next_to(title, DOWN, buff=0.14)
        bar = VGroup(title, rule).move_to(UP * HEAD_Y)
        anims = [FadeIn(bar, shift=DOWN * 0.2)]
        if self.title_bar is not None:
            anims.append(FadeOut(self.title_bar, shift=DOWN * 0.2))
        self.play(*anims, run_time=0.6)
        self.title_bar = bar

    def chapter(self, sid, number, name, tagline=None):
        """A new section: its title card, then its heading."""
        self.scene_start(sid, title=name)
        rule = Line(LEFT * 1.6, RIGHT * 1.6, stroke_color=BLUE, stroke_width=4)
        rest = ([text(f"Structure {number} of 7", SMALL, MUTED)] if number else []) + [text(name, TITLE, INK, BOLD)]
        parts = rest + [rule]
        if tagline:
            rest.append(text(tagline, BODY, BROWN))
            parts.append(rest[-1])
        card = VGroup(*parts).arrange(DOWN, buff=0.38).move_to(DOWN * 0.2)
        self.play(*[FadeIn(m, shift=UP * 0.15) for m in rest], run_time=0.7)
        self.play(Create(rule), run_time=0.9)
        self.play(FadeOut(card), run_time=0.5)
        self.heading(name)

    def finish(self, sid):
        """The scene slides off to the left."""
        self.wipe(everything=True, shift=LEFT * 1.5)
        self.scene_end(sid)

    def fit(self, *mobs, top=BOARD_TOP):
        """Layout guard: bring every mobject onto the board (a little smaller if it must be, then moved)."""
        for mob in mobs:
            if mob.width > 2 * EDGE_X:
                mob.scale(2 * EDGE_X / mob.width)
            if mob.height > top - FLOOR:
                mob.scale((top - FLOOR) / mob.height)
            dx = max(0.0, -EDGE_X - mob.get_left()[0]) - max(0.0, mob.get_right()[0] - EDGE_X)
            dy = max(0.0, FLOOR - mob.get_bottom()[1]) - max(0.0, mob.get_top()[1] - top)
            mob.shift(RIGHT * dx + UP * dy)
        return mobs[0]

    def caption(self, s, y=-2.7, x=0.0, color=INK, size=BODY, weight=NORMAL):
        """Animations that replace the line under the picture (``s`` None: remove it)."""
        new = None
        if s:
            new = self.fit(fitted_text(s, 2 * EDGE_X, size, color, weight).move_to(P(x, y)))
        anims = ([FadeOut(self.cap)] if self.cap is not None else []) + (
            [FadeIn(new, shift=UP * 0.15)] if new is not None else [])
        self.cap = new
        return anims

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

    @classmethod
    def flat(cls, what):
        """Animations from a single animation or a (nested) list of them."""
        if not isinstance(what, (list, tuple)):
            return [what]
        return [a for item in what for a in cls.flat(item)]

    def do(self, what, run_time=None):
        """Play an animation, a list of animations, or a function that returns one (or plays things itself)."""
        if isinstance(what, (types.FunctionType, types.MethodType)):
            what = what()
        anims = self.flat(what) if what is not None else []
        if anims:
            self.play(*anims, **({"run_time": run_time} if run_time else {}))

    def N(self, nid, spoken, *cues, after=None, pause=TURN_PAUSE):
        """The narrator speaks. ``cues`` are ``(word, what)`` or ``(word, what, run_time)`` in spoken order;
        ``after`` is played once the voice has stopped (the next line waits for it)."""
        n = self.narrate(id=nid, text=spoken, voice=NARRATOR_VOICE, subtitle=True, pause_after=pause)
        for item in cues:
            if item[0]:
                self.cue(n, item[0])
            self.do(item[1], item[2] if len(item) > 2 else None)
        if after is not None:
            self.wait_for_narration(n, include_pause=False)
            self.do(after)
        self.wait_for_narration(n)
        return n

    def step(self, listing, i, *anims, run_time=0.7):
        """One step of a code walk: light line ``i`` of ``listing`` and play ``anims`` with it."""
        todo = listing.focus(i) + self.flat(list(anims))
        if todo:
            self.play(*todo, run_time=run_time)

    def use_cases(self, nid, spoken, items, anchors):
        """A cleared board, then one drawing with its name per use case, each on its own word."""
        head = text("Typical use cases", BODY, BROWN, BOLD).move_to(UP * 1.75)
        pitch = 2 * EDGE_X / len(items)
        cards = []
        for k, (kind, label) in enumerate(items):
            x = -EDGE_X + pitch * (k + 0.5)
            drawing = glyph(kind).scale(1.5).move_to(P(x, 0.1))
            name = place(fitted_text(label, pitch - 0.5, LABEL), x=x, top=-1.0)
            cards.append(VGroup(drawing, name))

        def start():
            self.wipe()
            return FadeIn(head, shift=DOWN * 0.15)

        self.N(nid, spoken, (None, start, 0.5),
               *[(word, (lambda c=c: FadeIn(c, shift=UP * 0.2)), 0.6) for word, c in zip(anchors, cards)])

    # ================== 1. INTRODUCTION: WHY DO WE NEED DATA STRUCTURES? ===

    def intro(self):
        self.scene_start("S01_intro", title="Why Do We Need Data Structures?")

        title = text("Understanding Data Structures", TITLE, INK, BOLD)
        rule = Line(LEFT * 2.2, RIGHT * 2.2, stroke_color=BLUE, stroke_width=4)
        tag = text("A visual journey", BODY, BROWN)
        opening = VGroup(title, rule, tag).arrange(DOWN, buff=0.4)
        self.fit(opening, top=TOP)
        self.play(FadeIn(title, shift=UP * 0.2), Create(rule), run_time=1.0)
        self.play(FadeIn(tag, shift=UP * 0.15), run_time=0.7)

        # ---- the chaos: data with no order
        rng = random.Random(7)

        def near(spot):
            return P(spot[0] + rng.uniform(-0.12, 0.12), spot[1] + rng.uniform(-0.22, 0.22))

        chaos = VGroup(*[code(s, SMALL, rng.choice([INK, INK, MUTED, MUTED, BLUE, BROWN])).rotate(rng.uniform(-0.3, 0.3))
                         .move_to(near(spot)) for s, spot in zip(CHAOS, CHAOS_SPOTS)])

        def enter():
            self.play(FadeOut(opening), run_time=0.5)
            self.heading("Why do we need data structures?")
            return LaggedStart(*[FadeIn(m, scale=0.6) for m in chaos], lag_ratio=0.04, run_time=2.0)

        def swirl(by):
            """Every piece drifts to another place."""
            spots = CHAOS_SPOTS[by:] + CHAOS_SPOTS[:by]
            return [m.animate.move_to(near(spot)) for m, spot in zip(chaos, spots)]

        query = code("Find user #7,432", BODY, BLUE).move_to(LEFT * 0.4 + UP * 0.45)
        spinner = Arc(radius=0.24, start_angle=0, angle=1.5 * PI, stroke_color=FLASH, stroke_width=5)
        spinner.next_to(query, RIGHT, buff=0.4)
        failed = text("Search failed: took too long", LABEL, BAD, BOLD).move_to(DOWN * 0.45)

        def ask():
            middle = [m for m in chaos if abs(m.get_x()) < 3.7 and -0.95 < m.get_y() < 1.2]
            others = [m for m in chaos if m not in middle]
            self.play(FadeOut(Group(*middle)), *[m.animate.set_opacity(0.35) for m in others], run_time=0.6)
            return FadeIn(query, shift=UP * 0.15)

        def spin(first=False):
            if first:
                self.play(FadeIn(spinner), run_time=0.3)
            return Rotate(spinner, angle=-2 * TAU, about_point=spinner.get_arc_center(), rate_func=linear, run_time=1.8)

        self.N("s1_01", "Imagine you are building an app. You have user names, product prices, messages, locations, "
                        "timestamps. Thousands, maybe millions, of pieces of data. Now imagine storing all of it with "
                        "no order, no rules, no structure.",
               (None, enter),
               ("Thousands", lambda: swirl(1), 2.0),
               ("order", lambda: swirl(9), 2.0))
        self.N("s1_02", "Finding anything would be a nightmare. Your app would be slow. Your users would leave. Your "
                        "code would be a tangled mess.",
               ("Finding", ask, 0.5),
               ("slow", lambda: spin(True)),
               ("leave", spin),
               ("tangled", lambda: [FadeOut(spinner), FadeIn(failed, shift=UP * 0.15)], 0.6))

        # ---- data, operations, constraints
        names = ("Data", "Operations", "Constraints")
        boxes = VGroup(*[cell(1.1, BLUE, 3.4) for _ in names]).arrange(RIGHT, buff=1.2).move_to(UP * 0.7)
        words = [text(s, BODY, INK, BOLD).move_to(b) for s, b in zip(names, boxes)]
        subs = [text(s, LABEL, BROWN).next_to(b, DOWN, buff=0.35)
                for s, b in zip(("What we store", "What we do with it", "Memory, speed, scale"), boxes)]
        links = [Arrow(a.get_right(), b.get_left(), buff=0.12, color=BROWN, stroke_width=4, tip_length=0.22)
                 for a, b in zip(boxes, boxes[1:])]
        ops = text("Search, insert, delete, update, sort", LABEL, BLUE).move_to(DOWN * 1.75)
        self.fit(boxes, ops, *subs)

        def three():
            self.wipe()
            return LaggedStart(*[FadeIn(VGroup(b, w), shift=UP * 0.2) for b, w in zip(boxes, words)], lag_ratio=0.25,
                               run_time=1.2)

        self.N("s1_03", "This is why data structures exist. Their primary purpose is to organize data, so that we can "
                        "perform operations on it, searching, inserting, deleting, updating, sorting, as efficiently "
                        "as possible.",
               ("exist", three),
               ("organize", lambda: [ring(boxes[0]), FadeIn(subs[0], shift=UP * 0.15)], 0.8),
               ("operations", lambda: [GrowArrow(links[0]), ring(boxes[1]), FadeIn(subs[1], shift=UP * 0.15)], 0.8),
               ("searching", lambda: FadeIn(ops, shift=UP * 0.15), 0.6),
               ("efficiently", lambda: [GrowArrow(links[1]), ring(boxes[2]), FadeIn(subs[2], shift=UP * 0.15)], 0.8))

        # ---- every structure is a trade-off: the balance
        pivot = UP * 0.9
        post = Line(DOWN * 1.5, pivot, stroke_color=MUTED, stroke_width=5)
        foot = Triangle(stroke_color=MUTED, stroke_width=3, fill_color=MUTED, fill_opacity=1)
        foot.scale_to_fit_height(0.4).move_to(DOWN * 1.7)
        beam = Line(pivot + LEFT * 3, pivot + RIGHT * 3, stroke_color=INK, stroke_width=5)

        def pan(x, label, color):
            hang = pivot + RIGHT * x
            dish = Line(LEFT * 0.8, RIGHT * 0.8, stroke_color=color, stroke_width=6).move_to(hang + DOWN * 0.9)
            strings = VGroup(Line(hang, dish.get_left(), stroke_color=MUTED, stroke_width=2),
                             Line(hang, dish.get_right(), stroke_color=MUTED, stroke_width=2))
            return VGroup(strings, dish, text(label, BODY, color, BOLD).next_to(dish, DOWN, buff=0.2))

        speed, memory = pan(-3, "Speed", BLUE), pan(3, "Memory", BROWN)
        tilt = {"now": 0.0}

        def trade(to, s):
            """The beam tips (``to`` > 0: the speed side goes down) and the trade-off is named."""
            turn, drop = to - tilt["now"], 3 * (math.sin(to) - math.sin(tilt["now"]))
            tilt["now"] = to
            return [Rotate(beam, angle=turn, about_point=pivot), speed.animate.shift(DOWN * drop),
                    memory.animate.shift(UP * drop)] + self.caption(s, y=-2.75)

        def balance():
            self.wipe()
            return [FadeIn(VGroup(post, foot, beam)), FadeIn(speed, shift=UP * 0.15), FadeIn(memory, shift=UP * 0.15)]

        self.N("s1_04", "Every data structure is a trade off. Some are fast to search, but slow to insert. Some use "
                        "more memory, but give you instant access. Some are simple, but do not scale. Some are "
                        "complex, but handle millions of operations per second.",
               (None, balance, 0.8),
               ("search", lambda: trade(0.14, "Fast to search, slow to insert"), 0.8),
               ("memory", lambda: trade(-0.14, "More memory, instant access"), 0.8),
               ("simple", lambda: trade(0.14, "Simple, but does not scale"), 0.8),
               ("complex", lambda: trade(-0.14, "Complex, but millions of operations per second"), 0.8))

        # ---- ten seconds against ten milliseconds
        asks = phrase(text("When?", HEAD, BLUE, BOLD), text("Why?", HEAD, BLUE, BOLD), buff=1.2).move_to(UP * 1.7)
        slow_t = place(text("10 seconds", BODY), left=-6.3, y=0.3)
        fast_t = place(text("10 milliseconds", BODY), left=-6.3, y=-1.1)
        slow_bar = Rectangle(width=8.6, height=0.5, stroke_width=0, fill_color=BROWN, fill_opacity=1)
        place(slow_bar, left=-2.3, y=0.3)
        fast_bar = Rectangle(width=0.04, height=0.5, stroke_width=0, fill_color=GOOD, fill_opacity=1)
        place(fast_bar, left=-2.3, y=-1.1)
        times = text("1,000 times faster", BODY, GOOD, BOLD).next_to(fast_bar, RIGHT, buff=0.5)
        self.fit(asks, slow_t, fast_t, slow_bar, times)

        def clear():
            self.wipe()

        self.N("s1_05", "The goal is not to memorize them all. The goal is to understand when, and why, to use each "
                        "one. Because the right choice can turn a program that takes ten seconds, into one that takes "
                        "ten milliseconds.",
               (None, clear),
               ("understand", lambda: LaggedStart(FadeIn(asks[0], shift=UP * 0.2), FadeIn(asks[1], shift=UP * 0.2),
                                                  lag_ratio=0.5, run_time=1.2)),
               ("seconds", lambda: [FadeIn(slow_t), GrowFromEdge(slow_bar, LEFT)], 1.2),
               ("milliseconds", lambda: [FadeIn(fast_t), FadeIn(fast_bar), FadeIn(times, shift=LEFT * 0.2)], 0.8))

        # ---- the toolbox
        box = toolbox()
        looks = phrase(*[text(s, SMALL) for s in ("What it looks like", "When to use it", "Strengths and weaknesses",
                                                  "The code")], buff=0.7).move_to(DOWN * 3.0)
        self.fit(box, looks)

        def open_box():
            self.wipe()
            self.play(FadeIn(VGroup(box.body, box.lid), shift=UP * 0.2), run_time=0.7)
            return [FadeOut(box.lid, shift=UP * 0.5),
                    LaggedStart(*[FadeIn(VGroup(s, i)) for s, i in zip(box.slots, box.items)], lag_ratio=0.12,
                                run_time=1.4)]

        self.N("s1_06", "So let us build your mental toolbox. We will start simple, and work our way up. For each "
                        "structure, we will see what it looks like, when to use it, its strengths and weaknesses, and "
                        "what the code actually looks like.",
               ("toolbox", open_box),
               ("simple", lambda: ring(box.slots[0]), 0.8),
               ("looks", lambda: FadeIn(looks[0], shift=UP * 0.15), 0.5),
               ("when", lambda: FadeIn(looks[1], shift=UP * 0.15), 0.5),
               ("strengths", lambda: FadeIn(looks[2], shift=UP * 0.15), 0.5),
               ("code", lambda: FadeIn(looks[3], shift=UP * 0.15), 0.5))
        self.N("s1_07", "Let us begin.",
               ("begin", lambda: [box.items[0].animate.set_color(BLUE), box.slots[0].animate.set_stroke(BLUE, width=4),
                                  ring(box.slots[0])], 0.9))

        self.finish("S01_intro")

    # ========================================================= 2. ARRAYS ===

    def arrays(self):
        self.chapter("S02_arrays", 1, "Arrays", "The foundation")

        row = Row(ARRAY).at(-0.5, 0.3)
        size_t = place(text("Array of size 8", LABEL, MUTED), left=row.boxes.get_left()[0], y=1.95)
        at3 = row.boxes[3].get_top()
        ptr = VGroup(code("a[3]", LABEL, FLASH),
                     Arrow(at3 + UP * 0.62, at3 + UP * 0.08, buff=0, color=FLASH, stroke_width=4, tip_length=0.2))
        ptr[0].next_to(ptr[1], UP, buff=0.08)
        fast = phrase(code("O(1)", BODY, BLUE), text("Constant time access", BODY), code("0.001 s", LABEL, GOOD),
                      buff=0.4).move_to(DOWN * 1.8)
        brace = Brace(VGroup(row.boxes, row.idx), DOWN, buff=0.12, color=BROWN)
        block = text("One contiguous block: 8 slots × 4 bytes = 32 bytes", LABEL, BROWN).next_to(brace, DOWN, buff=0.15)
        self.fit(row, size_t, fast, block)

        self.N("s2_01", "An array is the simplest data structure: a fixed size collection of elements, stored in "
                        "contiguous memory, and accessed by an index.",
               ("array", lambda: [LaggedStart(*[FadeIn(b, shift=UP * 0.15) for b in row.boxes], lag_ratio=0.12,
                                              run_time=1.4), FadeIn(size_t)]),
               ("contiguous", lambda: ring(row.boxes)),
               ("index", lambda: LaggedStart(*[FadeIn(i, shift=UP * 0.1) for i in row.idx], lag_ratio=0.12,
                                             run_time=1.2)))
        self.N("s2_02", "Each box has a position, an index, starting at zero. Want the element at index three? You go "
                        "straight to it. No searching. No walking. That is O of one, constant time access.",
               ("box", lambda: LaggedStart(*[FadeIn(v, shift=DOWN * 0.15) for v in row.vals], lag_ratio=0.12,
                                           run_time=1.4)),
               ("zero", lambda: hl(row.idx[0], 1.6), 0.7),
               ("three", lambda: [ring(row.boxes[3]), hl(row.idx[3], 1.6)], 0.8),
               ("straight", lambda: FadeIn(ptr, shift=DOWN * 0.3), 0.5),
               ("constant", lambda: FadeIn(fast, shift=UP * 0.15), 0.7))
        self.N("s2_03", "This makes arrays incredibly fast for reading. They are also memory efficient, because the "
                        "computer knows exactly how much space to allocate, and where.",
               ("fast", lambda: hl(fast, 1.05), 0.8),
               ("memory", lambda: [FadeOut(VGroup(ptr, fast)), GrowFromCenter(brace), FadeIn(block, shift=UP * 0.15)]))

        # ---- the drawback: insert 25 at index 2
        newv = code("25", BODY, BROWN).move_to(row.boxes[2].get_center() + UP * 1.25)
        ghost = DashedVMobject(Square(1.0, stroke_color=BAD, stroke_width=3), num_dashes=20)
        ghost.next_to(row.boxes, RIGHT, buff=0)
        full = text("Array full: resize required", LABEL, BAD, BOLD).move_to(DOWN * 1.8)
        cells = list(row.vals)

        def shift_right():
            moves = [cells[k].animate.shift(RIGHT * 1.0) for k in range(len(cells) - 1, 1, -1)]
            return [LaggedStart(*moves, lag_ratio=0.12, run_time=1.6), FadeIn(ghost)]

        def land():
            cells.insert(2, newv)
            return [newv.animate.move_to(row.boxes[2]), cells[-1].animate.set_color(BAD),
                    FadeIn(full, shift=UP * 0.15)]

        self.N("s2_04", "But arrays have drawbacks. Inserting or deleting in the middle means shifting every element "
                        "after it.",
               ("drawbacks", lambda: [FadeOut(VGroup(brace, block)), FadeIn(newv, shift=DOWN * 0.2)], 0.7),
               ("shifting", shift_right),
               after=land)

        # ---- no room: a larger array, and everything is copied
        big = VGroup(*[cell(0.75) for _ in range(16)]).arrange(RIGHT, buff=0).move_to(DOWN * 1.9)
        big_t = place(text("New array of size 16", SMALL, MUTED), left=big.get_left()[0], y=-1.2)
        track = Line(P(-6.0, -3.05), P(-2.0, -3.05), stroke_color=MUTED, stroke_width=6)
        meter = Line(P(-6.0, -3.05), P(-2.0, -3.05), stroke_color=GOOD, stroke_width=8)
        copy_t = text("Copying", SMALL, MUTED).next_to(track, RIGHT, buff=0.3)
        slow = phrase(code("O(n)", BODY, BLUE), text("Linear time", BODY), buff=0.4).move_to(P(3.6, -3.05))
        self.fit(big, big_t, slow)

        def copy_over():
            moves = [c.animate.scale(0.75).move_to(b).set_color(INK) for c, b in zip([c.copy() for c in cells], big)]
            return [LaggedStart(*moves, lag_ratio=0.25, run_time=2.6), FadeIn(track, run_time=0.3),
                    FadeIn(copy_t, run_time=0.3), Create(meter, run_time=2.6, rate_func=linear)]

        self.N("s2_05", "And if you need more space, you often have to create an entirely new, larger array, and copy "
                        "everything over. That is O of n, linear time.",
               ("larger", lambda: [FadeOut(full), FadeIn(big, shift=UP * 0.2), FadeIn(big_t)], 0.8),
               ("copy", copy_over),
               ("linear", lambda: FadeIn(slow, shift=UP * 0.15), 0.6))

        self.use_cases("s2_06", "Typical use cases: storing a list of scores, pixel data in an image, lookup tables, "
                                "and as the underlying structure for many other data structures.",
                       [("bars", "Lists of scores"), ("grid", "Pixel data"), ("table", "Lookup tables"),
                        ("layers", "The base of other structures")],
                       ["scores", "pixel", "lookup", "underlying"])

        # ---- the code
        src = place(Listing(ARRAY_CODE), left=-6.5, top=BOARD_TOP)
        mini = Row(SCORES, side=0.8, size=LABEL, extra=1).at(-3.3, -2.45)
        printed = phrase(text("Prints", LABEL, MUTED), code("78", BODY, GOOD)).move_to(P(1.4, -2.45))
        hundred = code("100", LABEL, BROWN).move_to(mini.boxes[2])
        last = VGroup(mini.boxes[5], mini.idx[5])
        ends = verdict("Fast reads", "Rigid changes")
        place(ends, left=3.3, top=1.9)
        self.fit(src, mini, printed, ends)

        def show():
            self.wipe()
            return src.typed()

        def demo():
            self.step(src, 1, FadeIn(VGroup(mini.boxes[:5], mini.vals, mini.idx[:5]), shift=UP * 0.2))
            self.step(src, 3, ring(mini.boxes[2]), FadeIn(printed, shift=LEFT * 0.15), run_time=0.9)
            self.step(src, 5, FadeIn(last), *[v.animate.shift(RIGHT * 0.8) for v in mini.vals[2:]], run_time=0.9)
            self.play(FadeIn(hundred, shift=DOWN * 0.2), run_time=0.5)
            self.step(src, 7, FadeOut(hundred, shift=UP * 0.2), run_time=0.5)
            self.play(*[v.animate.shift(LEFT * 0.8) for v in mini.vals[2:]], FadeOut(last), run_time=0.8)
            self.step(src, None, run_time=0.3)

        self.N("s2_07", "Here is what it looks like in code.",
               ("code", show),
               after=demo)
        self.N("s2_08", "Simple, fast for reads, but rigid for modifications. That is the array.",
               ("fast", lambda: FadeIn(ends.good, shift=LEFT * 0.15), 0.6),
               ("rigid", lambda: FadeIn(ends.bad, shift=LEFT * 0.15), 0.6))

        self.finish("S02_arrays")

    # =================================================== 3. LINKED LISTS ===

    def linked_lists(self):
        self.chapter("S03_linked", 2, "Linked lists", "Flexible chains")

        # ---- one node
        part_d, part_n = cell(1.1, BLUE, 2.0), cell(1.1, BROWN, 2.0)
        VGroup(part_d, part_n).arrange(RIGHT, buff=0).move_to(LEFT * 1.0 + UP * 0.3)
        d_t, n_t = text("Data", BODY, BLUE, BOLD).move_to(part_d), text("Next", BODY, BROWN, BOLD).move_to(part_n)
        node_t = text("A node", LABEL, MUTED).next_to(VGroup(part_d, part_n), UP, buff=0.3)
        out = Arrow(part_n.get_right() + LEFT * 0.3, part_n.get_right() + RIGHT * 1.6, buff=0, color=BROWN,
                    stroke_width=4, tip_length=0.22)
        to_t = text("To the next node", LABEL, MUTED).next_to(out, RIGHT, buff=0.2)
        one = VGroup(part_d, part_n, d_t, n_t, node_t, out, to_t)
        self.fit(one)

        self.N("s3_01", "A linked list solves the rigidity of arrays. Instead of one contiguous block, each element, "
                        "called a node, contains its data, and a pointer to the next node.",
               ("node", lambda: [FadeIn(VGroup(part_d, d_t), shift=UP * 0.2), FadeIn(node_t)], 0.7),
               ("data", lambda: hl(d_t), 0.7),
               ("pointer", lambda: [FadeIn(VGroup(part_n, n_t), shift=LEFT * 0.2), GrowArrow(out), FadeIn(to_t)], 0.9))

        # ---- five nodes, anywhere in memory; inserting 25
        ch = chain(LIST, x=0.0, y=0.5)
        nodes = ch.nodes
        addrs = VGroup(*[code(a, SMALL, MUTED).next_to(n, UP, buff=0.2) for a, n in zip(ADDRESSES, nodes)])
        new = Node(25).move_to(P((nodes[1].get_x() + nodes[2].get_x()) / 2, -1.5))
        a_in = Arrow(nodes[1].link.get_center(), new.data.get_top() + UP * 0.06, buff=0, color=BROWN, stroke_width=4,
                     tip_length=0.2)
        a_out = Arrow(new.link.get_center(), nodes[2].data.get_bottom() + DOWN * 0.06, buff=0, color=BROWN,
                      stroke_width=4, tip_length=0.2)
        cheap = phrase(text("Only 2 pointers change", BODY), code("O(1)", BODY, BLUE), buff=0.4).move_to(DOWN * 2.8)
        self.fit(ch, addrs, new, cheap)

        def to_chain():
            self.play(FadeOut(one), run_time=0.5)
            return [LaggedStart(*[FadeIn(n, shift=UP * 0.15) for n in nodes], lag_ratio=0.15, run_time=1.2),
                    LaggedStart(*[GrowArrow(a) for a in ch.arrows], lag_ratio=0.2, run_time=1.2)]

        self.N("s3_02", "This means elements can be scattered anywhere in memory. Inserting or deleting is as simple "
                        "as adjusting a few pointers.",
               (None, to_chain),
               ("scattered", lambda: LaggedStart(*[FadeIn(a, shift=DOWN * 0.1) for a in addrs], lag_ratio=0.15,
                                                 run_time=1.0)),
               ("Inserting", lambda: FadeIn(new, shift=UP * 0.3), 0.7),
               ("pointers", lambda: [FadeOut(ch.arrows[1]), GrowArrow(a_in), GrowArrow(a_out)], 0.9))
        self.N("s3_03", "No shifting. No copying. That is the power of linked lists.",
               ("shifting", lambda: FadeIn(cheap, shift=UP * 0.15), 0.6),
               ("power", lambda: [hl(a_in), hl(a_out)], 0.8))

        # ---- variations: doubly linked, circular
        def beads(values, y):
            return VGroup(*[VGroup(cell(0.85), code(str(v), LABEL)) for v in values]).arrange(RIGHT, buff=1.15).move_to(
                UP * y)

        two_t = text("Doubly linked list", LABEL, BROWN, BOLD).move_to(UP * 2.1)
        two = beads([10, 20, 30, 40], 1.15)
        fwd = [Arrow(a.get_right() + UP * 0.16, b.get_left() + UP * 0.16, buff=0.08, color=BROWN, stroke_width=4,
                     tip_length=0.2) for a, b in zip(two, two[1:])]
        back = [Arrow(b.get_left() + DOWN * 0.16, a.get_right() + DOWN * 0.16, buff=0.08, color=BLUE, stroke_width=4,
                      tip_length=0.2) for a, b in zip(two, two[1:])]
        loop_t = text("Circular linked list", LABEL, BROWN, BOLD).move_to(DOWN * 0.55)
        loop = beads([10, 20, 30, 40], -1.5)
        nxt = [Arrow(a.get_right(), b.get_left(), buff=0.08, color=BROWN, stroke_width=4, tip_length=0.2)
               for a, b in zip(loop, loop[1:])]
        x_last, x_first = loop[-1].get_x(), loop[0].get_x()
        around = VMobject(stroke_color=BROWN, stroke_width=4).set_points_as_corners(
            [loop[-1].get_bottom(), P(x_last, -2.6), P(x_first, -2.6)])
        home = Arrow(P(x_first, -2.6), loop[0].get_bottom(), buff=0, color=BROWN, stroke_width=4, tip_length=0.2)

        def clear():
            self.wipe()

        def close_loop():
            self.play(Create(around), run_time=0.8)
            return GrowArrow(home)

        self.N("s3_04", "There are variations: doubly linked lists, where each node points both forward and backward, "
                        "and circular linked lists, where the last node loops back to the first.",
               (None, clear),
               ("doubly", lambda: [FadeIn(two_t), FadeIn(two, shift=UP * 0.2), *[GrowArrow(a) for a in fwd]], 0.9),
               ("backward", lambda: [GrowArrow(a) for a in back], 0.8),
               ("circular", lambda: [FadeIn(loop_t), FadeIn(loop, shift=UP * 0.2), *[GrowArrow(a) for a in nxt]], 0.9),
               ("loops", close_loop, 0.4))

        # ---- the trade-off: no jumping to the fifth node
        ch2 = chain(LIST, x=0.0, y=0.5)
        head = pointer("head", ch2.nodes[0], BLUE, UP)
        walker = pointer("1", ch2.nodes[0], FLASH, DOWN)
        slow = phrase(text("5 steps to reach the 5th node", BODY), code("O(n)", BODY, BLUE), buff=0.4).move_to(DOWN * 2.3)
        self.fit(ch2, head, slow)

        def again():
            self.wipe()
            return FadeIn(ch2, shift=UP * 0.2)

        def walk():
            self.play(FadeIn(walker, shift=UP * 0.15), run_time=0.4)
            for k in range(1, len(LIST)):
                self.play(walker.animate.set_x(ch2.nodes[k].data.get_x()), run_time=0.45)
                walker[0].become(code(str(k + 1), LABEL, FLASH).move_to(walker[0]))
            self.play(ring(ch2.nodes[-1]), run_time=0.7)

        self.N("s3_05", "But there is a trade off. To find the fifth element, you cannot jump directly. You have to "
                        "start at the head, and follow the chain.",
               (None, again, 0.7),
               ("fifth", lambda: ring(ch2.nodes[-1]), 0.8),
               ("head", lambda: FadeIn(head, shift=DOWN * 0.15), 0.5),
               ("follow", walk),
               after=lambda: FadeIn(slow, shift=UP * 0.15))

        self.use_cases("s3_06", "Typical use cases: implementing stacks and queues, managing playlists, browser "
                                "history, and undo and redo functionality.",
                       [("layers", "Stacks and queues"), ("lines", "Playlists"), ("back", "Browser history"),
                        ("undo", "Undo and redo")],
                       ["stacks", "playlists", "browser", "undo"])

        # ---- the code
        left = place(Listing(LIST_CODE_A), left=-6.5, top=BOARD_TOP)
        right = place(Listing(LIST_CODE_B), left=0.3, top=BOARD_TOP)
        small = dict(dw=0.7, lw=0.5, h=0.7, size=LABEL)
        mc = chain([10, 20, 30], x=-2.1, y=-2.6, gap=0.6, **small)
        five = Node(5, **small).move_to(P(-5.7, -2.6))
        a5 = link_arrow(five, mc.nodes[0])
        ends = verdict("Flexible changes", "Slower access")
        place(ends, left=3.3, y=-2.6)
        self.fit(left, right, mc, five, ends)

        def show():
            self.wipe()
            return [left.typed(), right.typed()]

        def demo():
            self.step(left, 6, FadeIn(mc.nodes[0], shift=UP * 0.15))
            self.step(left, 7, GrowArrow(mc.arrows[0]), FadeIn(mc.nodes[1], shift=UP * 0.15))
            self.step(left, 8, GrowArrow(mc.arrows[1]), FadeIn(mc.nodes[2], shift=UP * 0.15))
            self.step(left, None, *right.focus(1), FadeIn(five, shift=UP * 0.15))
            self.step(right, 2, GrowArrow(a5))
            self.step(right, 3, ring(five))
            self.step(right, 7, run_time=0.4)
            for n in (five, *mc.nodes):
                self.play(ring(n), run_time=0.45)
            self.step(right, None, run_time=0.3)

        self.N("s3_07", "Here is the code.",
               ("code", show),
               after=demo)
        self.N("s3_08", "Flexible, efficient for modifications, but slower for access. That is the linked list.",
               ("efficient", lambda: FadeIn(ends.good, shift=LEFT * 0.15), 0.6),
               ("slower", lambda: FadeIn(ends.bad, shift=LEFT * 0.15), 0.6))

        self.finish("S03_linked")

    # ========================================================= 4. STACKS ===

    def stacks(self):
        self.chapter("S04_stacks", 3, "Stacks", "Last in, first out")

        cx, base = -3.4, -2.5

        def slot(k, x=cx, floor=base, pitch=0.63):
            return P(x, floor + 0.36 + pitch * k)

        can = tub(2.9, 3.6).move_to(P(cx, base + 1.8))
        plates = [plate(k + 1).move_to(slot(k)) for k in range(4)]
        push_t = VGroup(text("Push", BODY, BLUE, BOLD),
                        Arrow(UP * 0.5, DOWN * 0.5, buff=0, color=BLUE, stroke_width=5, tip_length=0.25))
        push_t.arrange(DOWN, buff=0.15).move_to(P(cx - 2.5, 0.3))
        pop_t = VGroup(text("Pop", BODY, BROWN, BOLD),
                       Arrow(DOWN * 0.5, UP * 0.5, buff=0, color=BROWN, stroke_width=5, tip_length=0.25))
        pop_t.arrange(DOWN, buff=0.15).move_to(P(cx + 2.5, 0.3))
        lifo = place(text("Last in, first out", BODY, BROWN, BOLD), left=0.6, y=1.8)
        ops = [phrase(code(a, LABEL, BLUE, BOLD), text(b, LABEL), buff=0.35)
               for a, b in (("push", "Add to the top"), ("pop", "Remove from the top"),
                            ("peek", "Look at the top, keep it"))]
        for k, op in enumerate(ops):
            place(op, left=0.6, y=0.6 - 0.8 * k)
        self.fit(can, push_t, lifo, *ops)

        def fifth():
            """A fresh fifth plate, on the top of the stack."""
            return plate(5, color=BROWN).move_to(slot(4))

        tops = [fifth(), fifth()]

        self.N("s4_01", "A stack works like a stack of plates. You add to the top, and you remove from the top. Last "
                        "in, first out.",
               ("plates", lambda: [Create(can), LaggedStart(*[FadeIn(p, shift=DOWN * 0.4) for p in plates],
                                                            lag_ratio=0.25, run_time=1.4)]),
               ("add", lambda: [FadeIn(tops[0], shift=DOWN * 0.6), FadeIn(push_t)], 0.7),
               ("remove", lambda: [FadeOut(tops[0], shift=UP * 0.6), FadeIn(pop_t)], 0.7),
               ("Last", lambda: FadeIn(lifo, shift=UP * 0.15), 0.6))
        self.N("s4_02", "The core operations are push, to add to the top, and pop, to remove from the top. You can "
                        "also peek, to see the top without removing it.",
               ("push", lambda: [FadeIn(ops[0], shift=LEFT * 0.15), FadeIn(tops[1], shift=DOWN * 0.6), hl(push_t[0])],
                0.8),
               ("pop", lambda: [FadeIn(ops[1], shift=LEFT * 0.15), FadeOut(tops[1], shift=UP * 0.6), hl(pop_t[0])], 0.8),
               ("peek", lambda: [FadeIn(ops[2], shift=LEFT * 0.15), ring(plates[3])], 0.9))

        # ---- stacks everywhere: undo, back, the call stack
        shows = []
        for x, name, items, act in ((-4.4, "Undo", ("Type A", "Type B", "Type C"), "Undo removes Type C"),
                                    (0.0, "Back button", ("Page 1", "Page 2", "Page 3"), "Back returns to Page 2"),
                                    (4.4, "Call stack", ("main()", "foo()", "bar()"), "Return leaves bar()")):
            pile = [plate(s, w=2.8, h=0.6).move_to(P(x, -1.4 + 0.68 * k)) for k, s in enumerate(items)]
            shows.append((text(name, LABEL, BROWN, BOLD).move_to(P(x, 1.9)), pile,
                          text(act, SMALL, BLUE).move_to(P(x, -2.6))))

        def build(k, first=False):
            if first:
                self.wipe()
            name, pile, _ = shows[k]
            return [FadeIn(name), LaggedStart(*[FadeIn(p, shift=DOWN * 0.4) for p in pile], lag_ratio=0.3, run_time=1.0)]

        def take(k):
            _, pile, act = shows[k]
            return [FadeOut(pile[-1], shift=UP * 0.6), FadeIn(act, shift=UP * 0.15)]

        self.N("s4_03", "Stacks are everywhere in computing. The undo button in your editor? A stack of actions. The "
                        "back button in your browser? A stack of pages. Function calls in your program? A call stack.",
               ("undo", lambda: build(0, True)),
               ("actions", lambda: take(0), 0.7),
               ("back", lambda: build(1)),
               ("pages", lambda: take(1), 0.7),
               ("Function", lambda: build(2)),
               ("program", lambda: take(2), 0.7))

        self.use_cases("s4_04", "Typical use cases: undo and redo, expression evaluation, backtracking algorithms, "
                                "and depth first search.",
                       [("undo", "Undo and redo"), ("expr", "Expression evaluation"), ("maze", "Backtracking"),
                        ("tree", "Depth first search")],
                       ["undo", "expression", "backtracking", "depth"])

        # ---- the code, with the stack it builds
        src = place(Listing(STACK_CODE, MIN_FONT), left=-6.5, top=BOARD_TOP)
        x2, base2 = 3.9, -2.3
        can2 = tub(2.6, 2.4).move_to(P(x2, base2 + 1.2))
        pile = [plate(v, w=2.2).move_to(slot(k, x2, base2)) for k, v in enumerate((10, 20, 30))]
        got = [code(s, LABEL, GOOD).move_to(P(x2, 0.7)) for s in ("top = 30", "top = 20", "is_empty = False")]
        ends = verdict("O(1) push and pop", "Only the top is reachable")
        place(ends, left=0.9, top=2.2)
        self.fit(src, can2, ends)

        def show():
            self.wipe()
            return src.typed()

        def demo():
            self.step(src, 1, Create(can2))
            for k in range(3):
                self.step(src, 3 + k, FadeIn(pile[k], shift=DOWN * 0.5), run_time=0.55)
            self.step(src, 7, FadeOut(pile[2], shift=UP * 0.5), FadeIn(got[0]))
            self.step(src, 9, ring(pile[1]), FadeOut(got[0]), FadeIn(got[1]), run_time=0.9)
            self.step(src, 11, FadeOut(got[1]), FadeIn(got[2]))
            self.step(src, None, FadeOut(got[2]), run_time=0.4)

        self.N("s4_05", "Here is the code.",
               ("code", show),
               after=demo)
        self.N("s4_06", "Simple, fast, and perfect for last in, first out problems. That is the stack.",
               ("fast", lambda: FadeIn(ends.good, shift=LEFT * 0.15), 0.6),
               ("stack", lambda: FadeIn(ends.bad, shift=LEFT * 0.15), 0.6))

        self.finish("S04_stacks")

    # ========================================================= 5. QUEUES ===

    def queues(self):
        self.chapter("S05_queues", 4, "Queues", "First in, first out")

        ground = -0.1

        def stand(who, x):
            who.move_to(P(x, 0.0))
            return who.shift(UP * (ground + 0.05 - who[1].get_bottom()[1]))

        xs = [-4.0 + 1.3 * k for k in range(5)]
        people = [stand(person(), x) for x in xs]
        late = stand(person(BROWN), xs[-1])
        floor = Line(P(-5.6, ground), P(3.2, ground), stroke_color=MUTED, stroke_width=3)
        desk = Line(P(-5.2, ground), P(-5.2, 1.1), stroke_color=BROWN, stroke_width=6)
        desk_t = text("Counter", SMALL, BROWN).next_to(desk, UP, buff=0.12)
        fifo = place(text("First in, first out", BODY, BROWN, BOLD), left=1.3, y=1.9)
        deq = VGroup(text("Dequeue", LABEL, BLUE, BOLD), text("Remove from the front", SMALL, MUTED))
        deq.arrange(DOWN, buff=0.15).move_to(P(-3.9, -1.4))
        enq = VGroup(text("Enqueue", LABEL, BLUE, BOLD), text("Add to the back", SMALL, MUTED))
        enq.arrange(DOWN, buff=0.15).move_to(P(1.4, -1.4))
        self.fit(floor, desk_t, fifo, deq, enq)

        def serve():
            return [FadeOut(people[0], shift=LEFT * 0.9), *[p.animate.shift(LEFT * 1.3) for p in people[1:]],
                    FadeIn(late, shift=LEFT * 0.9)]

        self.N("s5_01", "A queue is the opposite of a stack. First in, first out. Like a line at a coffee shop: the "
                        "first person in line gets served first.",
               ("queue", lambda: [FadeIn(floor), LaggedStart(*[FadeIn(p, shift=LEFT * 0.3) for p in people],
                                                             lag_ratio=0.2, run_time=1.2)]),
               ("First", lambda: FadeIn(fifo, shift=UP * 0.15), 0.6),
               ("coffee", lambda: [Create(desk), FadeIn(desk_t)], 0.6),
               ("served", serve),
               after=lambda: [FadeIn(deq, shift=UP * 0.15), FadeIn(enq, shift=UP * 0.15)])

        # ---- queues that keep work in order
        lanes = []
        for k, (name, items) in enumerate((("Printer", ("Document 1", "Document 2", "Document 3")),
                                           ("CPU", ("Process A", "Process B", "Process C")),
                                           ("Messages", ("Msg 1", "Msg 2", "Msg 3")))):
            y = 1.3 - 1.6 * k
            tiles = [VGroup(cell(0.75, BLUE, 2.6), code(s, SMALL)).move_to(P(-1.6 + 3.3 * j, y))
                     for j, s in enumerate(items)]
            for tile in tiles:
                tile[1].move_to(tile[0])
            flows = [Arrow(a.get_right(), b.get_left(), buff=0.08, color=BROWN, stroke_width=4, tip_length=0.2)
                     for a, b in zip(tiles, tiles[1:])]
            lanes.append(VGroup(place(text(name, LABEL, BROWN, BOLD), left=-6.3, y=y), *tiles, *flows))
        self.fit(*lanes)

        def first_lane():
            self.wipe()
            return FadeIn(lanes[0], shift=RIGHT * 0.2)

        self.N("s5_02", "Queues are essential for managing tasks in order. Printer jobs? A queue. CPU scheduling? A "
                        "queue. Messages in a distributed system? A queue.",
               ("Printer", first_lane, 0.7),
               ("scheduling", lambda: FadeIn(lanes[1], shift=RIGHT * 0.2), 0.7),
               ("Messages", lambda: FadeIn(lanes[2], shift=RIGHT * 0.2), 0.7))

        # ---- variations: the priority queue and the deque
        prio_t = place(text("Priority queue", LABEL, BROWN, BOLD), left=-6.3, y=2.1)
        px = [-2.4 + 1.2 * k for k in range(5)]
        line_y = 0.35
        waiting = [person().move_to(P(x, line_y + 0.39)) for x in px[:4]]
        vip = person(BROWN, "VIP").move_to(P(px[4], line_y + 0.39))
        vip.shift(UP * (waiting[0].get_bottom()[1] - vip[1].get_bottom()[1]))
        p_floor = Line(P(-3.6, line_y - 0.05), P(3.4, line_y - 0.05), stroke_color=MUTED, stroke_width=3)
        deque_t = text("Deque (double ended queue)", LABEL, BROWN, BOLD).move_to(DOWN * 1.0)
        dq = Row([1, 2, 3, 4, 5], side=0.8, size=LABEL, index=False).at(0.0, -2.2)
        both = VGroup()
        for side in (LEFT, RIGHT):
            edge = dq.boxes.get_edge_center(side)
            both.add(VGroup(DoubleArrow(edge + side * 0.15, edge + side * 1.45, buff=0, color=BROWN, stroke_width=4,
                                        tip_length=0.2),
                            text("Add or remove", SMALL).next_to(edge + side * 1.6, side, buff=0)))
        self.fit(prio_t, deque_t, both)

        def clear():
            self.wipe()

        def jump():
            return [vip.animate(path_arc=PI / 3).shift(LEFT * 4.8), *[p.animate.shift(RIGHT * 1.2) for p in waiting]]

        self.N("s5_03", "There are variations. A priority queue serves items based on importance, not arrival time. A "
                        "deque, a double ended queue, lets you add or remove from both ends.",
               (None, clear),
               ("priority", lambda: [FadeIn(prio_t), FadeIn(p_floor), FadeIn(Group(*waiting, vip), shift=UP * 0.2)],
                0.8),
               ("importance", jump, 1.2),
               ("deque", lambda: [FadeIn(deque_t), FadeIn(dq, shift=UP * 0.2)], 0.8),
               ("both", lambda: [FadeIn(both[0], shift=RIGHT * 0.2), FadeIn(both[1], shift=LEFT * 0.2)], 0.8))

        self.use_cases("s5_04", "Typical use cases: task scheduling, breadth first search, handling requests in web "
                                "servers, and buffering data streams.",
                       [("calendar", "Task scheduling"), ("tree", "Breadth first search"),
                        ("server", "Web server requests"), ("queue", "Buffers for data streams")],
                       ["scheduling", "breadth", "servers", "buffering"])

        # ---- the code, with the queue it builds
        src = place(Listing(QUEUE_CODE, MIN_FONT), left=-6.5, top=BOARD_TOP)
        pipe = VGroup(Line(P(0.3, 0.85), P(5.9, 0.85), stroke_color=MUTED, stroke_width=4),
                      Line(P(0.3, -0.25), P(5.9, -0.25), stroke_color=MUTED, stroke_width=4))
        ends_t = VGroup(text("Front", SMALL, MUTED).move_to(P(0.9, -0.65)), text("Back", SMALL, MUTED).move_to(P(5.3, -0.65)))
        items = [VGroup(cell(0.9), code(str(v), LABEL)).move_to(P(1.3 + 1.1 * k, 0.3)) for k, v in enumerate((10, 20, 30))]
        for item in items:
            item[1].move_to(item[0])
        got = [code(s, LABEL, GOOD).move_to(P(3.1, -1.7)) for s in ("first = 10", "front = 20", "is_empty = False")]
        ends = verdict("O(1) enqueue and dequeue", "Only the ends are reachable")
        place(ends, left=0.3, top=2.3)
        self.fit(src, pipe, ends)

        def show():
            self.wipe()
            return src.typed()

        def demo():
            self.step(src, 2, FadeIn(pipe), FadeIn(ends_t))
            for k in range(3):
                self.step(src, 4 + k, FadeIn(items[k], shift=LEFT * 0.8), run_time=0.55)
            self.step(src, 8, FadeOut(items[0], shift=LEFT * 0.8), items[1].animate.shift(LEFT * 1.1),
                      items[2].animate.shift(LEFT * 1.1), FadeIn(got[0]), run_time=0.9)
            self.step(src, 10, ring(items[1]), FadeOut(got[0]), FadeIn(got[1]), run_time=0.9)
            self.step(src, 12, FadeOut(got[1]), FadeIn(got[2]))
            self.step(src, None, FadeOut(got[2]), run_time=0.4)

        self.N("s5_05", "Here is the code.",
               ("code", show),
               after=demo)
        self.N("s5_06", "Ordered, fair, and perfect for first come, first served problems. That is the queue.",
               ("fair", lambda: FadeIn(ends.good, shift=LEFT * 0.15), 0.6),
               ("queue", lambda: FadeIn(ends.bad, shift=LEFT * 0.15), 0.6))

        self.finish("S05_queues")

    # ==================================================== 6. HASH TABLES ===

    def hash_tables(self):
        self.chapter("S06_hash", 5, "Hash tables", "Instant lookup")

        names = list(HASHES)
        keys = [place(code(s, LABEL), left=-6.3, y=1.5 - 0.9 * k) for k, s in enumerate(names)]
        machine = cell(1.5, BROWN, 2.3).move_to(P(-2.6, 0.15))
        m_code = code("hash(key)", SMALL).move_to(machine)
        m_name = text("Hash function", SMALL, MUTED).next_to(machine, DOWN, buff=0.2)
        buckets = [cell(0.56, BLUE, 2.0).move_to(P(1.9, 1.75 - 0.66 * k)) for k in range(7)]
        idx = [code(str(k), SMALL, MUTED).move_to(P(0.5, b.get_y())) for k, b in enumerate(buckets)]
        entries = {s: code(s, SMALL).move_to(buckets[HASHES[s]]) for s in names if s != "Diana"}
        self.fit(*keys, machine, *buckets)

        def trail(name):
            """The way of one key: into the hash function, out as an index, on to its bucket."""
            key, b = keys[names.index(name)], HASHES[name]
            a_in = Arrow(key.get_right() + RIGHT * 0.15, machine.get_left() + UP * 0.3 * (key.get_y() - 0.15), buff=0,
                         color=BROWN, stroke_width=4, tip_length=0.2)
            num = code(str(b), BODY, BLUE).move_to(P(-0.95, 0.15))
            a_out = Arrow(P(-0.6, 0.15), idx[b].get_left() + LEFT * 0.1, buff=0, color=BROWN, stroke_width=4,
                          tip_length=0.2)
            return a_in, num, a_out

        def send(name, store=True):
            a_in, num, a_out = trail(name)
            self.play(GrowArrow(a_in), run_time=0.45)
            self.play(hl(m_code), FadeIn(num, shift=RIGHT * 0.2), run_time=0.5)
            self.play(GrowArrow(a_out), run_time=0.45)
            if store:
                self.play(FadeIn(entries[name]), ring(buckets[HASHES[name]]), run_time=0.6)
            return VGroup(a_in, num, a_out)

        alice = trail("Alice")
        marks = {}

        def others():
            self.play(FadeOut(VGroup(*alice)), run_time=0.4)
            for name in ("Bob", "Charlie"):
                self.play(FadeOut(send(name)), run_time=0.3)

        def diana():
            marks["diana"] = send("Diana", store=False)

        clash = text("Collision!", LABEL, BAD, BOLD).move_to(P(4.4, buckets[3].get_y()))
        chained = VGroup(cell(0.56, BLUE, 2.0), code("Diana", SMALL)).move_to(P(4.5, buckets[3].get_y()))
        chained[1].move_to(chained[0])
        c_link = Arrow(buckets[3].get_right(), chained.get_left(), buff=0.05, color=BROWN, stroke_width=4, tip_length=0.2)
        chain_t = text("Chaining", SMALL, BROWN).next_to(chained, UP, buff=0.15)
        moved = code("Diana", SMALL, BROWN).move_to(buckets[4])
        open_t = place(text("Open addressing", SMALL, BROWN), left=3.1, y=buckets[4].get_y())

        self.N("s6_01", "A hash table, also called a hash map, is one of the most powerful and widely used data "
                        "structures. It stores key value pairs, and gives you near instant lookups.",
               ("hash", lambda: LaggedStart(*[FadeIn(k, shift=RIGHT * 0.2) for k in keys], lag_ratio=0.2, run_time=1.2)),
               ("stores", lambda: LaggedStart(*[FadeIn(VGroup(b, i), shift=LEFT * 0.2) for b, i in zip(buckets, idx)],
                                              lag_ratio=0.1, run_time=1.4)),
               ("instant", lambda: [ring(b) for b in buckets], 0.9))
        self.N("s6_02", "Here is how it works: you give it a key. The hash function computes an index. The value is "
                        "stored at that index. When you want it back, the same key produces the same index. You go "
                        "straight there.",
               ("key", lambda: [FadeIn(VGroup(machine, m_code, m_name)), GrowArrow(alice[0])], 0.8),
               ("computes", lambda: [hl(m_code), FadeIn(alice[1], shift=RIGHT * 0.2)], 0.7),
               ("stored", lambda: [GrowArrow(alice[2]), FadeIn(entries["Alice"])], 0.8),
               ("same", lambda: [hl(keys[0]), hl(alice[1], 1.3)], 0.8),
               ("straight", lambda: ring(buckets[3]), 0.8),
               after=others)
        self.N("s6_03", "But sometimes, two keys hash to the same index. That is called a collision. Good hash tables "
                        "handle this with strategies like chaining, storing a list at each index, or open addressing, "
                        "finding the next available slot.",
               ("two", diana),
               ("collision", lambda: [buckets[3].animate.set_stroke(BAD, width=5), FadeIn(clash, scale=1.2)], 0.6),
               ("chaining", lambda: [FadeOut(clash), FadeOut(marks["diana"]), GrowArrow(c_link),
                                     FadeIn(chained, shift=LEFT * 0.2), FadeIn(chain_t)], 0.8),
               ("open", lambda: [FadeIn(moved, shift=DOWN * 0.3), FadeIn(open_t), ring(buckets[4])], 0.8))

        # ---- why it matters
        big_o = VGroup(code("O(1)", TITLE, BLUE), text("Average lookup, insert and delete", LABEL)).arrange(DOWN, buff=0.3)
        big_o.move_to(UP * 1.4)
        powers = []
        for k, (kind, name, sub) in enumerate((("db", "Database index", "Find user by ID"),
                                               ("bolt", "Cache", "Store session data"),
                                               ("lines", "Dictionary", "Word to definition"))):
            x = -4.4 + 4.4 * k
            powers.append(VGroup(glyph(kind).scale(1.3).move_to(P(x, -0.9)), text(name, LABEL, INK, BOLD).move_to(P(x, -2.0)),
                                 text(sub, SMALL, BROWN).move_to(P(x, -2.55))))

        def clear():
            self.wipe()

        self.N("s6_04", "On average, lookups, insertions, and deletions are all O of one, constant time. That is why "
                        "hash tables power database indexes, caches, and dictionaries in every programming language.",
               (None, clear),
               ("constant", lambda: FadeIn(big_o, shift=UP * 0.2), 0.7),
               ("database", lambda: FadeIn(powers[0], shift=UP * 0.2), 0.6),
               ("caches", lambda: FadeIn(powers[1], shift=UP * 0.2), 0.6),
               ("dictionaries", lambda: FadeIn(powers[2], shift=UP * 0.2), 0.6))

        self.use_cases("s6_05", "Typical use cases: database indexing, caching, counting frequencies, and "
                                "implementing sets.",
                       [("db", "Database indexing"), ("bolt", "Caching"), ("bars", "Counting frequencies"),
                        ("set", "Sets")],
                       ["indexing", "caching", "counting", "sets"])

        # ---- the code, with the table it builds
        src = place(Listing(HASH_CODE, MIN_FONT), left=-6.5, top=BOARD_TOP)
        t_name = code("user_ages", LABEL, BROWN).move_to(P(3.3, 0.6))
        pairs = [phrase(code(f'"{k}"', LABEL), code(":", LABEL, MUTED), code(str(v), LABEL, BLUE)).move_to(P(3.3, -0.1 - 0.7 * j))
                 for j, (k, v) in enumerate((("Alice", 30), ("Bob", 25), ("Charlie", 35)))]
        gone = Line(pairs[1].get_left() + LEFT * 0.1, pairs[1].get_right() + RIGHT * 0.1, stroke_color=BAD, stroke_width=4)
        got = [code(s, LABEL, GOOD).move_to(P(3.3, -2.5)) for s in ("age = 30", "Found!")]
        ends = verdict("O(1) average lookup", "Collisions, no order")
        place(ends, left=1.2, top=2.3)
        self.fit(src, ends)

        def show():
            self.wipe()
            return src.typed()

        def demo():
            self.step(src, 1, FadeIn(t_name))
            for k in range(3):
                self.step(src, 3 + k, FadeIn(pairs[k], shift=LEFT * 0.3), run_time=0.55)
            self.step(src, 7, ring(pairs[0]), FadeIn(got[0]), run_time=0.9)
            self.step(src, 9, Create(gone), pairs[1].animate.set_opacity(0.35), FadeOut(got[0]))
            self.step(src, 11, ring(pairs[2]), run_time=0.8)
            self.step(src, 12, FadeIn(got[1]))
            self.step(src, None, run_time=0.3)

        self.N("s6_06", "Here is the code.",
               ("code", show),
               after=demo)
        self.N("s6_07", "Fast, flexible, and the backbone of modern software. That is the hash table.",
               ("flexible", lambda: FadeIn(ends.good, shift=LEFT * 0.15), 0.6),
               ("table", lambda: FadeIn(ends.bad, shift=LEFT * 0.15), 0.6))

        self.finish("S06_hash")

    # ========================================================== 7. TREES ===

    def trees(self):
        self.chapter("S07_trees", 6, "Trees", "Hierarchical organization")

        tree = btree([""] * 7, 0.0, 1.6, 1.3, 1.4)
        nodes, edges = tree.nodes, tree.edges
        levels = [text(s, LABEL, BROWN).move_to(P(5.6, 1.6 - 1.4 * k)) for k, s in enumerate(("Root", "Child", "Leaf"))]
        vals = [code(str(v), SMALL).move_to(n) for v, n in zip(BST, nodes)]
        less = text("Smaller", SMALL, BLUE).move_to(P(-2.3, 1.2))
        more = text("Larger", SMALL, BLUE).move_to(P(2.3, 1.2))
        goal = phrase(text("Find", BODY), code("40", BODY, FLASH)).move_to(P(-5.3, 1.6))
        found = tick().next_to(nodes[4], DOWN, buff=0.15)
        self.fit(tree, goal, *levels)

        self.N("s7_01", "A tree is a hierarchical data structure. It starts with a root node, and each node can have "
                        "children. It is like a family tree, or the file system on your computer.",
               ("tree", lambda: FadeIn(nodes[0], scale=0.6), 0.6),
               ("root", lambda: FadeIn(levels[0], shift=LEFT * 0.2), 0.5),
               ("children", lambda: [Create(edges[1]), Create(edges[2]), FadeIn(nodes[1]), FadeIn(nodes[2]),
                                     FadeIn(levels[1], shift=LEFT * 0.2)], 0.8),
               ("family", lambda: [*[Create(edges[k]) for k in range(3, 7)], *[FadeIn(nodes[k]) for k in range(3, 7)],
                                   FadeIn(levels[2], shift=LEFT * 0.2)], 0.8),
               ("file", lambda: self.caption("Like a family tree, or folders inside folders", color=MUTED, size=LABEL), 0.6))
        self.N("s7_02", "The most common type is the binary tree, where each node has at most two children. But when "
                        "you organize a binary tree so that every left child is smaller than its parent, and every "
                        "right child is larger, you get a binary search tree.",
               ("binary", lambda: self.caption("Binary tree: at most 2 children per node", size=LABEL), 0.6),
               ("organize", lambda: LaggedStart(*[FadeIn(v, scale=0.6) for v in vals], lag_ratio=0.15, run_time=1.4)),
               ("left", lambda: [ring(nodes[1]), FadeIn(less)], 0.8),
               ("right", lambda: [ring(nodes[2]), FadeIn(more)], 0.8),
               ("search", lambda: self.caption("Binary search tree: left is smaller, right is larger", color=BLUE,
                                               size=LABEL, weight=BOLD), 0.6))

        def lit(k, color=FLASH):
            anims = [nodes[k].rim.animate.set_stroke(color, width=6)]
            if k:
                anims.append(edges[k].animate.set_stroke(color, width=6))
            return anims

        self.N("s7_03", "Now searching becomes fast. Want to find forty? Start at fifty. Go left. Go right. Found. "
                        "That is O of log n, logarithmic time. Much faster than searching a list.",
               ("forty", lambda: [FadeOut(VGroup(less, more)), FadeIn(goal, shift=RIGHT * 0.2)], 0.6),
               ("fifty", lambda: lit(0), 0.5),
               ("left", lambda: lit(1), 0.5),
               ("right", lambda: lit(4), 0.5),
               ("Found", lambda: [nodes[4].rim.animate.set_stroke(GOOD, width=6), FadeIn(found, scale=0.6)], 0.5),
               ("logarithmic", lambda: self.caption("3 steps for 7 nodes: O(log n)", color=BLUE, size=LABEL, weight=BOLD),
                0.6))

        # ---- unbalanced, then balanced again
        lean = [disc(v).move_to(P(-3.0 + 1.3 * k, 1.8 - 1.05 * k)) for k, v in enumerate(LIST)]
        lean_edges = [Line(a.get_center(), b.get_center(), buff=0.32, stroke_color=MUTED, stroke_width=3)
                      for a, b in zip(lean, lean[1:])]
        homes = [P(-3.4, -1.1), P(-2.2, 0.2), P(0.0, 1.5), P(2.2, 0.2), P(3.4, -1.1)]         # 10 20 30 40 50
        level_edges = [Line(homes[a], homes[b], buff=0.32, stroke_color=MUTED, stroke_width=3)
                       for a, b in ((2, 1), (2, 3), (1, 0), (3, 4))]

        def tilted():
            self.wipe()
            return [LaggedStart(*[FadeIn(n, shift=DOWN * 0.2) for n in lean], lag_ratio=0.2, run_time=1.2),
                    LaggedStart(*[Create(e) for e in lean_edges], lag_ratio=0.2, run_time=1.2)]

        self.N("s7_04", "But if the tree becomes unbalanced, say, all nodes lean to one side, it degrades to a linked "
                        "list, and search becomes O of n.",
               ("unbalanced", tilted),
               ("linked", lambda: [ring(n) for n in lean], 0.9),
               ("search", lambda: self.caption("Unbalanced: search becomes O(n)", y=-1.9, x=-3.4, color=BAD, size=LABEL,
                                               weight=BOLD), 0.6))

        def rebalance():
            self.play(FadeOut(VGroup(*lean_edges)), run_time=0.4)
            self.play(*[n.animate.move_to(p) for n, p in zip(lean, homes)], run_time=1.2)
            return [Create(e) for e in level_edges]

        root_keys = VGroup(cell(0.7, BLUE, 1.0), cell(0.7, BLUE, 1.0)).arrange(RIGHT, buff=0).move_to(UP * 1.2)
        kids = [VGroup(cell(0.7, BLUE, 1.0), cell(0.7, BLUE, 1.0)).arrange(RIGHT, buff=0).move_to(P(x, -0.8))
                for x in (-4.0, 0.0, 4.0)]
        key_text = [code(str(v), LABEL).move_to(c) for group, pair in zip([root_keys] + kids,
                                                                          ((20, 40), (5, 10), (25, 30), (45, 50)))
                    for v, c in zip(pair, group)]
        drops = [Line(root_keys.get_bottom() + RIGHT * dx, kid.get_top(), buff=0.08, stroke_color=MUTED, stroke_width=3)
                 for dx, kid in zip((-1.0, 0.0, 1.0), kids)]

        def b_tree():
            self.wipe()
            self.play(FadeIn(VGroup(root_keys, *kids, *key_text), shift=UP * 0.2), *[Create(d) for d in drops],
                      run_time=0.9)
            return self.caption("B-tree: many keys and many children per node", y=-2.4, size=LABEL)

        self.N("s7_05", "That is why we have balanced trees, like AVL trees and Red Black trees, which automatically "
                        "rearrange themselves to stay efficient. And B trees, used in databases and file systems, "
                        "which can have many children per node.",
               ("balanced", lambda: self.caption("Balanced trees: AVL, Red-Black", y=-1.9, x=-3.4, color=BLUE,
                                                 size=LABEL, weight=BOLD), 0.6),
               ("rearrange", rebalance, 0.7),
               ("databases", b_tree, 0.6),
               ("many", lambda: [ring(root_keys), *[hl(d) for d in drops]], 0.9))

        self.use_cases("s7_06", "Typical use cases: file systems, database indexing, expression parsing, and decision "
                                "making in AI.",
                       [("folder", "File systems"), ("db", "Database indexing"), ("expr", "Expression parsing"),
                        ("tree", "Decision making in AI")],
                       ["file", "database", "expression", "decision"])

        # ---- the code, in three pages, with the tree it builds
        pages = [place(Listing(src, MIN_FONT), left=-6.5, top=BOARD_TOP) for src in (TREE_CODE_1, TREE_CODE_2, TREE_CODE_3)]
        grown = btree(BST, 4.45, 1.6, 0.525, 1.1, r=0.26, size=MIN_FONT)
        asked = code("search(40)", SMALL, FLASH).move_to(P(4.45, -1.6))
        answer = code("search(40): found", SMALL, GOOD).move_to(P(4.45, -1.6))
        ends = verdict("O(log n) search", "Can become unbalanced", SMALL)
        place(ends, left=2.5, top=-2.2)
        self.fit(*pages, grown, ends)

        def show():
            self.wipe()
            return pages[0].typed()

        def grow(k):
            return [FadeIn(grown.nodes[k], scale=0.6)] + ([Create(grown.edges[k])] if k else [])

        def trace(k, color=FLASH):
            anims = [grown.nodes[k].rim.animate.set_stroke(color, width=6)]
            if k:
                anims.append(grown.edges[k].animate.set_stroke(color, width=6))
            return anims

        def demo():
            self.step(pages[0], 10, *grow(0))
            self.play(FadeOut(pages[0]), run_time=0.4)
            self.play(pages[1].typed(1.2))
            for line, k in ((6, 1), (11, 2), (6, 3), (11, 4), (6, 5), (11, 6)):      # goes left: line 6, right: 11
                self.step(pages[1], line, *grow(k), run_time=0.6)
            self.play(FadeOut(pages[1]), run_time=0.4)
            self.play(pages[2].typed(1.2), FadeIn(asked))
            self.step(pages[2], 2, *trace(0))
            self.step(pages[2], 7, *trace(1))
            self.step(pages[2], 8, *trace(4))
            self.step(pages[2], 5, *trace(4, GOOD), FadeOut(asked), FadeIn(answer))
            self.step(pages[2], None, run_time=0.3)

        self.N("s7_07", "Here is the code for a simple binary search tree.",
               ("code", show),
               after=demo)
        self.N("s7_08", "Hierarchical, efficient, and foundational to countless algorithms. That is the tree.",
               ("efficient", lambda: FadeIn(ends.good, shift=LEFT * 0.15), 0.6),
               ("tree", lambda: FadeIn(ends.bad, shift=LEFT * 0.15), 0.6))

        self.finish("S07_trees")

    # ========================================================= 8. GRAPHS ===

    def graphs(self):
        self.chapter("S08_graphs", 7, "Graphs", "Connecting the dots")

        main = graph({"A": (-3.2, 1.2), "B": (-0.6, 1.8), "C": (-2.4, -1.2), "D": (0.4, -0.4), "E": (3.0, 1.0),
                      "F": (2.8, -1.6)},
                     [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("B", "E"), ("D", "E"), ("D", "F"), ("E", "F")],
                     r=0.34, size=LABEL)
        vertex_t = text("Vertex", LABEL, BROWN).next_to(main.nodes["A"], LEFT, buff=0.3)
        edge_t = text("Edge", LABEL, BROWN).move_to(P(1.3, 1.9))
        self.fit(main, vertex_t, edge_t)

        self.N("s8_01", "Finally, we arrive at graphs, the most flexible and general data structure of all.",
               ("graphs", lambda: LaggedStart(*[FadeIn(n, scale=0.6) for n in main.nodes.values()], lag_ratio=0.15,
                                              run_time=1.2)),
               ("flexible", lambda: LaggedStart(*[Create(e) for e in main.edges.values()], lag_ratio=0.12, run_time=1.4)))

        # ---- three things a graph can be
        mini = {"P": (-1.1, 0.8), "Q": (1.1, 0.9), "R": (-0.8, -0.8), "S": (1.0, -0.7)}
        mini_edges = [("P", "Q"), ("P", "R"), ("Q", "S"), ("R", "S"), ("P", "S")]
        initials = dict(zip("PQRS", "ABCD"))

        def panel(x, name, note, **look):
            return VGroup(text(name, LABEL, BROWN, BOLD).move_to(P(x, 2.0)), graph(mini, mini_edges, x=x, y=0.15, **look),
                          fitted_text(note, 4.0, SMALL, MUTED).move_to(P(x, -1.75)))

        uses = [panel(-4.4, "Social network", "People linked by friendships", labels=initials),
                panel(0.0, "Road map", "Cities linked by roads", labels={}, weights=[4, 7, 3, 5, 9]),
                panel(4.4, "The internet", "Computers linked by cables", labels={}, square=True)]
        kinds = [panel(-4.4, "Directed", "Edges have a direction", labels=initials, directed=True),
                 panel(0.0, "Undirected", "Edges go both ways", labels=initials),
                 panel(4.4, "Weighted", "Edges carry a distance or a cost", labels=initials, weights=[4, 7, 3, 5, 9])]

        def first(panels):
            self.wipe()
            return FadeIn(panels[0], shift=UP * 0.2)

        def clear():
            self.wipe()

        self.N("s8_02", "A graph is a collection of vertices, or nodes, connected by edges. It can represent just "
                        "about any relationship: social networks, road maps, the internet, even the spread of a virus.",
               ("vertices", lambda: [ring(main.nodes["A"]), FadeIn(vertex_t)], 0.8),
               ("edges", lambda: [hl(main.edges[("B", "E")], 1.05), FadeIn(edge_t)], 0.8),
               ("social", lambda: first(uses), 0.7),
               ("road", lambda: FadeIn(uses[1], shift=UP * 0.2), 0.7),
               ("internet", lambda: FadeIn(uses[2], shift=UP * 0.2), 0.7))
        self.N("s8_03", "Graphs can be directed, where edges have a direction, or undirected, where they do not. They "
                        "can be weighted, where edges have values like distance or cost, or unweighted.",
               (None, clear),
               ("directed", lambda: FadeIn(kinds[0], shift=UP * 0.2), 0.7),
               ("undirected", lambda: FadeIn(kinds[1], shift=UP * 0.2), 0.7),
               ("weighted", lambda: FadeIn(kinds[2], shift=UP * 0.2), 0.7))

        # ---- matrix or list
        order = list(ADJ)
        m_t = text("Adjacency matrix", LABEL, BROWN, BOLD).move_to(P(-3.65, 2.05))

        def at(i, j):
            return P(-5.2 + 0.62 * j, 1.3 - 0.62 * i)

        heads = VGroup(*[code(s, SMALL, BLUE, BOLD).move_to(at(0, j + 1)) for j, s in enumerate(order)],
                       *[code(s, SMALL, BLUE, BOLD).move_to(at(i + 1, 0)) for i, s in enumerate(order)])
        bits = VGroup(*[code("1", SMALL, BROWN, BOLD).move_to(at(i + 1, j + 1)) if b in ADJ[a]
                        else code("0", SMALL, MUTED).move_to(at(i + 1, j + 1))
                        for i, a in enumerate(order) for j, b in enumerate(order)])
        m_note = text("Fast edge check, more memory", SMALL).move_to(P(-3.65, -2.7))
        l_t = text("Adjacency list", LABEL, BROWN, BOLD).move_to(P(3.5, 2.05))
        rows = VGroup(*[place(phrase(code(a, LABEL, BLUE, BOLD),
                                     Arrow(ORIGIN, RIGHT * 0.7, buff=0, color=BROWN, stroke_width=4, tip_length=0.18),
                                     code(", ".join(ADJ[a]), LABEL)), left=2.2, y=1.3 - 0.72 * i)
                        for i, a in enumerate(order)])
        l_note = text("Less memory, slower edge check", SMALL).move_to(P(3.5, -2.7))
        wall = Line(P(0, 2.2), P(0, -3.0), stroke_color=MUTED, stroke_width=2)
        self.fit(heads, m_note, rows, l_note)

        self.N("s8_04", "They can be represented as an adjacency matrix, a two dimensional array of connections, or "
                        "an adjacency list, where each node stores a list of its neighbors. Each has trade offs in "
                        "memory and speed.",
               (None, clear),
               ("matrix", lambda: [FadeIn(m_t), FadeIn(heads), LaggedStart(*[FadeIn(b) for b in bits], lag_ratio=0.03,
                                                                          run_time=1.4)]),
               ("list", lambda: [Create(wall), FadeIn(l_t), LaggedStart(*[FadeIn(r, shift=LEFT * 0.2) for r in rows],
                                                                        lag_ratio=0.15, run_time=1.2)]),
               ("memory", lambda: [FadeIn(m_note, shift=UP * 0.15), FadeIn(l_note, shift=UP * 0.15)], 0.7))

        # ---- graph algorithms at work
        road_t = text("Shortest path", LABEL, BROWN, BOLD).move_to(P(-3.4, 2.05))
        road = graph(ROAD, ROAD_EDGES, weights=ROAD_KM)
        total = phrase(text("Shortest:", LABEL, MUTED), code("2 + 3 + 3 = 8", LABEL, GOOD)).move_to(P(-3.4, -2.6))
        circle_t = text("Friend suggestions", LABEL, BROWN, BOLD).move_to(P(3.45, 2.05))
        circle = graph({"You": (1.5, 0.0), "A": (3.4, 1.2), "B": (3.4, -1.2), "C": (5.4, 0.0)},
                       [("You", "A"), ("You", "B"), ("A", "C"), ("B", "C")], r=0.42, size=MIN_FONT)
        maybe = DashedLine(circle.nodes["You"].get_center(), circle.nodes["C"].get_center(), buff=0.42, color=BROWN,
                           stroke_width=4)
        maybe_t = text("People you may know", LABEL, BROWN).move_to(P(3.45, -2.6))
        self.fit(road, total, circle, maybe_t)

        def drive():
            for e in ROAD_BEST:
                self.play(road.edges[e].animate.set_stroke(GOOD, width=7),
                          road.nodes[e[1]].rim.animate.set_stroke(GOOD, width=5), run_time=0.5)
            return FadeIn(total, shift=UP * 0.15)

        def start_road():
            self.wipe()
            return [FadeIn(road_t), FadeIn(road, shift=UP * 0.2)]

        self.N("s8_05", "Graph algorithms, like Dijkstra's shortest path, breadth first search, and depth first "
                        "search, are fundamental to computer science. If you have ever used GPS navigation, or seen "
                        "people you may know on social media, you have benefited from graph structures.",
               ("shortest", start_road, 0.8),
               ("navigation", drive, 0.6),
               ("people", lambda: [FadeIn(circle_t), FadeIn(circle, shift=UP * 0.2)], 0.8),
               ("benefited", lambda: [Create(maybe), FadeIn(maybe_t, shift=UP * 0.15),
                                      circle.nodes["C"].rim.animate.set_stroke(BROWN, width=5)], 0.9))

        self.use_cases("s8_06", "Typical use cases: social networks, GPS navigation, network routing, recommendation "
                                "systems, and dependency resolution.",
                       [("net", "Social networks"), ("route", "GPS navigation"), ("server", "Network routing"),
                        ("star", "Recommendation systems"), ("layers", "Dependency resolution")],
                       ["social", "navigation", "routing", "recommendation", "dependency"])

        # ---- the code: the graph itself, then breadth-first search on it
        g1 = place(Listing(GRAPH_CODE_1, MIN_FONT), left=-6.5, top=BOARD_TOP)
        g2 = place(Listing(GRAPH_CODE_2, MIN_FONT), left=-0.9, top=BOARD_TOP)
        g3 = place(Listing(GRAPH_CODE_3, MIN_FONT), left=-6.5, top=BOARD_TOP)
        net = graph({"A": (1.9, 0.6), "B": (3.5, 1.7), "C": (3.5, -0.5), "D": (4.9, 0.6), "E": (6.2, 0.6)},
                    [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E")])
        out_t = place(text("Output:", SMALL, MUTED), left=1.4, y=-1.8)
        visit = bfs_order("A")
        letters = [code(s, LABEL, GOOD).move_to(P(3.1 + 0.5 * k, -1.8)) for k, s in enumerate(visit)]
        found_by = {"A": [("A", "B"), ("A", "C")], "B": [("B", "D")], "C": [], "D": [("D", "E")], "E": []}
        ends = verdict("Models any relationship", "Complex, memory heavy")
        place(ends, left=1.4, top=-2.25)
        self.fit(g1, g2, g3, net, ends)

        def show():
            self.wipe()
            return [g1.typed(), g2.typed()]

        def demo():
            self.step(g2, 6, run_time=0.6)
            self.step(g2, 7, run_time=0.6)
            self.play(FadeOut(VGroup(g1, g2)), run_time=0.4)
            self.play(g3.typed(1.4), FadeIn(net, shift=UP * 0.2), FadeIn(out_t))
            for k, name in enumerate(visit):
                self.step(g3, 7, net.nodes[name].rim.animate.set_stroke(GOOD, width=6), FadeIn(letters[k]),
                          run_time=0.5)
                if found_by[name]:
                    self.step(g3, 12, *[net.edges[e].animate.set_stroke(BROWN, width=6) for e in found_by[name]],
                              run_time=0.5)
            self.step(g3, 13, run_time=0.5)
            self.step(g3, None, run_time=0.3)

        self.N("s8_07", "Here is the code for a simple graph, using an adjacency list.",
               ("code", show),
               after=demo)
        self.N("s8_08", "Flexible, powerful, and capable of modeling almost anything. That is the graph.",
               ("powerful", lambda: FadeIn(ends.good, shift=LEFT * 0.15), 0.6),
               ("graph", lambda: FadeIn(ends.bad, shift=LEFT * 0.15), 0.6))

        self.finish("S08_graphs")

    # ======================================= 9. CHOOSING THE RIGHT TOOL ====

    def choosing(self):
        self.chapter("S09_choose", None, "Choosing the right tool")

        ys = [2.0 - 0.83 * k for k in range(len(CHOICES))]
        root = place(text("Your problem", LABEL, BROWN, BOLD), left=-6.5, y=ys[3])
        asks, picks = [], []
        for (question, answer), y in zip(CHOICES, ys):
            q = place(text(question, LABEL), left=-3.2, y=y)
            twig = Line(root.get_right() + RIGHT * 0.15, P(-3.35, y), stroke_color=MUTED, stroke_width=2)
            asks.append(VGroup(twig, q))
            picks.append(VGroup(Arrow(P(3.45, y), P(4.15, y), buff=0, color=BROWN, stroke_width=4, tip_length=0.18),
                                place(text(answer, LABEL, BLUE, BOLD), left=4.3, y=y)))
        self.fit(root, *asks, *picks)

        def ask(k):
            return lambda: [Create(asks[k][0]), FadeIn(asks[k][1], shift=RIGHT * 0.15)]

        def pick(k):
            return lambda: [GrowArrow(picks[k][0]), FadeIn(picks[k][1], shift=RIGHT * 0.15)]

        self.N("s9_01", "So, which data structure should you use? It depends on the problem.",
               ("which", lambda: FadeIn(root, shift=RIGHT * 0.2), 0.6),
               ("depends", lambda: hl(root), 0.8))
        self.N("s9_02", "Need fast access by index? Array.",
               ("fast", ask(0), 0.5), ("Array", pick(0), 0.5), pause=0.35)
        self.N("s9_03", "Frequent insertions and deletions? Linked list.",
               ("Frequent", ask(1), 0.5), ("Linked", pick(1), 0.5), pause=0.35)
        self.N("s9_04", "Last in, first out? Stack.",
               ("Last", ask(2), 0.5), ("Stack", pick(2), 0.5), pause=0.35)
        self.N("s9_05", "First in, first out? Queue.",
               ("First", ask(3), 0.5), ("Queue", pick(3), 0.5), pause=0.35)
        self.N("s9_06", "Fast lookups by key? Hash table.",
               ("Fast", ask(4), 0.5), ("Hash", pick(4), 0.5), pause=0.35)
        self.N("s9_07", "Hierarchical data? Tree.",
               ("Hierarchical", ask(5), 0.5), ("Tree", pick(5), 0.5), pause=0.35)
        self.N("s9_08", "Complex relationships? Graph.",
               ("Complex", ask(6), 0.5), ("Graph", pick(6), 0.5))

        # ---- the grid: every structure with its strength and its weakness
        lefts = (-5.9, -2.6, 2.3)
        top = [place(text(s, SMALL, BROWN, BOLD), left=x, y=2.05) for s, x in zip(("Structure", "Strength", "Weakness"),
                                                                                  lefts)]
        under = Line(P(-6.1, 1.75), P(6.1, 1.75), stroke_color=BLUE, stroke_width=3)
        lines = []
        for k, (name, plus, minus) in enumerate(STRENGTHS):
            y = 1.35 - 0.64 * k
            lines.append(VGroup(place(text(name, SMALL, BLUE, BOLD), left=lefts[0], y=y),
                                place(text(plus, SMALL), left=lefts[1], y=y),
                                place(text(minus, SMALL, MUTED), left=lefts[2], y=y)))
        self.fit(*top, *lines)

        def grid():
            self.wipe()
            return [FadeIn(VGroup(*top)), Create(under),
                    LaggedStart(*[FadeIn(l, shift=UP * 0.1) for l in lines], lag_ratio=0.15, run_time=1.6)]

        def sweep():
            for line in lines:
                self.play(hl(line[0], 1.08), run_time=0.45)

        self.N("s9_09", "There is no single best structure, only the right one for the job. And understanding them is "
                        "what separates someone who writes code, from someone who writes good code.",
               ("right", lambda: [hl(p[1], 1.08) for p in picks], 0.9),
               ("understanding", grid),
               after=sweep)

        self.finish("S09_choose")

    # ============================================= 10. CLOSING THOUGHTS ====

    def closing(self):
        self.chapter("S10_closing", None, "Closing thoughts")

        box = toolbox(filled=True)
        self.fit(box)

        def shut():
            self.play(FadeIn(VGroup(box.body, box.slots)), run_time=0.7)
            self.play(FadeIn(box.lid, shift=DOWN * 0.5), run_time=0.6)
            return ring(box.body)

        scenes = []
        for k, (kind, name, sub) in enumerate((("stack", "Text editor", "Undo: a stack"),
                                               ("net", "Social network", "Find a friend: a graph"),
                                               ("hash", "Web browser", "Cache: a hash table"))):
            x = -4.4 + 4.4 * k
            scenes.append(VGroup(glyph(kind).scale(1.6).move_to(P(x, 0.7)), text(name, LABEL, INK, BOLD).move_to(P(x, -0.6)),
                                 fitted_text(sub, 4.0, SMALL, BROWN).move_to(P(x, -1.2))))

        def first():
            self.wipe()
            return FadeIn(scenes[0], shift=UP * 0.2)

        last = VGroup(text("Data Structures", TITLE, INK, BOLD),
                      Line(LEFT * 2.2, RIGHT * 2.2, stroke_color=BLUE, stroke_width=4),
                      text("The invisible architecture of software", BODY, BROWN)).arrange(DOWN, buff=0.4)
        self.fit(last, top=TOP)

        def final():
            self.wipe(everything=True)
            return [FadeIn(last[0], shift=UP * 0.2), Create(last[1])]

        self.N("s10_01", "Data structures are the vocabulary of efficient programming. They shape how we think about "
                         "problems, how we design algorithms, and how we build systems that scale.",
               ("vocabulary", lambda: LaggedStart(*[FadeIn(i, shift=UP * 0.2) for i in box.items], lag_ratio=0.15,
                                                  run_time=1.6)),
               ("problems", lambda: [hl(i, 1.08) for i in box.items[:3]], 0.8),
               ("algorithms", lambda: [hl(i, 1.08) for i in box.items[3:5]], 0.8),
               ("systems", lambda: [hl(i, 1.08) for i in box.items[5:]], 0.8))
        self.N("s10_02", "The next time you hit undo, search for a friend, or load a webpage, take a moment to "
                         "appreciate the invisible architecture at work.",
               (None, shut, 0.8),
               ("undo", first, 0.6),
               ("friend", lambda: FadeIn(scenes[1], shift=UP * 0.2), 0.6),
               ("webpage", lambda: FadeIn(scenes[2], shift=UP * 0.2), 0.6),
               ("invisible", lambda: [hl(s[2], 1.06) for s in scenes], 0.9))
        self.N("s10_03", "Because behind every smooth digital experience, there is a data structure doing the heavy "
                         "lifting.",
               ("behind", final, 1.0),
               ("heavy", lambda: FadeIn(last[2], shift=UP * 0.15), 0.8))

        # the end
        if self.mobjects:
            self.play(FadeOut(Group(*self.mobjects)), run_time=1.2)
        self.scene_end("S10_closing")
