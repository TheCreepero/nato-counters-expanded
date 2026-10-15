import argparse
import sys
from pathlib import Path

from counters import rbm, reference
from counters.symbols import SYMBOLS


def print_report(rows):
    print(f"{'symbol':<22} {'RBM battalion icon':<32} {'match':>6}   closest existing RBM counter")
    for symbol, score, closest_name, closest_score in rows:
        shown_score = "  none" if score is None else f"{score:6.2f}"
        print(f"{symbol.key:<22} {symbol.reference or '-':<32} {shown_score}   {closest_name} ({closest_score:.2f})")


def main():
    parser = argparse.ArgumentParser(description="Compare every symbol with the icon RBM's GFX Overhaul draws for the same branch.")
    parser.add_argument("--rbm-dir", type=Path, help="Folder of the installed RBM's GFX Overhaul mod.")
    parser.add_argument("--show", metavar="SYMBOL_KEY", help="Print the reference and the rendered symbol pixel by pixel.")
    parser.add_argument("--list", action="store_true", help="List the battalion icons RBM's GFX Overhaul provides.")
    parser.add_argument("--reference", metavar="NAME", help="Print one RBM battalion icon pixel by pixel.")
    arguments = parser.parse_args()

    rbm_dir = arguments.rbm_dir or rbm.find_rbm_install()
    if rbm_dir is None or not rbm_dir.is_dir():
        sys.exit("RBM's GFX Overhaul was not found. Pass --rbm-dir <folder>.")

    if arguments.list:
        print("\n".join(rbm.battalion_names(rbm_dir)))
        return

    if arguments.reference:
        coverage = reference.coverage_from_counter(rbm.battalion_nato_frame(rbm_dir, arguments.reference))
        print("\n".join(reference.coverage_grid(coverage)))
        return

    if arguments.show:
        symbol = next((candidate for candidate in SYMBOLS if candidate.key == arguments.show), None)
        if symbol is None:
            sys.exit(f"No symbol has the key '{arguments.show}'.")
        if symbol.reference is None:
            sys.exit(f"'{symbol.key}' declares no RBM reference.")
        expected = reference.coverage_from_counter(rbm.battalion_nato_frame(rbm_dir, symbol.reference))
        rendered = reference.symbol_coverage(symbol)
        print(reference.side_by_side(expected, rendered))
        print(f"match {reference.match_score(rendered, expected):.2f} (needs {reference.MATCH_THRESHOLD:.2f})")
        return

    rows, problems = reference.check_symbols(rbm_dir, SYMBOLS)
    print_report(rows)
    if problems:
        sys.exit("\n" + "\n".join(problems))


if __name__ == "__main__":
    main()
