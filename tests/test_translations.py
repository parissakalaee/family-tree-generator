from family_tree.translations import fa_text, star_suffix, t_name, t_ui


def test_t_name_unknown_key_returns_key():
    assert t_name('__no_such_key__', 'en') == '__no_such_key__'


def test_t_ui_unknown_key_returns_key():
    assert t_ui('__no_such_key__', 'en') == '__no_such_key__'


def test_t_ui_known_key_returns_nonempty_string():
    for lang in ('en', 'fa', 'nl'):
        result = t_ui('legend_male', lang)
        assert isinstance(result, str)
        assert result


def test_t_ui_unknown_lang_falls_back_to_english():
    assert t_ui('legend_male', 'xx') == t_ui('legend_male', 'en')


def test_fa_text_noop_for_english():
    assert fa_text('hello', 'en') == 'hello'


def test_fa_text_noop_for_dutch():
    assert fa_text('hallo', 'nl') == 'hallo'


def test_fa_text_noop_for_empty_string():
    assert fa_text('', 'fa') == ''


def test_fa_text_processes_persian():
    result = fa_text('سلام', 'fa')
    assert isinstance(result, str)
    assert result


def test_star_suffix_persian_uses_asterisk():
    assert '*' in star_suffix('fa')


def test_star_suffix_latin_uses_star_glyph():
    assert '★' in star_suffix('en')
    assert '★' in star_suffix('nl')


def test_star_suffix_format():
    for lang in ('en', 'fa', 'nl'):
        s = star_suffix(lang)
        assert '|' in s
        assert s.endswith('= ')
