from reportlab.lib.colors import HexColor, white

from family_tree.fonts import FONT_REG, FONT_BOLD, FONT_SUB, FONT_SUB_SIZE, STAR
from family_tree.translations import t_name, t_ui, fa_text
from family_tree.layout import BOX_W, BOX_UNIFORM, COL_W, MARGIN_X, find

# Colour palette
BG     = white
MALE_F = HexColor('#FFFFFF')
FEM_F  = HexColor('#E6E6E6')
ROOT_F = HexColor('#CFCFCF')
BORDER = HexColor('#111111')
TXT    = HexColor('#111111')
LINE   = HexColor('#444444')
DASH   = HexColor('#111111')


def fill_for(n):
    if n.get('root'):
        return ROOT_F
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


def draw_box(cv, x, y, w, h, fill, name, sub, lang, bold=False, font=9.3):
    cv.setFillColor(fill)
    cv.setStrokeColor(BORDER)
    cv.setLineWidth(2.2 if bold else 0.8)
    cv.roundRect(x, y - h / 2, w, h, 4, fill=1, stroke=1)
    cv.setFillColor(TXT)
    if sub:
        cv.setFont(FONT_BOLD[lang], font)
        cv.drawCentredString(x + w / 2, y + 2.5, name)
        cv.setFont(FONT_SUB[lang], FONT_SUB_SIZE[lang])
        cv.drawCentredString(x + w / 2, y - 8.5, sub)
    else:
        cv.setFont(FONT_BOLD[lang], font)
        cv.drawCentredString(x + w / 2, y - 3, name)


def draw_node(cv, n, ph, lang):
    x = n['x']
    y = ph - n['y']
    if n.get('root'):
        gap = BOX_UNIFORM / 2 + 9
        cx = x + BOX_W / 2
        draw_box(cv, x, y + gap, BOX_W, BOX_UNIFORM, ROOT_F,
                 fa_text(t_name(n['name'], lang), lang), None, lang, font=10)
        draw_box(cv, x, y - gap, BOX_W, BOX_UNIFORM, ROOT_F,
                 fa_text(t_name(n['sp'], lang), lang), None, lang, font=10)
        cv.setStrokeColor(BORDER)
        cv.setLineWidth(1.4)
        cv.setDash([])
        cv.line(cx, y + gap - BOX_UNIFORM / 2, cx, y - gap + BOX_UNIFORM / 2)
        return
    draw_box(cv, x, y, BOX_W, BOX_UNIFORM, fill_for(n),
             disp_name(n, lang), subline(n, lang), lang, bold=bool(n.get('bridge')))


def draw_connectors(cv, n, ph):
    if not n['kids']:
        return
    px = n['x'] + BOX_W
    py = ph - n['y']
    bus = px + (COL_W - BOX_W) / 2
    cv.setLineWidth(1.0)
    for k in n['kids']:
        ky = ph - k['y']
        cv.setStrokeColor(LINE)
        cv.setDash([1, 2] if k.get('step') else ([3, 3] if k.get('adopted') else []))
        cv.line(px, py, bus, py)
        cv.line(bus, py, bus, ky)
        cv.line(bus, ky, k['x'], ky)
    cv.setDash([])
    for k in n['kids']:
        draw_connectors(cv, k, ph)


def draw_title(cv, title, subtitle, lang, x, ty, tsize, ssize):
    """Title + subtitle anchored at edge x (right for Persian/RTL, left for English)."""
    draw = cv.drawRightString if lang == 'fa' else cv.drawString
    cv.setFillColor(TXT)
    cv.setFont(FONT_BOLD[lang], tsize)
    draw(x, ty, fa_text(title, lang))
    cv.setFillColor(HexColor('#555555'))
    cv.setFont(FONT_SUB[lang], ssize)
    draw(x, ty - tsize + 3, fa_text(subtitle, lang))


def draw_page(cv, tree, title, subtitle, legend_items, lang, cousin_link, pw, ph,
              draw_title_flag=True):
    """Draw the whole page content in natural coordinates (0..pw, 0..ph).
    The caller is responsible for page size and any transform (e.g. tiling)."""
    cv.setFillColor(BG)
    cv.rect(0, 0, pw, ph, fill=1, stroke=0)

    if draw_title_flag:
        x = (pw - MARGIN_X) if lang == 'fa' else MARGIN_X
        draw_title(cv, title, subtitle, lang, x, ph - 40, 19, 9.5)

    draw_connectors(cv, tree, ph)

    def _d(n):
        draw_node(cv, n, ph, lang)
        for k in n['kids']:
            _d(k)
    _d(tree)

    if cousin_link:
        wn, wd, hn = cousin_link
        m = find(tree, wn, depth=wd)
        s = find(tree, hn)
        if m and s:
            mx, my = m['x'], ph - m['y']
            sx, sy = s['x'], ph - s['y']
            lead = min(mx, sx) - 16
            cv.setStrokeColor(DASH)
            cv.setLineWidth(1.5)
            cv.setDash([5, 4])
            cv.line(mx, my, lead, my)
            cv.line(lead, my, lead, sy)
            cv.line(lead, sy, sx, sy)
            cv.setDash([])

    lx, ly = MARGIN_X, 110
    cv.setFont(FONT_REG[lang], 8)
    for i, (kind, t) in enumerate(legend_items):
        yy = ly - i * 14
        if kind in ('maleF', 'femF', 'bridge'):
            cv.setFillColor(MALE_F if kind == 'maleF' else (FEM_F if kind == 'femF' else white))
            cv.setStrokeColor(BORDER)
            cv.setLineWidth(2.2 if kind == 'bridge' else 0.8)
            cv.roundRect(lx, yy - 5, 20, 10, 2, fill=1, stroke=1)
        elif kind in ('cousin', 'adopt', 'step'):
            cv.setStrokeColor(DASH if kind == 'cousin' else LINE)
            cv.setLineWidth(1.5 if kind == 'cousin' else 1.0)
            cv.setDash([5, 4] if kind == 'cousin' else ([3, 3] if kind == 'adopt' else [1, 2]))
            cv.line(lx, yy, lx + 20, yy)
            cv.setDash([])
        cv.setFillColor(HexColor('#222222'))
        cv.drawString(lx + 26, yy - 3, fa_text(t, lang))


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
