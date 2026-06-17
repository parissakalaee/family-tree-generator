from pathlib import Path
from typing import Any

from family_tree.drawing import legend_basic
from family_tree.layout import person
from family_tree.render import A4, A4_LANDSCAPE, build_pdf, plan_tiles


def _page(lang: str = 'en') -> dict[str, Any]:
    return {
        'tree': person('Alice', 'f'),
        'title': 'Test Tree',
        'subtitle': 'Subtitle',
        'legend': legend_basic(lang),
    }


def test_plan_tiles_returns_positive_values():
    cols, rows, scale = plan_tiles(400.0, 500.0, A4)
    assert cols >= 1
    assert rows >= 1
    assert scale > 0


def test_plan_tiles_scale_fills_page_width():
    cols, rows, scale = plan_tiles(400.0, 500.0, A4)
    assert abs(scale * 400.0 - A4[0] * cols) < 1.0


def test_plan_tiles_tall_tree_spans_multiple_rows():
    _, rows, _ = plan_tiles(400.0, 5000.0, A4)
    assert rows > 1


def test_plan_tiles_forced_cols_increases_scale():
    _, _, scale_auto = plan_tiles(400.0, 500.0, A4)
    _, _, scale_two = plan_tiles(400.0, 500.0, A4, cols=2)
    assert scale_two > scale_auto


def test_build_pdf_creates_file(tmp_path: Path):
    out = tmp_path / 'test.pdf'
    build_pdf([_page()], str(out), 'en')
    assert out.exists()
    assert out.stat().st_size > 0


def test_build_pdf_persian(tmp_path: Path):
    out = tmp_path / 'test_fa.pdf'
    build_pdf([_page('fa')], str(out), 'fa')
    assert out.exists()
    assert out.stat().st_size > 0


def test_build_pdf_a4_tiled(tmp_path: Path):
    out = tmp_path / 'test_a4.pdf'
    build_pdf([_page()], str(out), 'en', paper=A4_LANDSCAPE)
    assert out.exists()
    assert out.stat().st_size > 0


def test_build_pdf_multipage(tmp_path: Path):
    out = tmp_path / 'multi.pdf'
    build_pdf([_page(), _page()], str(out), 'en')
    assert out.exists()
