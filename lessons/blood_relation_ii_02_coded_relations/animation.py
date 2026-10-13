"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Logical Reasoning
Video  : Lesson 11 - Blood Relation II - 02 - Coded Relations

Source script:
  C:\\Scripts\\Section A\\New folder\\Lesson 11 - Blood Relation II\\02 - Coded Relations.pdf

Built on the pattern of machine_language_animation.py (golden reference):
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per script section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``, layouts
    stacked with next_to and guarded with ``no_overlap`` and the validator.

Three roles, three voices (the script has no speaker labels; lines were assigned by meaning):
  NARRATOR  sets the scene, connects sections, reads the summary and the quiz.
  TEACHER   teaches, asks, corrects (drawn top left).
  STUDENT   answers, doubts, voices the wrong instinct of each trap (drawn top right).
No role name is ever spoken.  ``self.speaker(...)`` before each narration lights the ring of the
character who is talking and sets the expression.

Lesson 11, Video 1 of 4 (file 02 in its folder).
First video of the lesson: a silent breadcrumb, the lesson announcement, a recap of Lesson 10, then today's topic.
The narration follows the script section by section and ends with the Section Quiz and its answer key.
Every coded expression in the script was decoded again in the data block and the relation read off the family;
all answers are correct.  In the PDF the quiz answer key is printed with its columns out of line; here each row
carries its own answer (key: 1 b, 2 a, 3 c, 4 b, 5 d).
Pauses: 3 seconds on the hook, 10 on the checkpoint, 12 on each practice and quiz screen.
Teaching review, 2026-10-09 (narration departs from the script here): quiz 1 uses T, not U ("U" is heard as "you");
parent and child codes are named when first used; step six says aloud that a code plus is not a tree plus, and step
seven gets its example; the teacher confirms every answer the student gives and poses the exam patterns the student
solves; quiz answers are spoken as "option B" with the word first.
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
CELL = "#1B2440"

TERM = INK             # series terms
DIFF = "#4FC3F7"       # first differences
SECOND = "#4FC3F7"     # second differences / pattern of the differences
RATIO = "#4FC3F7"      # ratios (the next topic's tool)
FOCUS = "#FFD54F"      # "look here" / predicted value
GOOD = "#66BB6A"       # confirmed answer
BAD = "#EF5350"        # wrong / trap

FONT = "Segoe UI"
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
TOP_Y = FRAME_H / 2 - SAFE - 0.9              # first row under the top edge
BOTTOM_Y = -FRAME_H / 2 + SAFE + 0.45         # caption / tracker row

CARD_TOP = FRAME_H / 2 - SAFE - 0.2           # top edge of a question card


# ======================================================= text helpers ====

SHORT_WORDS = {"a", "an", "as", "at", "be", "by", "do", "he", "if", "in", "is", "it", "no", "of", "on", "or", "so", "to", "up", "we"}


def cap_first(s):
    """Start on-screen text with a capital letter when it starts with a word (not a variable, unit or number)."""
    start = 0
    while start < len(s) and s[start] in "“\"'(":
        start += 1
    words = s[start:].split()
    if not words:
        return s
    first = words[0].rstrip(".,;:?!”’")
    plain = first.replace("'", "").replace("’", "").replace("-", "")
    if not (plain.isalpha() and plain.islower()):
        return s
    if len(plain) == 1:
        follower = words[1].rstrip(".,;:?!") if len(words) > 1 else ""
        if not (plain == "a" and len(follower) >= 2 and follower.replace("-", "").isalpha()):
            return s
    elif len(plain) == 2 and plain not in SHORT_WORDS:
        return s
    return s[:start] + s[start].upper() + s[start + 1:]

def text(s, size=BODY, color=INK, weight=NORMAL, t2c=None):
    return Text(cap_first(s), font=FONT, font_size=size, color=color, weight=weight, t2c=t2c or {})


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


def pill(label, color=FOCUS, size=SMALL, fill_opacity=0.14):
    """Short keyword tag. The box is sized from the text, so text cannot escape."""
    t = text(label, size, color, BOLD)
    box = RoundedRectangle(corner_radius=(t.height + 0.26) / 2, width=t.width + 0.5, height=t.height + 0.26,
                           stroke_color=color, stroke_width=2, fill_color=color, fill_opacity=fill_opacity)
    t.move_to(box)
    return VGroup(box, t)



# ================================================== vocabulary helpers ====

WORD = "#4FC3F7"          # the question word
OPTION = INK              # option text
TRAP = BAD                # eliminated options
KEY = GOOD                # the answer
STEP_COLS = {"READ": "#4FC3F7", "PREDICT": "#CE93D8", "ELIMINATE": "#EF5350", "CONFIRM": "#66BB6A"}


def process_strip(size=LABEL):
    """READ → PREDICT → ELIMINATE → CONFIRM as four chips."""
    parts = []
    for i, (name, col) in enumerate(STEP_COLS.items()):
        if i:
            parts.append(text("→", size, MUTED))
        parts.append(pill(name, col, size=size))
    return VGroup(*parts).arrange(RIGHT, buff=0.2)


def step_chip(strip, name):
    """The chip for one step inside a process strip."""
    return strip[2 * list(STEP_COLS).index(name)]


class OptionQuestion:
    """WORD: (a) … (b) … (c) … (d) …, with elimination and confirmation effects.
    ``key`` is the letter of the answer; ``traps`` maps letters to the reason
    each wrong option is removed."""

    def __init__(self, word, options, key, traps, width=6.0, word_size=TITLE):
        assert key in "abcd"[:len(options)] and set(traps) | {key} == set("abcd"[:len(options)])
        self.key, self.traps = key, traps
        self.word = pill(word, WORD, size=word_size)
        self.rows = VGroup(*[VGroup(text(f"({l})", LABEL, MUTED), fitted_text(o, width - 1.0, BODY, OPTION))
                             .arrange(RIGHT, buff=0.25) for l, o in zip("abcd", options)])
        self.rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        self.group = VGroup(self.word, self.rows).arrange(DOWN, buff=0.45, aligned_edge=LEFT)

    def row(self, letter):
        return self.rows["abcd".index(letter)]

    def strike(self, letter, reason_color=TRAP):
        """Animations: strike through a wrong option, dim it, and tag the reason."""
        r = self.row(letter)
        line = Line(r.get_left() + LEFT * 0.05, r.get_right() + RIGHT * 0.05, color=TRAP, stroke_width=3)
        tag = pill(self.traps[letter], reason_color, size=SMALL).next_to(r, RIGHT, buff=0.35)
        return VGroup(line, tag), [Create(line), r.animate.set_opacity(0.4), FadeIn(tag, shift=LEFT * 0.1)]

    def confirm(self):
        r = self.row(self.key)
        box = SurroundingRectangle(r, color=KEY, buff=0.12, corner_radius=0.1)
        return box, [Create(box), r[1].animate.set_color(KEY)]


def meaning_circles(words, centres, radii, colors, label_size=LABEL):
    """Each word's meaning as a translucent circle with its label inside."""
    out = VGroup()
    for w, c, r, col in zip(words, centres, radii, colors):
        circ = Circle(radius=r, color=col, stroke_width=3, fill_color=col, fill_opacity=0.15).move_to(c)
        out.add(VGroup(circ, text(w, label_size, col, BOLD).move_to(c)))
    return out


def pair_chip(a, b, color, note=None, size=LABEL):
    """'a ≈ b' chip, optionally with a small note underneath."""
    chip = pill(f"{a}  ≈  {b}", color, size=size)
    if note:
        return VGroup(chip, text(note, SMALL, MUTED)).arrange(DOWN, buff=0.12)
    return chip


# ============================================================ the cast ====
# Three roles, three voices.  No role name is ever spoken: the lit ring on a
# drawn character shows who is talking (teacher top left, student top right);
# while the narrator speaks, both characters listen.

NARRATOR_VOICE = "vijay"
TEACHER_VOICE = "aditya"
STUDENT_VOICE = "kavya"
TURN_PAUSE = 0.6               # silence when the speaker changes (seconds), so voices never run together

SKIN = "#F2D0B0"               # characters use neutral tones, not the text colours
HAIR = "#2A2F3C"
LIPS = "#3A1F1F"
SHIRT_T = "#2E5E86"
SHIRT_S = "#8A6D1F"
RING_ON = "#FFD54F"


class Face(VGroup):
    """A drawn character: head, hair, eyes, brows, mouth and shoulders.

    ``look(name)`` sets the expression at once; ``look_to(name)`` returns the
    animations for a change on screen; ``talk(on)`` lights the speaking ring."""

    LOOKS = {"neutral": ("soft", "flat"), "smile": ("smile", "flat"), "happy": ("open", "up"),
             "ask": ("small", "one_up"), "think": ("flat", "down"), "confused": ("wavy", "tilt"),
             "surprised": ("o", "up"), "oops": ("frown", "tilt")}

    def __init__(self, r=0.34, kind="teacher", look="neutral"):
        super().__init__()
        self.r, self.kind = r, kind
        shirt = SHIRT_T if kind == "teacher" else SHIRT_S
        self.head = Circle(radius=r, stroke_color="#B89A7C", stroke_width=2, fill_color=SKIN, fill_opacity=1)
        self.body = Arc(radius=r * 1.3, start_angle=0, angle=PI, stroke_color=shirt, stroke_width=2,
                        fill_color=shirt, fill_opacity=1)
        self.body.next_to(self.head, DOWN, buff=-r * 0.3)
        self.ring = Circle(radius=r * 1.2, stroke_color=MUTED, stroke_width=3)
        hair = Arc(radius=r, start_angle=PI * 0.1, angle=PI * 0.8, stroke_width=0, fill_color=HAIR, fill_opacity=1)
        extras = VGroup(hair)
        if kind == "teacher":           # short hair and glasses
            for sx in (-1, 1):
                extras.add(Circle(radius=r * 0.2, stroke_color=HAIR, stroke_width=2).move_to(self.at(sx * 0.34, 0.06)))
            extras.add(Line(self.at(-0.14, 0.06), self.at(0.14, 0.06), stroke_color=HAIR, stroke_width=2))
        else:                           # a ponytail
            extras.add(Ellipse(width=r * 0.5, height=r * 0.95, stroke_width=0, fill_color=HAIR,
                               fill_opacity=1).move_to(self.at(0.95, 0.35)))
        self.eyes = VGroup(*[Dot(self.at(sx * 0.34, 0.06), radius=r * 0.085, color=HAIR) for sx in (-1, 1)])
        self.mouth = self._mouth("soft")
        self.brow_l, self.brow_r = self._brows("flat")
        self.add(self.body, self.ring, self.head, extras, self.eyes, self.brow_l, self.brow_r, self.mouth)
        self.look(look)

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

    def look(self, name):
        mouth, brows = self.LOOKS[name]
        left, right = self._brows(brows)
        self.mouth.become(self._mouth(mouth))
        self.brow_l.become(left)
        self.brow_r.become(right)
        self.now = name
        return self

    def look_to(self, name):
        if getattr(self, "now", None) == name:
            return []
        mouth, brows = self.LOOKS[name]
        left, right = self._brows(brows)
        self.now = name
        return [self.mouth.animate.become(self._mouth(mouth)), self.brow_l.animate.become(left),
                self.brow_r.animate.become(right)]

    def talk(self, on):
        return self.ring.animate.set_stroke(RING_ON if on else MUTED, width=6 if on else 3)

# ============================================================= lesson ====

class Family:
    """A family used to check the answers: genders, sibling groups, parents and marriages.

    Exam conventions are built in: brothers and sisters share both parents, and a married
    person's child is also the spouse's child (no step-relations)."""

    WORDS = {"spouse": ("husband", "wife"), "parent": ("father", "mother"), "child": ("son", "daughter"),
             "sibling": ("brother", "sister"), "grandparent": ("grandfather", "grandmother"),
             "grandchild": ("grandson", "granddaughter"), "uncle_aunt": ("uncle", "aunt"),
             "nephew_niece": ("nephew", "niece"), "cousin": ("cousin", "cousin"),
             "child_in_law": ("son-in-law", "daughter-in-law"), "parent_in_law": ("father-in-law", "mother-in-law"),
             "sibling_in_law": ("brother-in-law", "sister-in-law")}

    def __init__(self, facts=""):
        self.sex, self.group, self.parents, self.spouse = {}, {}, {}, {}
        self.tell(facts)

    def add(self, name, sex=None):
        if name not in self.group:
            self.group[name], self.parents[name], self.sex[name] = name, set(), None
        if sex:
            assert self.sex[name] in (None, sex), f"{name} cannot be both genders"
            self.sex[name] = sex
        return name

    def find(self, name):
        while self.group[name] != name:
            name = self.group[name]
        return name

    def merge(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.group[b] = a
            self.parents[a] |= self.parents.pop(b)

    def kids_group(self, parent):
        for root, people in self.parents.items():
            if parent in people:
                return root
        return None

    def siblings(self, a, b, sex=None):
        self.add(a, sex)
        self.add(b)
        self.merge(a, b)

    def child(self, kid, parent, sex=None):
        self.add(kid, sex)
        self.add(parent)
        for p in (parent, self.spouse.get(parent)):
            root = self.kids_group(p) if p else None
            if root is not None:
                self.merge(root, kid)
        root = self.find(kid)
        self.parents[root].add(parent)
        if parent in self.spouse:
            self.parents[root].add(self.spouse[parent])

    def couple(self, husband, wife):
        self.add(husband, "m")
        self.add(wife, "f")
        self.spouse[husband], self.spouse[wife] = wife, husband
        roots = [r for r in (self.kids_group(husband), self.kids_group(wife)) if r is not None]
        if len(roots) == 2:
            self.merge(roots[0], roots[1])
        if roots:
            self.parents[self.find(roots[0])] |= {husband, wife}

    def tell(self, facts):
        """Facts as 'X rel Y' ("X is the rel of Y"), separated by semicolons."""
        for fact in filter(None, (f.strip() for f in facts.split(";"))):
            x, rel, y = fact.split()
            if rel in ("father", "mother"):
                self.child(y, x)
                self.add(x, "m" if rel == "father" else "f")
            elif rel in ("son", "daughter", "child"):
                self.child(x, y, {"son": "m", "daughter": "f"}.get(rel))
            elif rel in ("brother", "sister", "sibling"):
                self.siblings(x, y, {"brother": "m", "sister": "f"}.get(rel))
            elif rel == "husband":
                self.couple(x, y)
            elif rel == "wife":
                self.couple(y, x)
            elif rel in ("male", "female"):
                self.add(x, rel[0])
            else:
                raise ValueError(fact)
        return self

    def par(self, x):
        return set(self.parents[self.find(x)])

    def sib(self, x):
        root = self.find(x)
        return {p for p in self.group if p != x and self.find(p) == root}

    def kids(self, x):
        return {p for p in self.group if x in self.parents[self.find(p)]}

    def wed(self, x):
        return {self.spouse[x]} if x in self.spouse else set()

    @staticmethod
    def over(step, people):
        out = set()
        for p in people:
            out |= step(p)
        return out

    def kind(self, x, y):
        """What X is to Y, without the gender (None if the facts do not link them)."""
        over, par, sib, kids, wed = self.over, self.par, self.sib, self.kids, self.wed
        parent_sibs = over(sib, par(y))
        tests = [("spouse", wed(y)), ("parent", par(y)), ("child", kids(y)), ("sibling", sib(y)),
                 ("grandparent", over(par, par(y))), ("grandchild", over(kids, kids(y))),
                 ("uncle_aunt", parent_sibs | over(wed, parent_sibs)),
                 ("nephew_niece", over(kids, sib(y)) | over(kids, over(sib, wed(y)))),
                 ("cousin", over(kids, parent_sibs)), ("child_in_law", over(wed, kids(y))),
                 ("parent_in_law", over(par, wed(y))), ("sibling_in_law", over(sib, wed(y)) | over(wed, sib(y)))]
        for name, people in tests:
            if x in people:
                return name
        return None

    def word(self, x, y):
        """The standard word for "X is Y's ___" (None when it cannot be determined)."""
        kind = self.kind(x, y)
        if kind is None:
            return None
        if kind == "cousin":
            return "cousin"
        return None if self.sex[x] is None else self.WORDS[kind]["mf".index(self.sex[x])]

    def side(self, x, y):
        """"paternal" or "maternal": the parent of Y through whom X is related."""
        for p in self.par(y):
            if x in self.par(p) | self.sib(p) | self.over(self.wed, self.sib(p)) | self.over(self.kids, self.sib(p)):
                return "paternal" if self.sex[p] == "m" else "maternal"
        return None

    def gap(self, x, y):
        """Rows from Y up to X (+1 = X is one generation above Y)."""
        return {"spouse": 0, "sibling": 0, "cousin": 0, "sibling_in_law": 0, "parent": 1, "uncle_aunt": 1, "parent_in_law": 1,
                "child": -1, "nephew_niece": -1, "child_in_law": -1, "grandparent": 2, "grandchild": -2}[self.kind(x, y)]


def rel(facts, x, y):
    """Shortcut: the word for "X is Y's ___" in the family described by ``facts``."""
    return Family(facts).word(x, y)

CODES = {"+": "brother", "−": "sister", "×": "father", "÷": "mother", "@": "son", "#": "daughter", "$": "husband", "%": "wife"}


def decode(expression):
    """'P × Q + R' -> the family it describes (each symbol joins its two neighbours only)."""
    parts = expression.split()
    return Family("; ".join(f"{parts[i]} {CODES[parts[i + 1]]} {parts[i + 2]}" for i in range(0, len(parts) - 2, 2)))


def coded(expression, x, y):
    return decode(expression).word(x, y)


def sided(expression, x, y):
    fam = decode(expression)
    return f"{fam.side(x, y)} {fam.word(x, y)}"


# ---- hook, second example, traps, checkpoint ----
assert sided("P × Q + R ÷ S", "P", "S") == "maternal grandfather"
assert sided("M − N × O + T", "M", "T") == "paternal aunt" and coded("M − N × O + T", "T", "M") is None
assert coded("K ÷ L + M", "M", "K") is None and coded("K ÷ L + M", "K", "M") == "mother"
assert sided("A ÷ B − C × D", "A", "D") == "paternal grandmother"
# ---- exam patterns ----
assert sided("X × Y ÷ Z", "X", "Z") == "maternal grandfather" and sided("X + Y ÷ Z", "X", "Z") == "maternal uncle"
assert sided("X − Y × Z", "X", "Z") == "paternal aunt" and coded("X ÷ Y − Z", "X", "Z") == "mother"
assert coded("X ÷ Y + Z", "Z", "X") is None and coded("X $ Y # Z", "X", "Z") == "son-in-law"
# ---- practice ----
assert coded("P × Q + R", "P", "R") == "father" and sided("A − B ÷ C", "A", "C") == "maternal aunt"
assert sided("K + L × M", "K", "M") == "paternal uncle" and sided("D ÷ E + F × G", "D", "G") == "paternal grandmother"
assert coded("H × J − K + L", "L", "H") is None
assert [decode("R − S × T").sex[p] for p in "RST"] == ["f", "m", None]
assert coded("A @ B $ C # D", "A", "D") == "grandson" and coded("M % N @ O # P", "M", "O") == "daughter-in-law"
# ---- section quiz ----
assert coded("T ÷ V + W", "T", "W") == "mother" and sided("P + Q − R × S", "P", "S") == "paternal uncle"
assert coded("L × M ÷ N − O", "O", "L") is None and decode("L × M ÷ N − O").kind("O", "L") == "grandchild"
assert [decode("E + F ÷ G − H").sex[p] for p in "EFGH"] == ["m", "f", "f", None]
assert coded("J @ K $ L # M", "J", "M") == "grandson"

OBJECTIVES = [("Decode expressions of two to four symbols", "into family links"),
              ("Find how the first person is related to the last", "or the reverse"),
              ("Say exactly whose gender the codes fix", "and when the answer cannot be determined")]
STEPS_A = [("Write the code table first", "codes change from question to question"),
           ("Each symbol joins only its two neighbours", "P × Q + R ÷ S  is  P × Q,   Q + R,   R ÷ S"),
           ("Draw each link as you decode it", "parent:  next person one row lower;   child:  one row higher;   sibling or spouse:  same row")]
STEPS_B = [("Gender comes from the person the code describes", "in A + B, A is male;  B is unknown.  Husband and wife codes fix both"),
           ("Read the relation from the first-named person", "“P to S” and “S to P” can have different answers"),
           ("Code symbols are not tree marks", "decode into words first, then draw with + and − for male and female"),
           ("No step relations", "if X is the wife of Y and Z is Y's son, X is Z's mother")]
FORMULAS = ["Code table first;   each symbol joins its two neighbours only",
            "Parent code → next person one row lower;   child code → one row higher",
            "Sibling or spouse code → same row",
            "Gender:   only for the person a code describes   (both partners for husband / wife)",
            "“How is X related to Y?”  →  the answer word describes X"]
PATTERNS_A = [["X × Y ÷ Z", "X to Z", "Father of Z's mother", "Maternal grandfather"],
              ["X + Y ÷ Z", "X to Z", "Brother of Z's mother", "Maternal uncle"],
              ["X − Y × Z", "X to Z", "Sister of Z's father", "Paternal aunt"]]
PATTERNS_B = [["X ÷ Y − Z", "X to Z", "Mother of Z's sister", "Mother"],
              ["X ÷ Y + Z", "Z to X", "Child of X;  Z's gender unknown", "Cannot be determined"],
              ["X $ Y # Z", "X to Z", "Husband of Z's daughter", "Son-in-law"]]
TRAPS = [("Trap 1  ·  giving the right-hand person a gender", "K ÷ L + M.   How is M related to K?",
          "“+ means brother, so M is K's son”", "“Brother” describes L, not M:  cannot be determined",
          "A code fixes the gender of the person on its left"),
         ("Trap 2  ·  answering in the wrong direction", "K ÷ L + M.   How is K related to M?",
          "“M is a son or daughter:  cannot be determined”", "K is the mother of L and of L's sibling M:  mother",
          "The answer word describes the first-named person;  check whose gender it needs")]
PRACTICE_A = [("L1", "P × Q + R.   How is P related to R?"), ("L1", "A − B ÷ C.   How is A related to C?"),
              ("L1", "K + L × M.   How is K related to M?"), ("L2", "D ÷ E + F × G.   How is D related to G?"),
              ("L2", "H × J − K + L.   How is L related to H?"), ("L2", "In R − S × T, whose genders are definitely known?")]
PRACTICE_B = [("L3", "@ son of,  # daughter of,  $ husband of,  % wife of.     A @ B $ C # D.   How is A related to D?"),
              ("L3", "Same codes.     M % N @ O # P.   How is M related to O?")]
ANSWERS_A = [("P is Q's father, and Q is R's brother", "Father"), ("A is the sister of C's mother B", "Maternal aunt"),
             ("K is the brother of M's father L", "Paternal uncle"), ("D is the mother of E and F, and F is G's father", "Paternal grandmother")]
ANSWERS_B = [("L is H's child, but no code describes L", "Cannot be determined"), ("T appears only on the right", "R female,  S male"),
             ("A is the son of C, and C is D's daughter", "Grandson"), ("M is the wife of N, and N is O's son", "Daughter-in-law")]
LENS = [("Recognition cue", "symbols such as +, −, ×, ÷ or @, #, $, % defined as relations, then an expression of letters and symbols"),
        ("Target time", "30 seconds, including writing the code table"),
        ("Sanity check", "the answer word's gender must match a code that describes that person")]
QUIZ = [["T ÷ V + W.   How is T related to W?", "(a) Grandmother\n(b) Mother\n(c) Sister\n(d) Aunt"],
        ["P + Q − R × S.   How is P related to S?", "(a) Paternal uncle\n(b) Maternal uncle\n(c) Father\n(d) Grandfather"],
        ["L × M ÷ N − O.   How is O related to L?", "(a) Grandson\n(b) Granddaughter\n(c) Cannot be determined\n(d) Son"],
        ["In E + F ÷ G − H, whose genders are definitely known?", "(a) E and F only\n(b) E, F and G\n(c) E, F, G and H\n(d) F and G only"],
        ["@ son,  # daughter,  $ husband:   J @ K $ L # M.   J to M?",
         "(a) Son\n(b) Son-in-law\n(c) Nephew\n(d) Grandson"]]
QUIZ_KEY = [("T is V's mother;  V and W are siblings", "(b)"), ("P, Q and R are siblings;  R is S's father", "(a)"),
            ("O is M's child, so L's grandchild;  no code describes O", "(c)"), ("E brother, F mother, G sister;  H appears only on the right", "(b)"),
            ("J is K's son;  K is L's husband, so L is J's mother;  L is M's daughter", "(d)")]


def two_line_blocks(items, color, detail_size=SMALL):
    """Numbered blocks: a bold title line with a detail line under it.  block[0] = title line, block[1] = detail line."""
    blocks = VGroup()
    for i, (title, detail) in enumerate(items):
        top = VGroup(pill(str(i + 1), color, size=SMALL), text(title, LABEL, color, BOLD)).arrange(RIGHT, buff=0.3)
        indent = Rectangle(width=0.75, height=0.1).set_stroke(width=0)                    # never shown
        blocks.add(VGroup(top, VGroup(indent, text(detail, detail_size, INK)).arrange(RIGHT, buff=0))
                   .arrange(DOWN, buff=0.16, aligned_edge=LEFT))
    return blocks.arrange(DOWN, buff=0.5, aligned_edge=LEFT)


def given_chips(p, r, t):
    return VGroup(pill(f"P = {p}", "#4FC3F7", size=LABEL), pill(f"R = {r}", "#FFB74D", size=LABEL),
                  pill(f"T = {t}", "#CE93D8", size=LABEL)).arrange(RIGHT, buff=0.35)


class CodedRelationsVideo(LMSScene):
    lesson_title = "Coded Relations"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_section()
        self.concept_journey()
        self.rule_box()
        self.short_trick()
        self.analogy()
        self.hook_solved()
        self.second_example()
        self.exam_patterns()
        self.traps()
        self.checkpoint()
        self.practice()
        self.answers()
        self.exam_lens()
        self.summary()
        self.section_quiz()

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

    def caption(self, s, color=INK):
        """One-line keyword caption in a fixed-width bar at the bottom of the frame."""
        t = fitted_text(s, SAFE_W - 1.0, BODY, color)
        bar = self.card(t, width=SAFE_W - 0.4, height=t.height + 0.9)
        return bar.move_to(UP * BOTTOM_Y)

    def breadcrumb(self, *parts):
        """Silent 'where are we' trail: Module > Lesson > Topic."""
        colors = [DIFF, MUTED, RATIO]
        items = []
        for i, p in enumerate(parts):
            if i:
                items.append(text("›", LABEL, MUTED))
            items.append(pill(p, colors[i % 3], size=SMALL))
        return fit_width(VGroup(*items).arrange(RIGHT, buff=0.25), SAFE_W)

    def verdict_card(self, good, s, width):
        """A ✓ (green) or ✗ (red) card with fitted text."""
        color = GOOD if good else BAD
        body = VGroup(text("✓" if good else "✗", 34, color, BOLD),
                      fitted_text(s, width - 1.3, SMALL, color, max_lines=2)).arrange(RIGHT, buff=0.25)
        return self.card(body, width=width, height=1.2, color=color)

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

    def table_rows(self, header, rows, widths, size=SMALL):
        """A small table as a VGroup of rows (header first). Each cell is fitted
        to its column and left-aligned at the column's left edge."""
        lefts, x = [], -sum(widths) / 2
        for w in widths:
            lefts.append(x)
            x += w
        out = VGroup()
        for i, cells in enumerate([header] + rows):
            color, weight = (FOCUS, BOLD) if i == 0 else (INK, NORMAL)
            row = VGroup(*[fitted_text(c, w - 0.3, size, color, weight, max_lines=2) for c, w in zip(cells, widths)])
            for cell, left in zip(row, lefts):
                cell.set_x(left + cell.width / 2)
            out.add(row)
        out.arrange(DOWN, buff=0.3)
        for row in out:                      # arrange() recentres rows; restore column alignment
            for cell, left in zip(row, lefts):
                cell.set_x(left + cell.width / 2)
        return out

    def recap_card(self, title, rows):
        """'Recap Card': term on the left, one-line meaning on the right."""
        table = self.table_rows([title, "what it means"], rows, [3.4, 8.0], size=LABEL)
        table[0][0].set_color(INK)
        card = self.card(table, width=SAFE_W - 0.4)
        return card, table

    def no_overlap(self, *mobs, gap=0.05):
        """Layout guard: the bounding boxes of the given blocks must not intersect
        (checked before anything is played, so a layout change can't silently overlap)."""
        for i, a in enumerate(mobs):
            for b in mobs[i + 1:]:
                apart_x = a.get_right()[0] + gap <= b.get_left()[0] or b.get_right()[0] + gap <= a.get_left()[0]
                apart_y = a.get_bottom()[1] >= b.get_top()[1] + gap or b.get_bottom()[1] >= a.get_top()[1] + gap
                if not (apart_x or apart_y):
                    raise ValueError(f"overlapping blocks: {a.__class__.__name__} at {a.get_center()} and "
                                     f"{b.__class__.__name__} at {b.get_center()}")

    # ----------------------------------------------------- pinned panel --
    PIN_W = 3.4                                   # width of the pinned reference panel

    def pin(self, card, corner=UR):
        """Animation: park a reference card in a corner. It stays on screen across scenes
        (``clear_stage`` leaves it) until ``unpin``."""
        fit_within(card, self.PIN_W, SAFE_H - 1.0)
        card.to_corner(corner, buff=SAFE)
        self.pinned = card
        return FadeIn(card, shift=LEFT * 0.2)

    def unpin(self):
        card, self.pinned = getattr(self, "pinned", None), None
        return FadeOut(card) if card is not None else Wait(0.01)

    def free_area(self):
        """(centre_x, width) of the stage left free by the pinned panel (full safe width if none)."""
        card = getattr(self, "pinned", None)
        left = -FRAME_W / 2 + SAFE
        right = (card.get_left()[0] - 0.3) if card is not None else FRAME_W / 2 - SAFE
        return (left + right) / 2, right - left

    def place_free(self, mob, y=None):
        """Fit ``mob`` into the free area (beside the pinned panel) and centre it there."""
        cx, w = self.free_area()
        fit_width(mob, w)
        mob.set_x(cx)
        if y is not None:
            mob.set_y(y)
        if getattr(self, "pinned", None) is not None:
            self.no_overlap(mob, self.pinned)
        return mob

    def clear_stage(self, run_time=0.6):
        """Scene transition: fade out everything except the pinned panel."""
        keep = getattr(self, "pinned", None)
        mobs = [m for m in self.mobjects if m is not keep]
        if mobs:
            self.play(FadeOut(Group(*mobs)), run_time=run_time)

    def steps_pin(self, title, steps):
        """A compact numbered-steps card for the pinned panel. ``steps`` = [(text, colour), ...]."""
        rows = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), text(t, SMALL, INK)).arrange(RIGHT, buff=0.2)
                        for i, (t, c) in enumerate(steps)]).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        return self.card(VGroup(text(title, SMALL, MUTED, BOLD), rows).arrange(DOWN, buff=0.2, aligned_edge=LEFT),
                         color=FOCUS)

    def pin_step(self, i, color=FOCUS):
        """Animation: light up row i of the pinned steps card."""
        return Indicate(self.pinned[1][1][i], color=color, scale_factor=1.08)

    def heading(self, s, color=FOCUS):
        head = pill(s, color, size=LABEL)
        return head.move_to(UP * (CARD_TOP - head.height / 2))

    def stack(self, head, items, buff=0.45, top=0.5, align=None):
        """Stack ``items`` under ``head`` (fitted to the frame, guarded against overlap).  Returns the group."""
        body = VGroup(*items)
        if align is None:
            body.arrange(DOWN, buff=buff)
        else:
            body.arrange(DOWN, buff=buff, aligned_edge=align)
        fit_within(body, SAFE_W, SAFE_H - head.height - top - 0.3)
        body.next_to(head, DOWN, buff=top)
        self.no_overlap(head, *items)
        self.validator.check_in_frame(VGroup(head, body))
        return body

    def placed_table(self, head, header, rows, widths, size=SMALL, room=0.8):
        """A table fitted under ``head``.  Returns (table, body rows)."""
        table = self.table_rows(header, rows, widths, size=size)
        fit_within(table, SAFE_W, SAFE_H - head.height - room)
        table.next_to(head, DOWN, buff=0.45)
        self.no_overlap(head, table)
        self.no_overlap(*table)
        self.validator.check_in_frame(VGroup(head, table))
        return table, table[1:]

    def verdict_pair(self, wrong, right):
        """A ✗ card and a ✓ card of the same height, side by side."""
        contents = [VGroup(text(mark, 34, c, BOLD), text(s, LABEL, c)).arrange(RIGHT, buff=0.25)
                    for mark, s, c in [("✗", wrong, BAD), ("✓", right, GOOD)]]
        tallest = max(c.height for c in contents) + 0.6
        return VGroup(*[self.card(c, width=6.2, height=tallest, color=col) for c, col in zip(contents, (BAD, GOOD))])\
            .arrange(RIGHT, buff=0.5)

    def show_trap(self, trap):
        """Lay out one trap.  Returns (head, question, wrong card, right card, rule)."""
        title, question, wrong, right, rule = trap
        head = self.heading(title, BAD)
        q = fitted_text(question, SAFE_W - 1.0, BODY, INK, NORMAL, max_lines=2)
        pair = self.verdict_pair(wrong, right)
        rule_pill = fit_width(pill(rule, FOCUS, size=LABEL), SAFE_W)
        self.stack(head, [q, pair, rule_pill], buff=0.7, top=0.8)
        self.no_overlap(pair[0], pair[1])
        return head, q, pair[0], pair[1], rule_pill

    def solve_steps(self, steps, color=WORD):
        """Numbered solution rows.  Each row = (number chip, working, result)."""
        rows = VGroup(*[VGroup(pill(str(i + 1), color, size=SMALL), text(what, LABEL, INK), text(result, LABEL, GOOD, BOLD))
                        .arrange(RIGHT, buff=0.3) for i, (what, result) in enumerate(steps)])
        return rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)

    def pattern_table(self, head, patterns):
        table, rows = self.placed_table(head, ["Pattern", "Example", "Method", "Answer"], [list(p) for p in patterns],
                                        [2.6, 4.6, 4.2, 1.8], room=1.2)
        for row in rows:
            row[0].set_color(WORD)
            row[3].set_color(GOOD)
        return table, rows

    def practice_table(self, head, questions, first):
        table, rows = self.placed_table(head, ["Level", "Question"],
                                        [[f"{level}  ·  {first + i}", q] for i, (level, q) in enumerate(questions)],
                                        [1.6, 11.0], room=1.3)
        level_cols = {"L1": WORD, "L2": WORD, "L3": WORD}
        for row, (level, _) in zip(rows, questions):
            row[0].set_color(level_cols[level])
        return table, rows

    def answer_table(self, head, answers, first):
        table, rows = self.placed_table(head, ["#", "Reasoning", "Answer"],
                                        [[str(first + i), how, ans] for i, (how, ans) in enumerate(answers)], [0.8, 8.6, 3.6])
        for row in rows:
            row[0].set_color(MUTED)
            row[2].set_color(GOOD)
        return table, rows

    # ------------------------------------------------------------ the cast --

    def speaker(self, who, look=None):
        """Show who is speaking: "N" narrator (both characters listen), "T" teacher, "S" student.

        The two characters walk in the first time one of them speaks and stay on screen
        (``clear_stage`` leaves them); ``look`` is the speaker's expression."""
        cast = getattr(self, "cast", None)
        if cast is None:
            if who == "N":
                return
            t, s = Face(0.34, "teacher", "neutral"), Face(0.34, "student", "neutral")
            top, side = FRAME_H / 2 - SAFE, FRAME_W / 2 - SAFE
            t.shift(UP * (top - t.get_top()[1]) + RIGHT * (-side - t.get_left()[0]))
            s.shift(UP * (top - s.get_top()[1]) + RIGHT * (side - s.get_right()[0]))
            self.cast, self.teacher_face, self.student_face = VGroup(t, s), t, s
            self.cast_clear()
            self.play(FadeIn(t, shift=RIGHT * 0.4), FadeIn(s, shift=LEFT * 0.4), run_time=0.5)
        if getattr(self, "speaking", None) == (who, look):
            return
        self.speaking = (who, look)
        t, s = self.teacher_face, self.student_face
        self.cast_clear()
        self.play(*t.look_to((look or "smile") if who == "T" else "neutral"), t.talk(who == "T"),
                  *s.look_to((look or "smile") if who == "S" else "neutral"), s.talk(who == "S"), run_time=0.25)

    def cast_clear(self):
        """Layout guard: nothing on screen may reach into a character's corner."""
        own = set(self.cast.get_family())
        for face, name in ((self.teacher_face, "teacher"), (self.student_face, "student")):
            l, r, b = face.get_left()[0] - 0.08, face.get_right()[0] + 0.08, face.get_bottom()[1] - 0.08
            for top in self.mobjects:
                for part in top.family_members_with_points():
                    if part in own:
                        continue
                    if part.get_right()[0] > l and part.get_left()[0] < r and part.get_top()[1] > b:
                        raise ValueError(f"{part!r} reaches into the {name}'s corner; keep the top corners free.")

    def clear_stage(self, run_time=0.6):
        """Scene transition: fade out everything except the pinned panel and the two characters."""
        keep = set()
        for kept in (getattr(self, "pinned", None), getattr(self, "cast", None)):
            if kept is not None:
                keep.update(kept.get_family())
        mobs = [m for m in self.mobjects
                if m not in keep and any(p not in keep for p in m.family_members_with_points())]
        if mobs:
            self.play(FadeOut(Group(*mobs)), run_time=run_time)

    def curtain(self):
        """The end of the video: the characters leave with everything else."""
        self.cast = None
        if self.mobjects:
            self.play(FadeOut(Group(*self.mobjects)), run_time=1.0)

    def table_under(self, head, ref, header, rows, widths, size=SMALL):
        """A reference block under ``head`` and a table under it, fitted to the space that is left.  Returns (table, body rows)."""
        fit_width(ref, SAFE_W)
        ref.next_to(head, DOWN, buff=0.35)
        table = self.table_rows(header, rows, widths, size=size)
        fit_within(table, SAFE_W, ref.get_bottom()[1] + FRAME_H / 2 - SAFE - 1.2)
        table.next_to(ref, DOWN, buff=0.4)
        self.no_overlap(head, ref, table)
        self.no_overlap(*table)
        self.validator.check_in_frame(VGroup(head, ref, table))
        return table, table[1:]
    def step_rows(self, items, color=WORD):
        """Numbered concept steps.  Each row = (number chip, the step[, a short note in green])."""
        rows = VGroup()
        for i, (what, note) in enumerate(items):
            row = VGroup(pill(str(i + 1), color, size=SMALL), text(what, LABEL, INK, BOLD))
            if note:
                row.add(text(note, LABEL, GOOD, BOLD))
            rows.add(row.arrange(RIGHT, buff=0.35))
        return fit_width(rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT), SAFE_W - 0.6)

    def tree(self, people, couples=(), kids=(), sibs=(), dx=1.9, dy=1.25, size=LABEL):
        """A family tree in the standard notation.

        people  {name: (column, row, sign)} with sign "+", "−" or "" (gender not known); row 0 is the top row
        couples [(a, b)]            a double line (=) between a married couple
        kids    [(parents, [children])] with parents = (a, b) or (a,): a vertical line down to the children
        sibs    [(a, b)]            a horizontal line joining siblings whose parents are not drawn
        Returns a VGroup with .node[name], .wed[(a, b)], .down[i] and .sib[(a, b)] for the cues."""
        tones = {"+": WORD, "−": FOCUS, "": MUTED}
        g = VGroup()
        g.node, g.wed, g.down, g.sib = {}, {}, [], {}
        for name, (col, row, sign) in people.items():
            label = text(f"{name} ({sign})" if sign else name, size, tones[sign], BOLD)
            box = RoundedRectangle(corner_radius=0.14, width=max(label.width + 0.4, 1.0), height=0.62, stroke_color=tones[sign],
                                   stroke_width=2.5, fill_color=PANEL, fill_opacity=1)
            node = VGroup(box, label.move_to(box)).move_to(RIGHT * col * dx + DOWN * row * dy)
            g.node[name] = node
            g.add(node)
        for a, b in couples:
            left, right = sorted((g.node[a], g.node[b]), key=lambda m: m.get_x())
            mark = VGroup(*[Line(left.get_right(), right.get_left(), stroke_color=INK, stroke_width=3).shift(UP * s)
                            for s in (0.06, -0.06)])
            g.wed[(a, b)] = mark
            g.add(mark)
        for a, b in sibs:
            left, right = sorted((g.node[a], g.node[b]), key=lambda m: m.get_x())
            mark = Line(left.get_right(), right.get_left(), stroke_color=MUTED, stroke_width=3)
            g.sib[(a, b)] = mark
            g.add(mark)
        for parents, children in kids:
            key = tuple(parents)
            if len(key) == 2:
                wed = g.wed.get(key) or g.wed.get(key[::-1])
                start = wed.get_center() + DOWN * 0.06
            else:
                start = g.node[key[0]].get_bottom()
            tops = [g.node[k].get_top() for k in children]
            bar = (start[1] + max(t[1] for t in tops)) / 2
            lines = VGroup(Line(start, [start[0], bar, 0]))
            xs = [t[0] for t in tops] + [start[0]]
            if max(xs) - min(xs) > 1e-3:
                lines.add(Line([min(xs), bar, 0], [max(xs), bar, 0]))
            for t in tops:
                lines.add(Line([t[0], bar, 0], t))
            lines.set_stroke(MUTED, 3)
            g.down.append(lines)
            g.add(lines)
        return g

    def row_tags(self, tree, tags, size=SMALL):
        """Generation labels (+1, 0, −1 ...) to the left of a tree.  tags = {a person on that row: label}."""
        left = tree.get_left()[0] - 0.55
        return VGroup(*[text(label, size, MUTED, BOLD).move_to([left, tree.node[name].get_y(), 0]) for name, label in tags.items()])

    def lines_block(self, items, color=None, size=LABEL):
        """Left-aligned lines of text.  items = strings, or (string, colour)."""
        rows = VGroup()
        for item in items:
            s, c = (item, color or INK) if isinstance(item, str) else item
            rows.add(text(s, size, c, BOLD))
        return rows.arrange(DOWN, buff=0.32, aligned_edge=LEFT)

    def steps_list(self, items, color=None):
        """Numbered steps: (step text, result in green or None)."""
        rows = VGroup()
        for i, (what, result) in enumerate(items):
            row = VGroup(pill(str(i + 1), color or WORD, size=SMALL), text(what, SMALL, INK, BOLD))
            if result:
                row.add(text(result, SMALL, GOOD, BOLD))
            rows.add(row.arrange(RIGHT, buff=0.3))
        return rows.arrange(DOWN, buff=0.36, aligned_edge=LEFT)

    def legend(self, size=SMALL):
        """The code table of this video."""
        return VGroup(*[pill(s, MUTED, size=size) for s in ("+  brother of", "−  sister of", "×  father of", "÷  mother of")]).arrange(RIGHT, buff=0.3)

    def links(self, parts, color=None):
        """An expression split into its links."""
        return VGroup(*[pill(p, color or WORD, size=LABEL) for p in parts]).arrange(RIGHT, buff=0.5)

    # ============================================== 0. INTRO ==========
    # First video of the lesson: silent breadcrumb, the lesson announcement, a recap of the previous lesson, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Logical Reasoning", "Lesson 11 · Blood Relation II", "Video 1 of 4")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        lesson = pill("Lesson 11  ·  Blood Relation II", RATIO, size=LABEL)
        recap = VGroup(text("From Lesson 10  ·  Blood Relation I", SMALL, MUTED),
                       fit_width(VGroup(pill("Draw each link;  walk from Y to X", WORD, size=LABEL), pill("A gender only when a word fixes it", GOOD, size=LABEL)).arrange(RIGHT, buff=0.4), SAFE_W - 0.6)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Coded Relations", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("Today: symbols that stand for family links", LABEL, FOCUS)
        block = VGroup(lesson, recap, title, today).arrange(DOWN, buff=0.55)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.6)
        self.no_overlap(crumb, lesson, recap, title, today)
        self.no_overlap(*recap[1])
        self.validator.check_in_frame(VGroup(crumb, block))

        self.speaker("N")
        n = self.narrate(
            id="intro_01",
            text="Now we start lesson eleven: blood relations, part two.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "eleven")
        self.play(FadeIn(lesson, scale=1.03))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="intro_02",
            text="In lesson ten you learned to draw each link on a tree, walk from the second person to the first, and fix "
                 "a gender only when a word fixes it.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.at_word(n, "draw")
        self.play(FadeIn(recap[0]), FadeIn(recap[1][0], shift=UP * 0.1))
        self.at_word(n, "gender")
        self.play(FadeIn(recap[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="intro_03",
            text="This first video covers coded relations: symbols that stand for family links.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "covers")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "symbols")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("The caterer's shorthand")
        codes = self.legend()
        card = pill("Table 4:     P × Q + R ÷ S", FOCUS, size=BODY)
        ask = text("How is P related to S?", LABEL, INK, BOLD)
        split = self.links(["P × Q", "Q + R", "R ÷ S"])
        self.stack(head, [codes, card, ask, split], buff=0.7, top=0.9)
        self.no_overlap(*codes)

        self.speaker("N")
        n = self.narrate(
            id="hook_01",
            text="A wedding caterer writes family links in shorthand. Plus means brother of. Minus means sister of. Times "
                 "means father of. Divided by means mother of.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "shorthand")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Plus")
        self.play(FadeIn(codes[0], shift=RIGHT * 0.2))
        self.at_word(n, "Minus")
        self.play(FadeIn(codes[1], shift=RIGHT * 0.2))
        self.at_word(n, "Times")
        self.play(FadeIn(codes[2], shift=RIGHT * 0.2))
        self.at_word(n, "Divided")
        self.play(FadeIn(codes[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "ask")
        n = self.narrate(
            id="hook_02",
            text="The card for table four reads: P times Q plus R divided by S. How is P related to S?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "card")
        self.play(FadeIn(card, scale=1.03))
        self.at_word(n, "related")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.speaker("S", "confused")
        n = self.narrate(
            id="hook_03",
            text="It looks like algebra!",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "algebra")
        self.play(Indicate(card, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("T", "smile")
        n = self.narrate(
            id="hook_04",
            text="Read as a sentence, yes. Read one symbol at a time, it is three short links in a family tree. By the end "
                 "of this video you will answer it in under half a minute.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "three")
        self.play(FadeIn(split[0], shift=RIGHT * 0.2), FadeIn(split[1], shift=RIGHT * 0.2), FadeIn(split[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. OBJECTIVES ==========

    def objectives(self):
        self.scene_start("S02_objectives", title="Objectives")

        head = self.heading("By the end of this video")
        blocks = two_line_blocks(OBJECTIVES, WORD)
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        self.speaker("N")
        n = self.narrate(
            id="objectives_01",
            text="By the end of this video, you will be able to do three things.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="objectives_02",
            text="One: decode expressions of two to four symbols into family links.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.at_word(n, "decode")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "links")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="objectives_03",
            text="Two: find how the first person is related to the last, or the reverse.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.at_word(n, "find")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "reverse")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="objectives_04",
            text="Three: say exactly whose gender the codes fix, and when the answer cannot be determined.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "gender")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "cannot")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS SECTION ==========

    def why_this_section(self):
        self.scene_start("S03_why_this_section", title="Why This Section")

        head = self.heading("Why this section")
        common = pill("Coded relations are the most common blood-relation format", WORD, size=LABEL)
        punish = pill("They punish anyone who decodes loosely or invents a gender", BAD, size=LABEL)
        self.stack(head, [common, punish], buff=1.1, top=1.4)

        self.speaker("T")
        n = self.narrate(
            id="why_this_section_01",
            text="Coded relations are the most common blood relation format in aptitude papers.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "common")
        self.play(FadeIn(common, scale=1.03))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="why_this_section_02",
            text="They test nothing beyond the links of lesson ten, but they punish anyone who decodes loosely or invents "
                 "a gender.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "punish")
        self.play(FadeIn(punish, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_section")

    # ============================================== 4. THE CONCEPT JOURNEY ==========

    def concept_journey(self):
        self.scene_start("S04_concept_journey", title="The Concept Journey")

        head = self.heading("Steps 1 to 3  ·  Table, links, rows")
        blocks = two_line_blocks(STEPS_A, WORD)
        self.stack(head, list(blocks), buff=0.55, top=0.8, align=LEFT)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_01",
            text="Step one: write the code table first. Codes change from question to question, so copy the meanings once, "
                 "beside the question, before you read any expression.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "table")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03), FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "change")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "ask")
        n = self.narrate(
            id="concept_journey_02",
            text="Step two: each symbol joins only its two neighbours. So how many statements are in our expression?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "neighbours")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "statements")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="concept_journey_03",
            text="Three. P times Q, Q plus R, and R divided by S. And P is never linked directly to R.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Three")
        self.play(Indicate(blocks[1][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_04",
            text="Step three: draw each link as you decode it. A parent code, father of or mother of, puts the next person "
                 "one row lower. A child code, son of or daughter of, puts them one row higher. A sibling or spouse code "
                 "keeps the same row.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "draw")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "lower")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 4 to 7  ·  Gender, direction, marks")
        blocks = two_line_blocks(STEPS_B, WORD)
        self.stack(head, list(blocks), buff=0.45, top=0.7, align=LEFT)

        self.speaker("T", "ask")
        n = self.narrate(
            id="concept_journey_05",
            text="Step four: gender comes from the person the code describes. In A plus B, brother describes A, so A is "
                 "male. What about B?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "gender")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03), FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "describes")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="concept_journey_06",
            text="Unknown. Nothing describes B.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Unknown")
        self.play(Indicate(blocks[0][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_07",
            text="Right. Only a husband or wife code fixes both partners: a husband's partner is female, and a wife's "
                 "partner is male. Step five: read the relation from the first-named person. P to S, and S to P, can "
                 "have different answers.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "first-named")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "different")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_08",
            text="Step six: code symbols are not tree marks. In the code, plus may mean brother of. On your tree, plus "
                 "still means male. So decode into words first, then draw.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "marks")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2), FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_08b",
            text="Step seven: no step relations. If X is the wife of Y, and Z is Y's son, then X is Z's mother.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "seven")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2), FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_concept_journey")

    # ============================================== 5. RULE BOX ==========

    def rule_box(self):
        self.scene_start("S05_rule_box", title="Rule Box")

        head = self.heading("Rule box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_width(lines, SAFE_W - 1.6)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        self.speaker("T")
        n = self.narrate(
            id="rule_box_01",
            text="Here is the rule box. Code table first, and each symbol joins its two neighbours only.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "table")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="rule_box_02",
            text="A parent code puts the next person one row lower; a child code, one row higher.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "lower")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="rule_box_03",
            text="A sibling or spouse code keeps the same row.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "same")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="rule_box_04",
            text="Gender only for the person a code describes.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "Gender")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="rule_box_05",
            text="And the answer word describes the first-named person.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "answer")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_rule_box")

    # ============================================== 6. SHORT TRICK ==========

    def short_trick(self):
        self.scene_start("S06_short_trick", title="Short Trick")

        head = self.heading("Short trick")
        draw = pill("Draw each decoded link at once:  parent drops a row, child lifts a row, sibling and spouse keep it", WORD, size=SMALL)
        give = pill("Give a gender only from a code that describes the person, or from being a husband or wife", FOCUS, size=SMALL)
        self.stack(head, [draw, give], buff=1.0, top=1.4)

        self.speaker("T")
        n = self.narrate(
            id="short_trick_01",
            text="The short trick. Draw each decoded link at once: parent codes drop the next person one row, child codes "
                 "lift them, sibling and spouse codes keep the row.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Draw")
        self.play(FadeIn(draw, scale=1.03))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="short_trick_02",
            text="And give a person a gender only from a code that describes them, or from being someone's husband or "
                 "wife.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "gender")
        self.play(FadeIn(give, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_short_trick")

    # ============================================== 7. THE ANALOGY ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy")

        head = self.heading("The analogy  ·  a train route with stops")
        route = VGroup(pill("P", WORD, size=BODY), Line(LEFT * 0.6, RIGHT * 0.6, color=MUTED, stroke_width=5), pill("Q", WORD, size=BODY),
                       Line(LEFT * 0.6, RIGHT * 0.6, color=MUTED, stroke_width=5), pill("R", WORD, size=BODY),
                       Line(LEFT * 0.6, RIGHT * 0.6, color=MUTED, stroke_width=5), pill("S", WORD, size=BODY)).arrange(RIGHT, buff=0.2)
        like = pill("Each symbol is one segment between two neighbouring stations;  ride them in order", WORD, size=SMALL)
        stops = pill("Where it stops:  a family link read backwards may need a gender you do not have", BAD, size=SMALL)
        self.stack(head, [route, like, stops], buff=0.7, top=1.0)

        self.speaker("T")
        n = self.narrate(
            id="analogy_01",
            text="A coded expression is a train route with stops. Each symbol is one segment between two neighbouring "
                 "stations. You ride the segments in order; you never jump from the first station to the third.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "route")
        self.play(FadeIn(route))
        self.at_word(n, "segment")
        self.play(FadeIn(like, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.speaker("S", "ask")
        n = self.narrate(
            id="analogy_02",
            text="Can I ride it backwards?",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "backwards")
        self.play(Indicate(route, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="analogy_03",
            text="A train segment is the same both ways. A family link is not. P is the father of Q, read backwards, is: Q "
                 "is the son or daughter of P. And that backward word may need a gender you do not have.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "backward")
        self.play(FadeIn(stops, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE: CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example: Closing the Hook")

        head = self.heading("Worked example  ·  P × Q + R ÷ S")
        family = self.tree({"P": (0.5, 0, "+"), "Q": (0, 1, "+"), "R": (1, 1, "−"), "S": (1, 2, "")},
                           kids=[(("P",), ["Q", "R"]), (("R",), ["S"])], dy=1.1)
        steps = self.steps_list([("P × Q:  P is Q's father", "P male, one row up"), ("Q + R:  Q is R's brother", "Same row"),
                                 ("R ÷ S:  R is S's mother", "R female"), ("The father of S's mother", "Maternal grandfather")])
        both = VGroup(family, steps).arrange(RIGHT, buff=0.9)
        self.stack(head, [both], top=0.9)
        self.no_overlap(family, steps)

        self.speaker("T", "ask")
        n = self.narrate(
            id="hook_solved_01",
            text="Back to table four. First link: P times Q.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "First")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="hook_solved_02",
            text="P is the father of Q. So P is male, one row above Q.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "father")
        self.play(FadeIn(family.node['P']), FadeIn(family.down[0][0]), FadeIn(family.down[0][2]), FadeIn(family.node['Q']), FadeIn(steps[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "ask")
        n = self.narrate(
            id="hook_solved_03",
            text="Q plus R.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "plus")
        self.play(Indicate(family.node['Q'], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="hook_solved_04",
            text="Q is the brother of R. Same row, so P is also the father of R.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "brother")
        self.play(FadeIn(family.down[0][1]), FadeIn(family.down[0][3]), FadeIn(family.node['R']), FadeIn(steps[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "ask")
        n = self.narrate(
            id="hook_solved_05",
            text="R divided by S.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "divided")
        self.play(Indicate(family.node['R'], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="hook_solved_06",
            text="R is the mother of S. So R is female, one row above S.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "mother")
        self.play(FadeIn(family.down[1]), FadeIn(family.node['S']), FadeIn(steps[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "ask")
        n = self.narrate(
            id="hook_solved_07",
            text="So P is the father of the mother of S.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "father")
        self.play(Indicate(family.node['P'], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("S", "happy")
        n = self.narrate(
            id="hook_solved_08",
            text="Maternal grandfather!",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "grandfather")
        self.play(FadeIn(steps[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "happy")
        n = self.narrate(
            id="hook_solved_09",
            text="Correct: maternal grandfather. Three symbols, three links, one word. Not algebra at all.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "grandfather")
        self.play(Indicate(steps[3], color=GOOD, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example")

        head = self.heading("When the reverse cannot be determined")
        expr = pill("M − N × O + T", FOCUS, size=BODY)
        family = self.tree({"M": (0, 0, "−"), "N": (1.2, 0, "+"), "O": (0.7, 1, "+"), "T": (1.9, 1, "")},
                           kids=[(("N",), ["O", "T"])], sibs=[("M", "N")], dy=1.1)
        steps = self.steps_list([("M is N's sister;  N is the father of O and T", "M is T's paternal aunt"),
                                 ("Reverse:  no code describes T", "Nephew or niece:  cannot be determined")])
        self.stack(head, [expr, family, steps], buff=0.5, top=0.7)

        self.speaker("T", "ask")
        n = self.narrate(
            id="second_example_01",
            text="Same codes. M minus N times O plus T. How is M related to T, and how is T related to M?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "codes")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(expr, scale=1.03))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="second_example_02",
            text="M is the sister of N, so M is female. N is the father of O, and O is the brother of T, so N is also the "
                 "father of T.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "sister")
        self.play(FadeIn(family.node['M']), FadeIn(family.sib[('M', 'N')]), FadeIn(family.node['N']))
        self.at_word(n, "father")
        self.play(FadeIn(family.down[0]), FadeIn(family.node['O']), FadeIn(family.node['T']))
        self.wait_for_narration(n)

        self.speaker("T", "ask")
        n = self.narrate(
            id="second_example_03",
            text="So M is the sister of T's father.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "sister")
        self.play(Indicate(family.node['M'], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="second_example_04",
            text="Paternal aunt.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "aunt")
        self.play(FadeIn(steps[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="second_example_05",
            text="Now the reverse. T is the child of M's brother, but no code describes T. Nephew or niece: cannot be "
                 "determined.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "reverse")
        self.play(Indicate(family.node['T'], color=FOCUS, scale_factor=1.03))
        self.at_word(n, "cannot")
        self.play(FadeIn(steps[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_second_example")

    # ============================================== 10. EXAM PATTERNS - HOW THIS IS ASKED ==========

    def exam_patterns(self):
        self.scene_start("S10_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns  ·  part 1")
        codes = self.legend()
        table, rows = self.table_under(head, codes, ["Expression", "Asked", "Decoded path", "Answer"], PATTERNS_A, [2.6, 1.8, 4.6, 4.0], size=LABEL)
        for row in rows:
            row[2].set_color(WORD)
            row[3].set_color(GOOD)

        self.speaker("T")
        n = self.narrate(
            id="exam_patterns_01",
            text="How this is asked. X times Y divided by Z: the father of Z's mother. Maternal grandfather. Your turn. "
                 "X plus Y divided by Z?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "asked")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(codes), FadeIn(table[0]))
        self.at_word(n, "father")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "turn")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="exam_patterns_02",
            text="X is the brother of Z's mother. Maternal uncle.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "brother")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="exam_patterns_03",
            text="Right. X minus Y times Z: the sister of Z's father. Paternal aunt.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "sister")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  part 2")
        codes = VGroup(self.legend(), VGroup(pill("$  husband of", MUTED, size=SMALL), pill("#  daughter of", MUTED, size=SMALL)).arrange(RIGHT, buff=0.3))\
            .arrange(DOWN, buff=0.2)
        table, rows = self.table_under(head, codes, ["Expression", "Asked", "Decoded path", "Answer"], PATTERNS_B, [2.6, 1.8, 4.6, 4.0], size=LABEL)
        for row in rows:
            row[2].set_color(WORD)
            row[3].set_color(GOOD)

        self.speaker("T")
        n = self.narrate(
            id="exam_patterns_04",
            text="X divided by Y minus Z: the mother of Z's sister. A sister's mother is your mother too, so the answer "
                 "is mother. Now be careful. X divided by Y plus Z, but they ask how Z is related to X.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(codes), FadeIn(table[0]))
        self.at_word(n, "mother")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03), FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "careful")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="exam_patterns_05",
            text="Z is a child of X, but no code describes Z, so the gender is unknown. Cannot be determined.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "child")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="exam_patterns_06",
            text="Exactly. And with new codes: X dollar Y hash Z. The husband of Z's daughter: son-in-law.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "husband")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_exam_patterns")

    # ============================================== 11. TRAPS AND CONFUSING QUESTIONS ==========

    def traps(self):
        self.scene_start("S11_traps", title="Traps and Confusing Questions")

        head, ask, wrong, right, rule = self.show_trap(TRAPS[0])

        self.speaker("T", "ask")
        n = self.narrate(
            id="traps_01",
            text="Trap one. Same codes. K divided by L plus M. How is M related to K?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "one")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "related")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="traps_02",
            text="Plus means brother, so M is the son of K.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "brother")
        self.play(FadeIn(wrong))
        self.wait_for_narration(n)

        self.speaker("T", "think")
        n = self.narrate(
            id="traps_03",
            text="Brother describes L, not M. M is a child of K, of unknown gender: cannot be determined.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "unknown")
        self.play(FadeIn(right))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="traps_04",
            text="A code fixes the gender of the person it describes, the one on its left. Only husband and wife codes "
                 "also fix the partner.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "left")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, ask, wrong, right, rule = self.show_trap(TRAPS[1])

        self.speaker("T", "ask")
        n = self.narrate(
            id="traps_05",
            text="Trap two. The same expression, the other way: how is K related to M?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "two")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "other")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="traps_06",
            text="M is a son or a daughter, so, cannot be determined.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "cannot")
        self.play(FadeIn(wrong))
        self.wait_for_narration(n)

        self.speaker("T", "think")
        n = self.narrate(
            id="traps_07",
            text="The question asks what K is to M. K is the mother of L, and of L's sibling M. Mother.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "Mother")
        self.play(FadeIn(right))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="traps_08",
            text="The answer word describes the first-named person. Check whose gender that word needs.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "describes")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        codes = self.legend()
        ask = VGroup(pill("A ÷ B − C × D", FOCUS, size=BODY), text("How is A related to D?", LABEL, INK, BOLD)).arrange(RIGHT, buff=0.6)
        family = self.tree({"A": (0.5, 0, "−"), "B": (0, 1, "−"), "C": (1, 1, "+"), "D": (1, 2, "")},
                           kids=[(("A",), ["B", "C"]), (("C",), ["D"])], dy=1.0)
        answer = pill("Paternal grandmother", GOOD, size=LABEL)
        self.stack(head, [codes, ask, family, answer], buff=0.4, top=0.6)

        self.speaker("T", "ask")
        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. A divided by B minus C times D. How is A related to D?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "turn")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03), FadeIn(codes))
        self.at_word(n, "related")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.speaker("S", "happy")
        n = self.narrate(
            id="checkpoint_02",
            text="A is the mother of B. B is the sister of C, so A is the mother of C too. C is the father of D. Paternal "
                 "grandmother.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "mother")
        self.play(FadeIn(family))
        self.at_word(n, "grandmother")
        self.play(FadeIn(answer, scale=1.03))
        self.wait_for_narration(n)

        self.speaker("T", "happy")
        n = self.narrate(
            id="checkpoint_03",
            text="Correct. And check the gender: grandmother needs A to be female, and the mother code describes A. So "
                 "the word is safe.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "gender")
        self.play(Indicate(family.node['A'], color=GOOD, scale_factor=1.03))
        self.at_word(n, "safe")
        self.play(Indicate(answer, color=GOOD, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_checkpoint")

    # ============================================== 13. PRACTICE QUESTIONS ==========

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        head = self.heading("Practice  ·  Levels 1 and 2")
        table, rows = self.practice_table(head, PRACTICE_A, 1)

        self.speaker("T")
        n = self.narrate(
            id="practice_01",
            text="Codes as before: plus brother, minus sister, times father, divided by mother. Level one.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "Codes")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "Level")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2), FadeIn(rows[1], shift=RIGHT * 0.2), FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="practice_02",
            text="Level two.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "two")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2), FadeIn(rows[4], shift=RIGHT * 0.2), FadeIn(rows[5], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="practice_03",
            text="Pause the video and solve these six.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)
        self.clear_stage()

        head = self.heading("Practice  ·  Level 3")
        table, rows = self.practice_table(head, PRACTICE_B, 7)

        self.speaker("T")
        n = self.narrate(
            id="practice_04",
            text="Level three uses new codes: at, son of; hash, daughter of; dollar, husband of; percent, wife of.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Level")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "new")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2), FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="practice_05",
            text="Pause again and solve these two.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S13_practice")

    # ============================================== 14. ANSWER KEY, WITH REASONING ==========

    def answers(self):
        self.scene_start("S14_answers", title="Answer Key, with Reasoning")

        head = self.heading("Answer key  ·  1 to 4", GOOD)
        table, rows = self.answer_table(head, ANSWERS_A, 1)

        self.speaker("S")
        n = self.narrate(
            id="answers_01",
            text="One: father. P is the father of Q, and Q is the brother of R.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "father")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.at_word(n, "brother")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="answers_02",
            text="Yes. Two: maternal aunt. A is the sister of C's mother.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "aunt")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.at_word(n, "sister")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="answers_03",
            text="Three: paternal uncle. K is the brother of M's father.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "uncle")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.at_word(n, "brother")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="answers_04",
            text="Right. Four: paternal grandmother. D is the mother of E and F, and F is the father of G.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "grandmother")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.at_word(n, "mother")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        self.speaker("S")
        n = self.narrate(
            id="answers_05",
            text="Five: cannot be determined. L is a child of H, but no code describes L.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "cannot")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.at_word(n, "child")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="answers_06",
            text="Yes. Six: R is female and S is male. Sister describes R, and father describes S. T appears only on the "
                 "right, so nothing describes T.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "female")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.at_word(n, "only")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="answers_07",
            text="Seven: grandson. A is the son of B, and B's wife C is his mother. C is the daughter of D.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "grandson")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.at_word(n, "daughter")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="answers_08",
            text="Correct. Eight: daughter-in-law. M is the wife of N, and N is the son of O.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "daughter-in-law")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.at_word(n, "wife")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ============================================== 15. EXAM LENS - RECOGNISE AND MOVE ==========

    def exam_lens(self):
        self.scene_start("S15_exam_lens", title="Exam Lens - Recognise and Move")

        head = self.heading("Exam lens: recognise and move", RATIO)
        blocks = two_line_blocks(LENS, RATIO)
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        self.speaker("T")
        n = self.narrate(
            id="exam_lens_01",
            text="Recognise and move. The recognition cue: symbols defined as relations, then an expression of letters and "
                 "symbols.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "symbols")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="exam_lens_02",
            text="The target time: thirty seconds, including writing the code table.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "target")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "thirty")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="exam_lens_03",
            text="The sanity check: before answering, confirm that the gender of the answer word matches a code that "
                 "describes that person.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "confirm")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        route = VGroup(pill("Table first", GOOD, size=LABEL), pill("One link per symbol", GOOD, size=LABEL),
                       pill("Draw each link", GOOD, size=LABEL)).arrange(RIGHT, buff=0.4)
        gender = text("The codes fix only the genders of the people they describe", LABEL, INK, BOLD)
        answer = pill("Answer from the first-named person;  no gender for the word:  cannot be determined", FOCUS, size=SMALL)
        self.stack(head, [route, gender, answer], buff=0.8, top=1.0)
        self.no_overlap(*route)

        self.speaker("N")
        n = self.narrate(
            id="summary_01",
            text="Quick revision. Write the code table, split the expression at every symbol, and draw each link as you "
                 "read it.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "table")
        self.play(FadeIn(route[0], shift=UP * 0.1))
        self.at_word(n, "split")
        self.play(FadeIn(route[1], shift=UP * 0.1))
        self.at_word(n, "draw")
        self.play(FadeIn(route[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="summary_02",
            text="The codes fix only the genders of the people they describe.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.at_word(n, "genders")
        self.play(FadeIn(gender, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="summary_03",
            text="Answer from the first-named person, and say cannot be determined when the answer word needs a gender no "
                 "code gives.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Answer")
        self.play(FadeIn(answer, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_summary")

    # ============================================== 17. SECTION QUIZ ==========

    def section_quiz(self):
        self.scene_start("S17_section_quiz", title="Section Quiz")

        head = self.heading("Section quiz")
        rules = VGroup(pill("5 questions", WORD, size=BODY), pill("4 minutes", WORD, size=BODY), pill("+3 correct", GOOD, size=BODY),
                       pill("−1 wrong", BAD, size=BODY)).arrange(RIGHT, buff=0.4)
        gate = VGroup(VGroup(pill("12 or more out of 15", GOOD, size=LABEL), text("move on", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.5),
                      VGroup(pill("below 12", BAD, size=LABEL), text("replay the Traps segment, then retry", BODY, INK, BOLD)).arrange(RIGHT, buff=0.5))            .arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        self.stack(head, [rules, gate], buff=1.1, top=1.1)
        self.no_overlap(*rules)
        self.no_overlap(*gate)

        self.speaker("N")
        n = self.narrate(
            id="section_quiz_01",
            text="Now the section quiz: five questions in four minutes, with plus three for a correct answer and minus one "
                 "for a wrong one.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.at_word(n, "quiz")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "questions")
        self.play(FadeIn(rules[0], shift=UP * 0.1))
        self.at_word(n, "minutes")
        self.play(FadeIn(rules[1], shift=UP * 0.1))
        self.at_word(n, "plus")
        self.play(FadeIn(rules[2], shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(rules[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="section_quiz_02",
            text="Twelve or more out of fifteen: move on. Below twelve: replay the traps segment, then retry.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "move")
        self.play(FadeIn(gate[0], shift=RIGHT * 0.2))
        self.at_word(n, "replay")
        self.play(FadeIn(gate[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Section quiz  ·  questions 1 to 3")
        ref = self.legend()
        table, rows = self.table_under(head, ref, ["#", "Question", "Options"],
                                       [[str(0 + i + 1)] + list(row) for i, row in enumerate(QUIZ[0:3])], [0.8, 5.4, 7.0])
        for row in rows:
            row[0].set_color(MUTED)

        self.speaker("N")
        n = self.narrate(
            id="section_quiz_03",
            text="Here are questions one, two and three.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(ref), FadeIn(table[0]))
        self.at_word(n, "one")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "two")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="section_quiz_04",
            text="Pause the video and solve them.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)
        self.clear_stage()

        head = self.heading("Section quiz  ·  questions 4 to 5")
        ref = self.legend()
        table, rows = self.table_under(head, ref, ["#", "Question", "Options"],
                                       [[str(3 + i + 1)] + list(row) for i, row in enumerate(QUIZ[3:5])], [0.8, 5.4, 7.0])
        for row in rows:
            row[0].set_color(MUTED)

        self.speaker("N")
        n = self.narrate(
            id="section_quiz_05",
            text="And here are questions four and five.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(ref), FadeIn(table[0]))
        self.at_word(n, "four")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="section_quiz_06",
            text="Pause again and solve them.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)
        self.clear_stage()

        head = self.heading("Section quiz  ·  answer key", GOOD)
        table, rows = self.answer_table(head, QUIZ_KEY, 1)
        nxt = self.breadcrumb("Next", "Family Puzzles - Multi-Person Trees")
        nxt.next_to(table, DOWN, buff=0.6)
        self.no_overlap(table, nxt)
        self.validator.check_in_frame(VGroup(head, table, nxt))

        self.speaker("T")
        n = self.narrate(
            id="section_quiz_07",
            text="One: option B, mother. T is the mother of V, and V and W are siblings.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "option")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.at_word(n, "siblings")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="section_quiz_08",
            text="Two: option A, paternal uncle. P, Q and R are siblings, and R is the father of S.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "option")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.at_word(n, "father")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="section_quiz_09",
            text="Yes. Three: option C, cannot be determined. O is a grandchild of L, but no code describes O.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "option")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.at_word(n, "grandchild")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="section_quiz_10",
            text="Four: option B: E, F and G. E is a brother, F a mother, G a sister. H appears only on the right.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "option")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.at_word(n, "only")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="section_quiz_11",
            text="Right. Five: option D, grandson. J is the son of K, and K's wife L is his mother. L is the daughter "
                 "of M.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "option")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.at_word(n, "mother")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="section_quiz_12",
            text="Next: family puzzles, with many people on one tree.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.curtain()
        self.scene_end("S17_section_quiz")
