"""Family-tree definitions.

Each family lives in a YAML data file under ``family_tree/data/trees/``.
This module loads those files and exposes them through the registry ``ALL``,
mapping ``name -> FamilyTree``. Every FamilyTree provides ``SLUG`` and
``make_pages(lang)``, the same interface the CLI consumes.

To add a new family: drop a ``<name>.yaml`` next to the others (see the header
of ``emma.yaml`` for the schema) — it is picked up automatically.
"""

from typing import Any

import yaml
from importlib.resources import files

from family_tree.translations import t_ui, t_name, star_suffix
from family_tree.drawing import legend_basic, legend_with_cousin

# Auto-discover all YAML files in the trees data directory.
_NAMES = tuple(
    p.stem
    for p in files('family_tree').joinpath('data', 'trees').iterdir()
    if p.name.endswith('.yaml')
)

# Page `legend:` value -> builder in drawing.py.
_LEGENDS = {'basic': legend_basic, 'cousin': legend_with_cousin}


def _normalize(node: dict[str, Any]) -> dict[str, Any]:
    """Ensure every node has a ``kids`` list, recursively (leaves omit it)."""
    node['kids'] = node.get('kids') or []
    for kid in node['kids']:
        _normalize(kid)
    return node


class FamilyTree:
    """A family loaded from YAML, rendered to PDF pages per language."""

    SLUG: str
    _pages: list[dict[str, Any]]

    def __init__(self, spec: dict[str, Any]) -> None:
        self.SLUG = spec['slug']
        self._pages = spec['pages']
        for page in self._pages:
            _normalize(page['tree'])

    def make_pages(self, lang: str) -> list[dict[str, Any]]:
        pages: list[dict[str, Any]] = []
        for pg in self._pages:
            legend = _LEGENDS[pg.get('legend', 'basic')](
                lang, with_step=pg.get('steps', False)
            )
            page = {
                'tree':     pg['tree'],
                'title':    t_ui(pg['title'], lang),
                'subtitle': t_ui(pg['subtitle'], lang)
                            + star_suffix(lang)
                            + t_name(pg['star_person'], lang),
                'legend':   legend,
            }
            if pg.get('cousin_link'):
                page['cousin_link'] = tuple(pg['cousin_link'])
            pages.append(page)
        return pages


def _load(name: str) -> FamilyTree:
    path = files('family_tree').joinpath('data', 'trees', f'{name}.yaml')
    with path.open(encoding='utf-8') as f:
        return FamilyTree(yaml.safe_load(f))


# Registry used by the CLI: name -> FamilyTree.
ALL = {name: _load(name) for name in _NAMES}
