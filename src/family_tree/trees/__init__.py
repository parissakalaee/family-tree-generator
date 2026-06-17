"""Family-tree definitions.

Each family lives in a YAML data file under ``family_tree/data/trees/``.
This module loads those files and exposes them through the registry ``ALL``,
mapping ``name -> FamilyTree``. Every FamilyTree provides ``SLUG`` and
``make_pages(lang)``, the same interface the CLI consumes.

To add a new family: drop a ``<name>.yaml`` next to the others (see the header
of ``parissa.yaml`` for the schema) and add its name to ``_NAMES`` below.
"""

import yaml
from importlib.resources import files

from family_tree.render import (
    t_ui, t_name, star_suffix, legend_basic, legend_with_cousin,
)

# Families to load. The name is what you type on the CLI: ``family-tree saber``.
_NAMES = ('parissa', 'saber')

# Page `legend:` value -> builder in render.py.
_LEGENDS = {'basic': legend_basic, 'cousin': legend_with_cousin}


def _normalize(node):
    """Ensure every node has a ``kids`` list, recursively (leaves omit it)."""
    node['kids'] = node.get('kids') or []
    for kid in node['kids']:
        _normalize(kid)
    return node


class FamilyTree:
    """A family loaded from YAML, rendered to PDF pages per language."""

    def __init__(self, spec):
        self.SLUG = spec['slug']
        self._pages = spec['pages']
        for page in self._pages:
            _normalize(page['tree'])

    def make_pages(self, lang):
        pages = []
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


def _load(name):
    path = files('family_tree').joinpath('data', 'trees', f'{name}.yaml')
    with path.open(encoding='utf-8') as f:
        return FamilyTree(yaml.safe_load(f))


# Registry used by the CLI: name -> FamilyTree.
ALL = {name: _load(name) for name in _NAMES}
