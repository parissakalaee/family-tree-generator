from pathlib import Path

from family_tree.cli import main


def test_single_tree_single_lang(tmp_path: Path):
    main(['emma', '--lang', 'en', '--out', str(tmp_path)])
    assert (tmp_path / 'emma' / 'en' / 'emma_family_tree_en.pdf').exists()


def test_all_languages_generated(tmp_path: Path):
    main(['lars', '--out', str(tmp_path)])
    for lang in ('en', 'fa', 'nl'):
        assert (tmp_path / 'lars' / lang / f'lars_family_tree_{lang}.pdf').exists()


def test_print_flag_produces_a4_pdf(tmp_path: Path):
    main(['emma', '--lang', 'en', '--out', str(tmp_path), '--print'])
    assert (tmp_path / 'emma' / 'en' / 'emma_family_tree_en_a4.pdf').exists()


def test_output_directory_is_created(tmp_path: Path):
    out = tmp_path / 'nested' / 'dir'
    main(['emma', '--lang', 'en', '--out', str(out)])
    assert out.is_dir()
