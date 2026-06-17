"""
================================================================================
 Family Tree Render Engine — shared by the tree modules in family_tree.trees
================================================================================
P(name, gender, sp=, sp2=, alias=, kids=[], **flags) builds a node.
`name`, `sp`, `sp2`, `alias` are canonical English keys — translations.json
maps each one to its 'en' and 'fa' display form.

Build the tree data ONCE (language-independent), then call build_pdf() once
per language to get the matching PDF. Persian uses the bundled Vazirmatn font
with arabic-reshaper + python-bidi; English uses Helvetica. Persian titles are
right-aligned (RTL); English titles are left-aligned.

Flags on P():
    root=True        grey two-box root couple
    bridge='(see X page)'   thick border, appears on both pages
    star=True         marks the "you are here" person (* / ★)
    alias='Name'      shown as Name ("Alias") / Name (Alias)
    sp2='Name'        second spouse, shown as sp / sp2
    cousin / cousin_src   spouse subline shows "(cousin)" / "(فامیل)"
    step=True          dotted connector line to this child
================================================================================
"""

import json
import math
from importlib.resources import files

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white

from family_tree.fonts import (
    FONT_REG, FONT_BOLD, FONT_SUB, FONT_SUB_SIZE, FONT_COUSIN_LABEL, STAR,
    register_fonts,
)

# ── Translations ──────────────────────────────────────────────────────────────
with files('family_tree').joinpath('data', 'translations.json').open(encoding='utf-8') as f:
    _T = json.load(f)

def t_name(key, lang):
    """Translate a person name; fall back to the key itself."""
    v = _T['names'].get(key, {}).get(lang, '')
    return v if v else key

def t_ui(key, lang):
    """Translate a UI string; fall back to English."""
    v = _T['ui'].get(key, {}).get(lang, '')
    return v if v else _T['ui'].get(key, {}).get('en', key)

def fa_text(text, lang):
    """Reshape + bidi so ReportLab renders Persian correctly. No-op for English."""
    if lang != 'fa' or not text:
        return text
    return get_display(arabic_reshaper.reshape(str(text)))

def star_suffix(lang):
    """'  |  * = ' (fa) or '  |  ★ = ' (en) — used in page subtitles."""
    return '  |  %s = ' % STAR[lang]

# ── Palette ───────────────────────────────────────────────────────────────────
BG     = white
MALE_F = HexColor('#FFFFFF')
FEM_F  = HexColor('#E6E6E6')
ROOT_F = HexColor('#CFCFCF')
BORDER = HexColor('#111111')
TXT    = HexColor('#111111')
LINE   = HexColor('#444444')
DASH   = HexColor('#111111')

# ── Geometry ──────────────────────────────────────────────────────────────────
ROW_H = 40; COL_W = 180; BOX_W = 150; BOX_UNIFORM = 36
MARGIN_X = 40; MARGIN_TOP = 100; MARGIN_BOT = 35


def P(name, g, sp=None, sp2=None, kids=None, **kw):
    d = {'name': name, 'g': g, 'sp': sp, 'sp2': sp2, 'kids': kids or []}
    d.update(kw)
    return d


# ── Layout (language-independent) ────────────────────────────────────────────
def assign_layout(node, depth, cursor):
    node['depth'] = depth
    if node['kids']:
        for k in node['kids']:
            assign_layout(k, depth + 1, cursor)
        node['y'] = (node['kids'][0]['y'] + node['kids'][-1]['y']) / 2
    else:
        node['y'] = cursor[0]; cursor[0] += ROW_H
    node['x'] = MARGIN_X + depth * COL_W

def count_leaves(n):
    return 1 if not n['kids'] else sum(count_leaves(k) for k in n['kids'])

def max_depth(n):
    return n['depth'] if not n['kids'] else max(max_depth(k) for k in n['kids'])

def find(n, name, depth=None):
    if n['name'] == name and (depth is None or n['depth'] == depth): return n
    for k in n['kids']:
        r = find(k, name, depth)
        if r: return r
    return None


# ── Display text helpers ─────────────────────────────────────────────────────
def fill_for(n):
    if n.get('root'): return ROOT_F
    return MALE_F if n['g'] == 'm' else FEM_F

def disp_name(n, lang):
    s = t_name(n['name'], lang)
    if n.get('alias'):
        alias = t_name(n['alias'], lang)
        s = '%s ("%s")' % (s, alias) if lang == 'en' else '%s (%s)' % (s, alias)
    if n.get('star'):
        s = s + '  ' + STAR[lang]
    return fa_text(s, lang)

def subline(n, lang):
    sp = t_name(n['sp'], lang) if n.get('sp') else None
    prefix = ''
    if n.get('bridge'):
        bridge_txt = n['bridge'] if lang == 'en' else \
            t_ui('see_paternal' if 'paternal' in n['bridge'] else 'see_maternal', lang)
        return fa_text('%s%s   %s' % (prefix, sp, bridge_txt), lang)
    if n.get('sp2'):
        return fa_text('%s%s / %s' % (prefix, sp, t_name(n['sp2'], lang)), lang)
    if n.get('sp'):
        return fa_text('%s%s' % (prefix, sp), lang)
    return None


# ── Drawing ───────────────────────────────────────────────────────────────────
def draw_box(cv, x, y, w, h, fill, name, sub, lang, bold=False, font=9.3):
    cv.setFillColor(fill); cv.setStrokeColor(BORDER); cv.setLineWidth(2.2 if bold else 0.8)
    cv.roundRect(x, y - h / 2, w, h, 4, fill=1, stroke=1)
    cv.setFillColor(TXT)
    if sub:
        cv.setFont(FONT_BOLD[lang], font); cv.drawCentredString(x + w / 2, y + 2.5, name)
        cv.setFont(FONT_SUB[lang], FONT_SUB_SIZE[lang]); cv.drawCentredString(x + w / 2, y - 8.5, sub)
    else:
        cv.setFont(FONT_BOLD[lang], font); cv.drawCentredString(x + w / 2, y - 3, name)

def draw_node(cv, n, ph, lang):
    x = n['x']; y = ph - n['y']
    if n.get('root'):
        gap = BOX_UNIFORM / 2 + 9; cx = x + BOX_W / 2
        draw_box(cv, x, y + gap, BOX_W, BOX_UNIFORM, ROOT_F, fa_text(t_name(n['name'], lang), lang), None, lang, font=10)
        draw_box(cv, x, y - gap, BOX_W, BOX_UNIFORM, ROOT_F, fa_text(t_name(n['sp'], lang), lang),   None, lang, font=10)
        cv.setStrokeColor(BORDER); cv.setLineWidth(1.4); cv.setDash([])
        cv.line(cx, y + gap - BOX_UNIFORM / 2, cx, y - gap + BOX_UNIFORM / 2)
        return
    draw_box(cv, x, y, BOX_W, BOX_UNIFORM, fill_for(n),
             disp_name(n, lang), subline(n, lang), lang, bold=bool(n.get('bridge')))

def draw_connectors(cv, n, ph):
    if not n['kids']: return
    px = n['x'] + BOX_W; py = ph - n['y']; bus = px + (COL_W - BOX_W) / 2
    cv.setLineWidth(1.0)
    for k in n['kids']:
        ky = ph - k['y']
        cv.setStrokeColor(LINE)
        cv.setDash([1, 2] if k.get('step') else ([3, 3] if k.get('adopted') else []))
        cv.line(px, py, bus, py); cv.line(bus, py, bus, ky); cv.line(bus, ky, k['x'], ky)
    cv.setDash([])
    for k in n['kids']:
        draw_connectors(cv, k, ph)


# ── Page renderer ─────────────────────────────────────────────────────────────
def page_size(tree):
    """Natural (width, height) the tree needs. Also assigns x/y/depth on nodes."""
    cursor = [MARGIN_TOP]; assign_layout(tree, 0, cursor)
    pw = MARGIN_X * 2 + (max_depth(tree) + 1) * COL_W
    ph = MARGIN_TOP + count_leaves(tree) * ROW_H + MARGIN_BOT
    return pw, ph


def _draw_title(cv, title, subtitle, lang, x, ty, tsize, ssize):
    """Title + subtitle anchored at edge x (right edge for Persian/RTL, left for
    English), with the title baseline at ty."""
    draw = cv.drawRightString if lang == 'fa' else cv.drawString
    cv.setFillColor(TXT); cv.setFont(FONT_BOLD[lang], tsize)
    draw(x, ty, fa_text(title, lang))
    cv.setFillColor(HexColor('#555555')); cv.setFont(FONT_SUB[lang], ssize)
    draw(x, ty - tsize + 3, fa_text(subtitle, lang))


def _draw_page(cv, tree, title, subtitle, legend_items, lang, cousin_link, pw, ph,
               draw_title=True):
    """Draw the whole page content in natural coordinates (0..pw, 0..ph).
    The caller is responsible for page size and any transform (e.g. tiling).
    draw_title=False skips the heading so the caller can place it unscaled."""
    cv.setFillColor(BG); cv.rect(0, 0, pw, ph, fill=1, stroke=0)

    if draw_title:
        x = (pw - MARGIN_X) if lang == 'fa' else MARGIN_X
        _draw_title(cv, title, subtitle, lang, x, ph - 40, 19, 9.5)

    draw_connectors(cv, tree, ph)

    def _d(n):
        draw_node(cv, n, ph, lang)
        for k in n['kids']: _d(k)
    _d(tree)

    # Cousin marriage link (dashed connector between two boxes)
    if cousin_link:
        wn, wd, hn = cousin_link
        m = find(tree, wn, depth=wd); s = find(tree, hn)
        if m and s:
            mx, my = m['x'], ph - m['y']
            sx, sy = s['x'], ph - s['y']
            lead = min(mx, sx) - 16
            cv.setStrokeColor(DASH); cv.setLineWidth(1.5); cv.setDash([5, 4])
            cv.line(mx, my, lead, my)
            cv.line(lead, my, lead, sy)
            cv.line(lead, sy, sx, sy)
            cv.setDash([])
            # Label intentionally omitted — the legend already explains the dashed line.

    # Legend
    lx, ly = MARGIN_X, 110; cv.setFont(FONT_REG[lang], 8)
    for i, (kind, t) in enumerate(legend_items):
        yy = ly - i * 14
        if kind in ('maleF', 'femF', 'bridge'):
            cv.setFillColor(MALE_F if kind == 'maleF' else (FEM_F if kind == 'femF' else white))
            cv.setStrokeColor(BORDER); cv.setLineWidth(2.2 if kind == 'bridge' else 0.8)
            cv.roundRect(lx, yy - 5, 20, 10, 2, fill=1, stroke=1)
        elif kind in ('cousin', 'adopt', 'step'):
            cv.setStrokeColor(DASH if kind == 'cousin' else LINE)
            cv.setLineWidth(1.5 if kind == 'cousin' else 1.0)
            cv.setDash([5, 4] if kind == 'cousin' else ([3, 3] if kind == 'adopt' else [1, 2]))
            cv.line(lx, yy, lx + 20, yy); cv.setDash([])
        cv.setFillColor(HexColor('#222222')); cv.drawString(lx + 26, yy - 3, fa_text(t, lang))


def render_page(cv, tree, title, subtitle, legend_items, lang, cousin_link=None):
    """Render one tree on a single page sized to fit it (for on-screen viewing)."""
    pw, ph = page_size(tree)
    cv.setPageSize((pw, ph))
    _draw_page(cv, tree, title, subtitle, legend_items, lang, cousin_link, pw, ph)


# ── A4 tiling (for printing on a home printer and gluing together) ─────────────
A4 = (595.27, 841.89)          # portrait, in points
A4_LANDSCAPE = (841.89, 595.27) # landscape, in points
# Per-side blank borders, in points (72pt = 1 inch; 3mm ≈ 8.5pt).
# Edge-to-edge on three sides; a 3mm strip at the bottom only.
PRINT_MARGIN_L = 0
PRINT_MARGIN_R = 0
PRINT_MARGIN_T = 0
PRINT_MARGIN_B = 0
# Inset of the heading from its start edge (right for Persian, left for English)
# and from the top, on the A4 print sheets, in points (24 ≈ 8mm).
TITLE_MARGIN = 24
TITLE_MARGIN_TOP = 24


def plan_tiles(pw, ph, paper, cols=None, min_scale=0.515):
    """Scale the tree to fill the page width exactly, then stack vertically.
    Returns (cols, rows, scale). cols forces a column count (default: auto)."""
    tile_w = paper[0] - PRINT_MARGIN_L - PRINT_MARGIN_R
    tile_h = paper[1] - PRINT_MARGIN_T - PRINT_MARGIN_B
    c = cols or max(1, math.ceil(pw / tile_w))
    s = max(min_scale, c * tile_w / pw)   # fill width; may exceed 1.0 (scale up)
    r = max(1, math.ceil(ph * s / tile_h))
    return c, r, s


def render_page_tiled(cv, tree, title, subtitle, legend_items, lang,
                      cousin_link=None, paper=A4, cols=None, min_scale=0.515):
    """Render one tree split across a grid of portrait `paper` sheets, scaled
    onto the fewest sheets (see plan_tiles). The heading is drawn at a fixed
    size pinned to the page edge on the top row, so it stays large and properly
    aligned regardless of how much the tree itself is scaled down."""
    pw, ph = page_size(tree)
    pgw, pgh = paper
    tile_w = pgw - PRINT_MARGIN_L - PRINT_MARGIN_R
    tile_h = pgh - PRINT_MARGIN_T - PRINT_MARGIN_B
    cols, rows, s = plan_tiles(pw, ph, paper, cols=cols, min_scale=min_scale)
    sh = ph * s                                  # scaled drawing height

    for r in range(rows):
        for c in range(cols):
            cv.setPageSize(paper)
            cv.saveState()
            # Clip to the printable area so content never bleeds past the margin.
            clip = cv.beginPath()
            clip.rect(PRINT_MARGIN_L, PRINT_MARGIN_B, tile_w, tile_h)
            cv.clipPath(clip, stroke=0, fill=0)
            # Place this tile's chunk of the scaled drawing in the printable area.
            cv.translate(PRINT_MARGIN_L - c * tile_w,
                         PRINT_MARGIN_B + (r + 1) * tile_h - sh)
            cv.scale(s, s)
            _draw_page(cv, tree, title, subtitle, legend_items, lang, cousin_link,
                       pw, ph, draw_title=False)
            cv.restoreState()
            # Heading at fixed size on the top-left sheet, pinned to the page edge.
            if r == 0 and c == 0:
                x = (pgw - PRINT_MARGIN_R - TITLE_MARGIN) if lang == 'fa' \
                    else (PRINT_MARGIN_L + TITLE_MARGIN)
                _draw_title(cv, title, subtitle, lang, x, pgh - TITLE_MARGIN_TOP, 16, 9)
            cv.showPage()


def build_pdf(pages, outpath, lang, paper=None, cols=None):
    """Build a PDF. paper=None -> one natural-sized page per tree (default).
    paper=(w, h) -> each tree tiled across that paper size for printing;
    cols forces a column count (otherwise the layout is auto-optimized)."""
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


# ── Legend builders ───────────────────────────────────────────────────────────
def legend_basic(lang, with_step=False):
    items = [
        ('maleF',  t_ui('legend_male', lang)),
        ('femF',   t_ui('legend_female', lang)),
        ('bridge', t_ui('legend_bridge', lang)),
    ]
    if with_step:
        items.append(('step', t_ui('legend_step', lang)))
    return items

def legend_with_cousin(lang, with_step=False):
    base = legend_basic(lang, with_step=False)
    items = base + [('cousin', t_ui('cousins_married', lang))]
    if with_step:
        items.append(('step', t_ui('legend_step', lang)))
    return items
