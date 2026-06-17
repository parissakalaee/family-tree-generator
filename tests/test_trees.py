from family_tree.trees import ALL, FamilyTree


def test_registry_not_empty():
    assert len(ALL) > 0


def test_known_trees_present():
    assert 'emma' in ALL
    assert 'lars' in ALL


def test_all_values_are_family_tree_instances():
    for tree in ALL.values():
        assert isinstance(tree, FamilyTree)


def test_slug_is_nonempty_string():
    for tree in ALL.values():
        assert isinstance(tree.SLUG, str)
        assert tree.SLUG


def test_make_pages_returns_nonempty_list():
    for lang in ('en', 'fa', 'nl'):
        pages = ALL['emma'].make_pages(lang)
        assert isinstance(pages, list)
        assert len(pages) >= 1


def test_make_pages_has_required_keys():
    for page in ALL['emma'].make_pages('en'):
        assert {'tree', 'title', 'subtitle', 'legend'} <= page.keys()


def test_make_pages_title_is_nonempty_string():
    for lang in ('en', 'fa', 'nl'):
        for page in ALL['emma'].make_pages(lang):
            assert isinstance(page['title'], str)
            assert page['title']


def test_make_pages_legend_is_list_of_tuples():
    for page in ALL['emma'].make_pages('en'):
        assert isinstance(page['legend'], list)
        for kind, label in page['legend']:
            assert isinstance(kind, str)
            assert isinstance(label, str)


def test_tree_nodes_are_normalized():
    def check(node: dict) -> None:
        assert isinstance(node['kids'], list)
        for k in node['kids']:
            check(k)

    for page in ALL['emma'].make_pages('en'):
        check(page['tree'])
