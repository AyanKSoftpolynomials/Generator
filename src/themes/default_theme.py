"""Default LMS visual theme.

Every visual constant (colours, font sizes, spacing, timing, strokes) lives
here so the whole look of the videos can be changed from one file.
Components in ``src/components`` read from this module; lesson scripts can
import it directly too:

    from src.themes import default_theme as theme
    Text("Hi", color=theme.ACCENT)

Colours are plain hex strings, which Manim accepts anywhere it takes a colour.
"""

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------

# Deep navy background. Keep in sync with background_color in manim.cfg.
BACKGROUND = "#0E1726"

TEXT_PRIMARY = "#F4F6FA"    # titles and body text
TEXT_SECONDARY = "#A9B4C7"  # subtitles, captions, less important text
TEXT_MUTED = "#6B7A90"      # hints, faded content

ACCENT = "#4CC3FF"          # main brand accent: key objects, section labels
ACCENT_ALT = "#9B8CFF"      # secondary accent for contrast with ACCENT

HIGHLIGHT = "#FFC857"       # drawing attention to a word/term/number
IMPORTANT = "#FF8A5B"       # "remember this" information boxes

CORRECT = "#3DDC97"         # correct answers / ticks
INCORRECT = "#FF5C7A"       # incorrect answers / crosses

EQUATION = TEXT_PRIMARY     # default colour for maths
NUMBER_LINE = "#C9D3E3"     # axis, ticks and numbers on number lines
ARROW = ACCENT              # default arrow colour

BOX_FILL = "#16233A"        # fill for info boxes / cards
BOX_FILL_OPACITY = 0.9

# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------

# Font used by Text(). Pango falls back to a default sans-serif font if this
# is not installed. To ship a custom font, put it in assets/fonts/ and see
# README.md > "Adding assets".
FONT = "Segoe UI"

TITLE_SIZE = 56
SUBTITLE_SIZE = 36
BODY_SIZE = 30
LABEL_SIZE = 24
SECTION_LABEL_SIZE = 22
EQUATION_SIZE = 48

# ---------------------------------------------------------------------------
# Layout (Manim units; the frame is ~14.2 wide x 8 tall)
# ---------------------------------------------------------------------------

MARGIN = 0.5          # distance from frame edges
SPACING_SMALL = 0.2
SPACING_MEDIUM = 0.4
SPACING_LARGE = 0.8

CORNER_RADIUS = 0.15  # rounded corners on boxes
BOX_PADDING = 0.3     # space between a box and its content

# ---------------------------------------------------------------------------
# Strokes
# ---------------------------------------------------------------------------

STROKE_THIN = 2
STROKE_NORMAL = 4
STROKE_THICK = 6

# ---------------------------------------------------------------------------
# Animation timing (seconds)
# ---------------------------------------------------------------------------

ANIM_FAST = 0.4
ANIM_NORMAL = 0.8
ANIM_SLOW = 1.5

PAUSE_SHORT = 0.5
PAUSE = 1.0
PAUSE_LONG = 2.0
