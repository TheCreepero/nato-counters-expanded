import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from counters import dds, rbm
from counters.layout import COLOURS, ECHELONS, PALETTE_PATH, RBM_ECHELON_NAMES, SIZES, plate_path


def load_symbol_stack(folder, size, echelon, colour):
    pattern = f"mpu.template.*.{RBM_ECHELON_NAMES[echelon]}.{colour}.{size.file_suffix}.dds"
    files = sorted(folder.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No RBM counters match {folder / pattern}")
    return np.stack([dds.read_rgba(path) for path in files]).astype(np.int32)


def read_ink(stack, size):
    y = size.origin_y + size.inner_height // 2
    x = size.origin_x - 1
    return stack[0, y, x, :3]


def blank_plate(stack, ink):
    distance_from_ink = np.abs(stack[:, :, :, :3] - ink).sum(axis=3)
    least_inked = distance_from_ink.argmax(axis=0)
    return np.take_along_axis(stack, least_inked[None, :, :, None], axis=0)[0]


def repair_shared_glyph_pixels(plate, size):
    top, bottom = size.origin_y + 1, size.origin_y + size.inner_height - 1
    left, right = size.origin_x + 2, size.origin_x + size.inner_width - 2
    core = plate[top:bottom, left:right, :3]
    row_colour = np.median(core, axis=1, keepdims=True).astype(plate.dtype)
    repaired = int((np.abs(core - row_colour).max(axis=2) > 0).sum())
    plate[top:bottom, left:right, :3] = row_colour
    return repaired


def main():
    parser = argparse.ArgumentParser(description="Derive blank counter plates from an installed copy of RBM's GFX Overhaul.")
    parser.add_argument("--rbm-dir", type=Path, help="Folder of the installed RBM's GFX Overhaul mod.")
    arguments = parser.parse_args()

    rbm_dir = arguments.rbm_dir or rbm.find_rbm_install()
    if rbm_dir is None or not rbm_dir.is_dir():
        sys.exit("RBM's GFX Overhaul was not found. Pass --rbm-dir <folder>.")

    palette = {}
    plate_count = 0
    repaired_total = 0
    for size in SIZES:
        source_folder = rbm.counters_folder(rbm_dir) / size.folder
        for colour in COLOURS:
            for echelon in ECHELONS:
                stack = load_symbol_stack(source_folder, size, echelon, colour)
                ink = read_ink(stack, size)
                plate = blank_plate(stack, ink)
                repaired_total += repair_shared_glyph_pixels(plate, size)
                target = plate_path(size, colour, echelon)
                target.parent.mkdir(parents=True, exist_ok=True)
                Image.fromarray(plate.astype(np.uint8), "RGBA").save(target)
                plate_count += 1
                recorded = palette.setdefault(colour, {"ink": [int(value) for value in ink]})
                if recorded["ink"] != [int(value) for value in ink]:
                    sys.exit(f"Ink colour for '{colour}' differs between plates: {recorded['ink']} and {ink.tolist()}")

    PALETTE_PATH.write_text(json.dumps(palette, indent=4) + "\n", encoding="utf-8", newline="\r\n")
    print(f"Source: {rbm_dir}")
    print(f"Wrote {plate_count} plates and {PALETTE_PATH.name}")
    print(f"Interior pixels covered by every RBM symbol and repaired from their row: {repaired_total}")


if __name__ == "__main__":
    main()
