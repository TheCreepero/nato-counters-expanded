import json

import numpy as np
from PIL import Image

from . import rbm
from .canvas import Pen
from .layout import FIRST_INDEX, PALETTE_PATH, SMALL, plate_path

MATCH_THRESHOLD = 0.8
DUPLICATE_THRESHOLD = 0.8


def interior(pixels, size=SMALL):
    return pixels[size.origin_y:size.origin_y + size.inner_height, size.origin_x:size.origin_x + size.inner_width]


def symbol_coverage(symbol, size=SMALL):
    pen = Pen(size)
    symbol.draw(pen)
    return interior(pen.coverage(), size)


def coverage_from_counter(pixels, size=SMALL):
    plate = interior(np.asarray(Image.open(plate_path(size, "white", "div")).convert("RGBA")), size)[:, :, :3].astype(np.float64)
    ink = np.array(json.loads(PALETTE_PATH.read_text(encoding="utf-8"))["white"]["ink"], dtype=np.float64)
    shown = interior(pixels, size)[:, :, :3].astype(np.float64)
    return np.clip(((plate - shown) / (plate - ink)).mean(axis=2), 0.0, 1.0)


def match_score(first, second):
    union = np.maximum(first, second).sum()
    if union == 0:
        return 1.0
    return float(np.minimum(first, second).sum() / union)


def coverage_grid(coverage):
    return ["".join("." if value < 0.04 else "%x" % round(value * 15) for value in row) for row in coverage]


def side_by_side(reference, rendered):
    lines = [f"{'RBM reference':<{reference.shape[1]}}   rendered"]
    for left, right in zip(coverage_grid(reference), coverage_grid(rendered)):
        lines.append(f"{left}   {right}")
    return "\n".join(lines)


def check_symbols(rbm_dir, symbols):
    problems = []
    rows = []

    existing = {name: coverage_from_counter(rbm.template_counter(rbm_dir, name, SMALL)) for name in rbm.RBM_TEMPLATE_SYMBOLS}
    for symbol in symbols:
        rendered = symbol_coverage(symbol)
        closest_name, closest_score = max(((name, match_score(rendered, coverage)) for name, coverage in existing.items()),
                                          key=lambda item: item[1])
        if closest_score >= DUPLICATE_THRESHOLD:
            problems.append(f"{symbol.key}: duplicates RBM's own '{closest_name}' counter (match {closest_score:.2f}).")

        if symbol.reference is None:
            rows.append((symbol, None, closest_name, closest_score))
            continue
        reference = coverage_from_counter(rbm.battalion_nato_frame(rbm_dir, symbol.reference))
        score = match_score(rendered, reference)
        rows.append((symbol, score, closest_name, closest_score))
        if score < MATCH_THRESHOLD:
            problems.append(
                f"{symbol.key}: matches RBM's '{symbol.reference}' battalion icon only {score:.2f} (needs {MATCH_THRESHOLD:.2f})."
            )
    return rows, problems


def check_indices(manifest, rbm_dir, game_dir):
    problems = []
    unverified = []
    chosen = set(manifest.values())
    below = sorted(index for index in chosen if index < FIRST_INDEX)
    if below:
        problems.append(f"Icon indices {below} lie below {FIRST_INDEX}, inside the range of RBM's GFX Overhaul, the game or its DLC.")
    if rbm_dir is None or not rbm_dir.is_dir():
        unverified.append("RBM's GFX Overhaul")
    else:
        highest = max(rbm.declared_template_indices(rbm_dir))
        if highest + 1 != FIRST_INDEX:
            problems.append(
                f"RBM's GFX Overhaul now ends at icon index {highest}, but this mod starts at {FIRST_INDEX}. "
                "The picker stops at the first index without a sprite, so the two must meet exactly: stop and tell the owner."
            )
    if game_dir is None or not game_dir.is_dir():
        unverified.append("the game")
    else:
        taken = sorted(chosen & rbm.declared_template_indices(game_dir))
        if taken:
            problems.append(f"The game or its DLC now declares icon indices {taken}, which this mod also uses: stop and tell the owner.")
    return problems, unverified
