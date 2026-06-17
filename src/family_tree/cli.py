"""
Command-line entry point for building family-tree PDFs.

Examples:
    family-tree                  # build every tree, all languages
    family-tree emma             # just the Emma tree, all languages
    family-tree lars --lang fa   # just the Lars tree, Persian only
    family-tree --out /tmp/pdfs  # choose the output directory
"""

import argparse
from collections.abc import Sequence
from pathlib import Path

from family_tree.render import build_pdf, A4_LANDSCAPE
from family_tree.trees import ALL


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog='family-tree',
        description='Generate multilingual family-tree PDFs.',
    )
    parser.add_argument(
        'trees', nargs='*', choices=sorted(ALL),
        help='Which tree(s) to build (default: all).',
    )
    parser.add_argument(
        '--lang', choices=['fa', 'en', 'nl', 'all'], default='all',
        help='Language to render (default: all).',
    )
    parser.add_argument(
        '--out', default='output', type=Path,
        help='Output directory for the PDFs (default: ./output).',
    )
    parser.add_argument(
        '--print', dest='print_a4', action='store_true',
        help='Also write A4-tiled "_a4" PDFs (split across sheets to glue together).',
    )
    parser.add_argument(
        '--print-cols', dest='print_cols', type=int, default=1,
        help='How many A4 columns wide the printout is (default: 1).',
    )
    args = parser.parse_args(argv)

    trees = args.trees or sorted(ALL)
    langs = ['fa', 'en', 'nl'] if args.lang == 'all' else [args.lang]
    args.out.mkdir(parents=True, exist_ok=True)

    for name in trees:
        module = ALL[name]
        for lang in langs:
            lang_dir = args.out / name / lang
            lang_dir.mkdir(parents=True, exist_ok=True)
            outpath = lang_dir / f'{module.SLUG}_{lang}.pdf'
            build_pdf(module.make_pages(lang), str(outpath), lang)
            print(f'wrote {outpath}')
            if args.print_a4:
                a4path = lang_dir / f'{module.SLUG}_{lang}_a4.pdf'
                build_pdf(module.make_pages(lang), str(a4path), lang,
                          paper=A4_LANDSCAPE, cols=args.print_cols)
                print(f'wrote {a4path}')


if __name__ == '__main__':
    main()
