"""PDF output: single-page and A4-tiled rendering."""

import math
from typing import Any

from reportlab.pdfgen import canvas
from reportlab.pdfgen.canvas import Canvas

from family_tree.fonts import register_fonts
from family_tree.layout import page_size
from family_tree.drawing import draw_page, draw_title

A4: tuple[float, float] = (595.27, 841.89)
A4_LANDSCAPE: tuple[float, float] = (841.89, 595.27)

# Per-side blank borders in points. Edge-to-edge on all sides.
PRINT_MARGIN_L = 0
PRINT_MARGIN_R = 0
PRINT_MARGIN_T = 0
PRINT_MARGIN_B = 0
# Inset of the heading from its page edge on A4 print sheets (≈8mm).
TITLE_MARGIN = 24
TITLE_MARGIN_TOP = 24


def render_page(cv: Canvas, tree: dict[str, Any], title: str, subtitle: str,
               legend_items: list[tuple[str, str]], lang: str,
               cousin_link: tuple[str, int, str] | None = None) -> None:
    """Render one tree on a single page sized to fit it (for on-screen viewing)."""
    pw, ph = page_size(tree)
    cv.setPageSize((pw, ph))
    draw_page(cv, tree, title, subtitle, legend_items, lang, cousin_link, pw, ph)


def plan_tiles(pw: float, ph: float, paper: tuple[float, float],
               cols: int | None = None, min_scale: float = 0.515) -> tuple[int, int, float]:
    """Scale the tree to fill the page width exactly, then stack vertically.
    Returns (cols, rows, scale). cols forces a column count (default: auto)."""
    tile_w = paper[0] - PRINT_MARGIN_L - PRINT_MARGIN_R
    tile_h = paper[1] - PRINT_MARGIN_T - PRINT_MARGIN_B
    c = cols or max(1, math.ceil(pw / tile_w))
    s = max(min_scale, c * tile_w / pw)
    r = max(1, math.ceil(ph * s / tile_h))
    return c, r, s


def render_page_tiled(cv: Canvas, tree: dict[str, Any], title: str, subtitle: str,
                      legend_items: list[tuple[str, str]], lang: str,
                      cousin_link: tuple[str, int, str] | None = None,
                      paper: tuple[float, float] = A4,
                      cols: int | None = None, min_scale: float = 0.515) -> None:
    """Render one tree split across a grid of portrait `paper` sheets, scaled
    onto the fewest sheets. The heading is drawn at a fixed size on the top
    sheet, unaffected by the tree scale."""
    pw, ph = page_size(tree)
    pgw, pgh = paper
    tile_w = pgw - PRINT_MARGIN_L - PRINT_MARGIN_R
    tile_h = pgh - PRINT_MARGIN_T - PRINT_MARGIN_B
    cols, rows, s = plan_tiles(pw, ph, paper, cols=cols, min_scale=min_scale)
    sh = ph * s

    for r in range(rows):
        for c in range(cols):
            cv.setPageSize(paper)
            cv.saveState()
            clip = cv.beginPath()
            clip.rect(PRINT_MARGIN_L, PRINT_MARGIN_B, tile_w, tile_h)
            cv.clipPath(clip, stroke=0, fill=0)
            cv.translate(PRINT_MARGIN_L - c * tile_w,
                         PRINT_MARGIN_B + (r + 1) * tile_h - sh)
            cv.scale(s, s)
            draw_page(cv, tree, title, subtitle, legend_items, lang, cousin_link,
                      pw, ph, draw_title_flag=False)
            cv.restoreState()
            if r == 0 and c == 0:
                x = (pgw - PRINT_MARGIN_R - TITLE_MARGIN) if lang == 'fa' \
                    else (PRINT_MARGIN_L + TITLE_MARGIN)
                draw_title(cv, title, subtitle, lang, x, pgh - TITLE_MARGIN_TOP, 16, 9)
            cv.showPage()


def build_pdf(pages: list[dict[str, Any]], outpath: str, lang: str,
              paper: tuple[float, float] | None = None, cols: int | None = None) -> None:
    """Build a PDF. paper=None -> one natural-sized page per tree (default).
    paper=(w, h) -> each tree tiled across that paper size for printing."""
    register_fonts()
    cv = canvas.Canvas(outpath)
    for pg in pages:
        args = (cv, pg['tree'], pg['title'], pg['subtitle'],
                pg['legend'], lang, pg.get('cousin_link'))
        if paper:
            render_page_tiled(*args, paper=paper, cols=cols)
        else:
            render_page(*args)
            cv.showPage()
    cv.save()
