"""
Font handling for the PDF renderer.

Persian text is drawn with the bundled **Vazirmatn** font (SIL OFL licensed,
see assets/fonts/OFL.txt) so the project renders identically on any machine
without a system font install. English uses ReportLab's built-in Helvetica.

To use a different Persian font (e.g. Nazli), point the FAMILY_TREE_FONT_DIR
environment variable at a directory containing files named
``Vazirmatn-Regular.ttf`` and ``Vazirmatn-Bold.ttf``.
"""

import os
from importlib.resources import files

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Registered font names used throughout the renderer, keyed by language.
FONT_REG = {'fa': 'Vazir', 'en': 'Helvetica', 'nl': 'Helvetica'}
FONT_BOLD = {'fa': 'VazirBold', 'en': 'Helvetica-Bold', 'nl': 'Helvetica-Bold'}
FONT_SUB = {'fa': 'Vazir', 'en': 'Helvetica-Oblique', 'nl': 'Helvetica-Oblique'}
FONT_SUB_SIZE = {'fa': 7.5, 'en': 7.0, 'nl': 7.0}
FONT_COUSIN_LABEL = {'fa': 'VazirBold', 'en': 'Helvetica-BoldOblique', 'nl': 'Helvetica-BoldOblique'}
STAR = {'fa': '*', 'en': '★', 'nl': '★'}  # Vazirmatn has no star glyph, so use *

_registered = False


def _font_path(filename: str) -> str:
    """Resolve a font file from FAMILY_TREE_FONT_DIR, else the bundled assets."""
    override = os.environ.get('FAMILY_TREE_FONT_DIR')
    if override:
        return os.path.join(override, filename)
    return str(files('family_tree').joinpath('assets', 'fonts', filename))


def register_fonts() -> None:
    """Register the Persian TTF fonts with ReportLab (idempotent)."""
    global _registered
    if _registered:
        return
    pdfmetrics.registerFont(TTFont('Vazir', _font_path('Vazirmatn-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('VazirBold', _font_path('Vazirmatn-Bold.ttf')))
    _registered = True
