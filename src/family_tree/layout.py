# Geometry constants (points)
ROW_H = 40
COL_W = 180
BOX_W = 150
BOX_UNIFORM = 36
MARGIN_X = 40
MARGIN_TOP = 100
MARGIN_BOT = 45


def P(name, g, sp=None, sp2=None, kids=None, **kw):
    d = {'name': name, 'g': g, 'sp': sp, 'sp2': sp2, 'kids': kids or []}
    d.update(kw)
    return d


def assign_layout(node, depth, cursor):
    node['depth'] = depth
    if node['kids']:
        for k in node['kids']:
            assign_layout(k, depth + 1, cursor)
        node['y'] = (node['kids'][0]['y'] + node['kids'][-1]['y']) / 2
    else:
        node['y'] = cursor[0]
        cursor[0] += ROW_H
    node['x'] = MARGIN_X + depth * COL_W


def count_leaves(n):
    return 1 if not n['kids'] else sum(count_leaves(k) for k in n['kids'])


def max_depth(n):
    return n['depth'] if not n['kids'] else max(max_depth(k) for k in n['kids'])


def find(n, name, depth=None):
    if n['name'] == name and (depth is None or n['depth'] == depth):
        return n
    for k in n['kids']:
        r = find(k, name, depth)
        if r:
            return r
    return None


def page_size(tree):
    """Natural (width, height) the tree needs. Also assigns x/y/depth on nodes."""
    cursor = [MARGIN_TOP]
    assign_layout(tree, 0, cursor)
    pw = MARGIN_X * 2 + (max_depth(tree) + 1) * COL_W
    ph = MARGIN_TOP + count_leaves(tree) * ROW_H + MARGIN_BOT
    return pw, ph
