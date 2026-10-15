import math

import numpy as np
from PIL import Image, ImageDraw

from .layout import UNIT_HEIGHT, UNIT_WIDTH

SUPERSAMPLE = 8
STROKE = 1.6

W = UNIT_WIDTH
H = UNIT_HEIGHT
CX = W / 2
CY = H / 2


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

    def coverage(self):
        reduced = self.image.resize((self.size.width, self.size.height), Image.BOX)
        coverage = np.asarray(reduced, dtype=np.float64) / 255.0
        inside = np.zeros_like(coverage)
        top, left = self.size.origin_y, self.size.origin_x
        inside[top:top + self.size.inner_height, left:left + self.size.inner_width] = 1.0
        return coverage * inside
