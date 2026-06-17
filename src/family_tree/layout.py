from typing import Any

# Geometry constants (points)
ROW_H: int = 40
COL_W: int = 180
BOX_W: int = 150
BOX_UNIFORM: int = 36
MARGIN_X: int = 40
MARGIN_TOP: int = 100
MARGIN_BOT: int = 45


def person(name: str, g: str, sp: str | None = None, sp2: str | None = None,
           kids: list[dict[str, Any]] | None = None, **kw: Any) -> dict[str, Any]:
    d = {'name': name, 'g': g, 'sp': sp, 'sp2': sp2, 'kids': kids or []}
    d.update(kw)
    return d


def assign_layout(node: dict[str, Any], depth: int, cursor: list[float]) -> None:
    node['depth'] = depth
    if node['kids']:
        for k in node['kids']:
            assign_layout(k, depth + 1, cursor)
        node['y'] = (node['kids'][0]['y'] + node['kids'][-1]['y']) / 2
    else:
        node['y'] = cursor[0]
        cursor[0] += ROW_H
    node['x'] = MARGIN_X + depth * COL_W


def count_leaves(n: dict[str, Any]) -> int:
    return 1 if not n['kids'] else sum(count_leaves(k) for k in n['kids'])


def max_depth(n: dict[str, Any]) -> int:
    return n['depth'] if not n['kids'] else max(max_depth(k) for k in n['kids'])


def find(n: dict[str, Any], name: str, depth: int | None = None) -> dict[str, Any] | None:
    if n['name'] == name and (depth is None or n['depth'] == depth):
        return n
    for k in n['kids']:
        r = find(k, name, depth)
        if r:
            return r
    return None


def page_size(tree: dict[str, Any]) -> tuple[float, float]:
    """Natural (width, height) the tree needs. Also assigns x/y/depth on nodes."""
    cursor = [MARGIN_TOP]
    assign_layout(tree, 0, cursor)
    pw = MARGIN_X * 2 + (max_depth(tree) + 1) * COL_W
    ph = MARGIN_TOP + count_leaves(tree) * ROW_H + MARGIN_BOT
    return pw, ph
