import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw

from .layout import UNIT_HEIGHT, UNIT_WIDTH

SUPERSAMPLE = 8
STROKE = 1.6

W = UNIT_WIDTH
H = UNIT_HEIGHT
CX = W / 2
CY = H / 2

# Fitted on RBM's Military Police "MP" at map size, where the pipeline compares every symbol: 0.86 with the letters
# 0.5 right of and 0.75 below the centre, where RBM puts them. RBM draws its designer-size letters smaller (0.84 alone
# at height 10.5), so one draw function cannot match both sizes; these values score 0.59 there.
TEXT_HEIGHT = 12.0
TEXT_STROKE = 2.5
LETTER_SPACING = 0.2


def _arc(centre_x, centre_y, radius_x, radius_y, start_degrees, end_degrees):
    return ("arc", centre_x, centre_y, radius_x, radius_y, start_degrees, end_degrees)


# Stroke font in RBM's style (its Military Police "MP" and Militia "M"): each glyph is (advance, strokes), drawn as the
# centre line of the stroke in a box whose height is 1. A stroke is a polyline or an _arc; angles in degrees, y down.
GLYPHS = {
    " ": (0.5, ()),
    "A": (0.8, ([(0, 1), (0.4, 0), (0.8, 1)], [(0.16, 0.62), (0.64, 0.62)])),
    "B": (0.7, ([(0, 0), (0, 1)], [(0, 0), (0.4, 0)], _arc(0.4, 0.24, 0.26, 0.24, -90, 90), [(0.4, 0.48), (0, 0.48)],
                [(0.4, 0.48), (0.42, 0.48)], _arc(0.42, 0.74, 0.28, 0.26, -90, 90), [(0.42, 1), (0, 1)])),
    "C": (0.75, (_arc(0.45, 0.5, 0.45, 0.5, 40, 320),)),
    "D": (0.75, ([(0, 0), (0, 1)], [(0, 0), (0.25, 0)], _arc(0.25, 0.5, 0.5, 0.5, -90, 90), [(0.25, 1), (0, 1)])),
    "E": (0.6, ([(0.6, 0), (0, 0), (0, 1), (0.6, 1)], [(0, 0.5), (0.5, 0.5)])),
    "F": (0.6, ([(0.6, 0), (0, 0), (0, 1)], [(0, 0.5), (0.5, 0.5)])),
    "G": (0.8, (_arc(0.42, 0.5, 0.42, 0.5, 320, 0), [(0.84, 0.5), (0.84, 1)], [(0.84, 0.55), (0.48, 0.55)])),
    "H": (0.7, ([(0, 0), (0, 1)], [(0.7, 0), (0.7, 1)], [(0, 0.5), (0.7, 0.5)])),
    "I": (0.0, ([(0, 0), (0, 1)],)),
    "J": (0.6, ([(0.6, 0), (0.6, 0.7)], _arc(0.3, 0.7, 0.3, 0.3, 0, 180))),
    "K": (0.7, ([(0, 0), (0, 1)], [(0.7, 0), (0, 0.62)], [(0.25, 0.42), (0.7, 1)])),
    "L": (0.6, ([(0, 0), (0, 1), (0.6, 1)],)),
    "M": (1.0, ([(0, 1), (0, 0)], [(1.0, 0), (1.0, 1)], [(0.22, 0), (0.5, 1), (0.78, 0)])),
    "N": (0.75, ([(0, 1), (0, 0), (0.75, 1), (0.75, 0)],)),
    "O": (0.85, (_arc(0.425, 0.5, 0.425, 0.5, 0, 360),)),
    "P": (0.78, ([(0, 1), (0, 0), (0.55, 0)], _arc(0.55, 0.25, 0.23, 0.25, -90, 90), [(0.55, 0.5), (0, 0.5)])),
    "Q": (0.85, (_arc(0.425, 0.5, 0.425, 0.5, 0, 360), [(0.5, 0.65), (0.85, 1)])),
    "R": (0.78, ([(0, 1), (0, 0), (0.55, 0)], _arc(0.55, 0.25, 0.23, 0.25, -90, 90), [(0.55, 0.5), (0, 0.5)],
                 [(0.45, 0.5), (0.78, 1)])),
    "S": (0.7, (_arc(0.35, 0.25, 0.33, 0.25, 330, 90), _arc(0.35, 0.75, 0.35, 0.25, 270, 510))),
    "T": (0.7, ([(0, 0), (0.7, 0)], [(0.35, 0), (0.35, 1)])),
    "U": (0.7, ([(0, 0), (0, 0.65)], _arc(0.35, 0.65, 0.35, 0.35, 180, 0), [(0.7, 0.65), (0.7, 0)])),
    "V": (0.8, ([(0, 0), (0.4, 1), (0.8, 0)],)),
    "W": (1.1, ([(0, 0), (0.25, 1), (0.55, 0.2), (0.85, 1), (1.1, 0)],)),
    "X": (0.75, ([(0, 0), (0.75, 1)], [(0.75, 0), (0, 1)])),
    "Y": (0.75, ([(0, 0), (0.375, 0.5), (0.75, 0)], [(0.375, 0.5), (0.375, 1)])),
    "Z": (0.7, ([(0, 0), (0.7, 0), (0, 1), (0.7, 1)],)),
    "0": (0.7, (_arc(0.35, 0.5, 0.35, 0.5, 0, 360),)),
    "1": (0.3, ([(0, 0.2), (0.3, 0), (0.3, 1)],)),
    "2": (0.7, (_arc(0.35, 0.3, 0.35, 0.3, 200, 360), [(0.7, 0.3), (0, 1), (0.7, 1)])),
    "3": (0.7, (_arc(0.33, 0.25, 0.33, 0.25, 200, 450), _arc(0.35, 0.75, 0.35, 0.25, 270, 520))),
    "4": (0.75, ([(0.55, 1), (0.55, 0), (0, 0.7), (0.75, 0.7)],)),
    "5": (0.7, ([(0.65, 0), (0.05, 0), (0, 0.45), (0.33, 0.36)], _arc(0.33, 0.68, 0.37, 0.32, 270, 495))),
    "6": (0.7, ([(0.55, 0), (0.02, 0.62)], _arc(0.35, 0.7, 0.35, 0.3, 0, 360))),
    "7": (0.7, ([(0, 0), (0.7, 0), (0.25, 1)],)),
    "8": (0.7, (_arc(0.35, 0.24, 0.3, 0.24, 0, 360), _arc(0.35, 0.74, 0.35, 0.26, 0, 360))),
    "9": (0.7, (_arc(0.35, 0.3, 0.35, 0.3, 0, 360), [(0.68, 0.38), (0.15, 1)])),
}


def glyph(character):
    try:
        return GLYPHS[character.upper()]
    except KeyError:
        raise KeyError(f"The text primitive has no glyph for {character!r}; add one to GLYPHS in tools/counters/canvas.py.") from None


def text_width(text, height=TEXT_HEIGHT, width=TEXT_STROKE, spacing=LETTER_SPACING):
    """Width in units of the ink Pen.text draws for `text`."""
    skeleton = height - width
    return sum(glyph(character)[0] * skeleton + width for character in text) + spacing * height * max(0, len(text) - 1)


class Pen:
    def __init__(self, size):
        self.size = size
        self.image = Image.new("L", (size.width * SUPERSAMPLE, size.height * SUPERSAMPLE), 0)
        self.draw = ImageDraw.Draw(self.image)

    def _point(self, x, y):
        return (
            (self.size.origin_x + x * self.size.scale_x) * SUPERSAMPLE,
            (self.size.origin_y + y * self.size.scale_y) * SUPERSAMPLE,
        )

    def _stroke(self, width):
        return max(1, round(width * self.size.stroke_scale * SUPERSAMPLE))

    def line(self, points, width=STROKE, round_caps=False):
        self.draw.line([self._point(x, y) for x, y in points], fill=255, width=self._stroke(width), joint="curve")
        if round_caps:
            for x, y in (points[0], points[-1]):
                self.disc(x, y, width / 2)

    def polygon(self, points):
        self.draw.polygon([self._point(x, y) for x, y in points], fill=255)

    def disc(self, x, y, radius):
        self.draw.ellipse([self._point(x - radius, y - radius), self._point(x + radius, y + radius)], fill=255)

    def ring(self, x, y, radius, width=STROKE):
        half = width / 2
        outer = [self._point(x - radius - half, y - radius - half), self._point(x + radius + half, y + radius + half)]
        self.draw.ellipse(outer, outline=255, width=self._stroke(width))

    def arc(self, x, y, radius_x, radius_y, start_degrees, end_degrees, width=STROKE):
        steps = max(8, int(abs(end_degrees - start_degrees) / 3))
        points = []
        for step in range(steps + 1):
            angle = math.radians(start_degrees + (end_degrees - start_degrees) * step / steps)
            points.append((x + radius_x * math.cos(angle), y + radius_y * math.sin(angle)))
        self.line(points, width)

    def oval(self, left, top, right, bottom, width=STROKE):
        x0, y0 = self._point(left, top)
        x1, y1 = self._point(right, bottom)
        stroke = self._stroke(width)
        half = stroke / 2
        radius = (y1 - y0) / 2 + half
        self.draw.rounded_rectangle([x0 - half, y0 - half, x1 + half, y1 + half], radius=radius, outline=255, width=stroke)

    def text(self, text, x=CX, y=CY, height=TEXT_HEIGHT, width=TEXT_STROKE, spacing=LETTER_SPACING, anchor="center"):
        """Capitals and digits from GLYPHS, `height` units tall in ink, centred on (x, y) or starting at x for anchor="left".

        Straight strokes get square ends and every glyph is clipped to its own box, so letters are flat at the top and
        bottom and square at the corners, as RBM draws them.
        """
        skeleton = height - width
        left = x - text_width(text, height, width, spacing) / 2 if anchor == "center" else x
        top = y - height / 2
        for character in text:
            advance, strokes = glyph(character)
            glyph_width = advance * skeleton + width
            scratch = Image.new("L", self.image.size, 0)
            draw = ImageDraw.Draw(scratch)

            def unit(point):
                return self._point(left + width / 2 + point[0] * skeleton, top + width / 2 + point[1] * skeleton)

            for stroke in strokes:
                if stroke[0] == "arc":
                    _, centre_x, centre_y, radius_x, radius_y, start, end = stroke
                    steps = max(8, int(abs(end - start) / 3))
                    points = [(centre_x + radius_x * math.cos(math.radians(start + (end - start) * step / steps)),
                               centre_y + radius_y * math.sin(math.radians(start + (end - start) * step / steps)))
                              for step in range(steps + 1)]
                    draw.line([unit(point) for point in points], fill=255, width=self._stroke(width), joint="curve")
                    continue
                for (x0, y0), (x1, y1) in zip(stroke, stroke[1:]):
                    length = math.hypot(x1 - x0, y1 - y0) or 1.0
                    reach = width / 2 / skeleton / length
                    ends = [(x0 - (x1 - x0) * reach, y0 - (y1 - y0) * reach), (x1 + (x1 - x0) * reach, y1 + (y1 - y0) * reach)]
                    draw.line([unit(point) for point in ends], fill=255, width=self._stroke(width))
            box_left, box_top = self._point(left, top)
            box_right, box_bottom = self._point(left + glyph_width, top + height)
            box = tuple(round(value) for value in (box_left, box_top, box_right, box_bottom))
            self.image.paste(ImageChops.lighter(self.image.crop(box), scratch.crop(box)), box[:2])
            left += glyph_width + spacing * height

    def coverage(self):
        reduced = self.image.resize((self.size.width, self.size.height), Image.BOX)
        coverage = np.asarray(reduced, dtype=np.float64) / 255.0
        inside = np.zeros_like(coverage)
        top, left = self.size.origin_y, self.size.origin_x
        inside[top:top + self.size.inner_height, left:left + self.size.inner_width] = 1.0
        return coverage * inside
