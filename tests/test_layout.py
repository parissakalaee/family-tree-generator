from family_tree.layout import (
    COL_W,
    MARGIN_BOT,
    MARGIN_TOP,
    MARGIN_X,
    ROW_H,
    assign_layout,
    count_leaves,
    find,
    max_depth,
    page_size,
    person,
)


def test_person_builds_node():
    n = person('Alice', 'f')
    assert n['name'] == 'Alice'
    assert n['g'] == 'f'
    assert n['sp'] is None
    assert n['sp2'] is None
    assert n['kids'] == []


def test_person_with_spouse_and_kids():
    child = person('Bob', 'm')
    n = person('Alice', 'f', sp='Charlie', kids=[child])
    assert n['sp'] == 'Charlie'
    assert n['kids'] == [child]


def test_person_extra_flags():
    n = person('Alice', 'f', star=True, root=True)
    assert n['star'] is True
    assert n['root'] is True


def test_count_leaves_single_node():
    assert count_leaves(person('A', 'f')) == 1


def test_count_leaves_two_children():
    n = person('A', 'f', kids=[person('B', 'm'), person('C', 'f')])
    assert count_leaves(n) == 2


def test_count_leaves_nested():
    root = person('A', 'f', kids=[person('B', 'm', kids=[person('C', 'f')])])
    assert count_leaves(root) == 1


def test_assign_layout_sets_depth_and_position():
    n = person('A', 'f')
    assign_layout(n, 0, [MARGIN_TOP])
    assert n['depth'] == 0
    assert n['x'] == MARGIN_X
    assert n['y'] == MARGIN_TOP


def test_assign_layout_child_is_one_column_deeper():
    child = person('B', 'm')
    root = person('A', 'f', kids=[child])
    assign_layout(root, 0, [MARGIN_TOP])
    assert child['depth'] == 1
    assert child['x'] == MARGIN_X + COL_W


def test_assign_layout_parent_y_is_midpoint_of_children():
    c1, c2 = person('B', 'm'), person('C', 'f')
    root = person('A', 'f', kids=[c1, c2])
    assign_layout(root, 0, [MARGIN_TOP])
    assert root['y'] == (c1['y'] + c2['y']) / 2


def test_max_depth_leaf():
    n = person('A', 'f')
    assign_layout(n, 0, [0.0])
    assert max_depth(n) == 0


def test_max_depth_two_levels():
    root = person('A', 'f', kids=[person('B', 'm')])
    assign_layout(root, 0, [0.0])
    assert max_depth(root) == 1


def test_find_root_node():
    n = person('Alice', 'f')
    assert find(n, 'Alice') is n


def test_find_child_node():
    child = person('Bob', 'm')
    root = person('Alice', 'f', kids=[child])
    assert find(root, 'Bob') is child


def test_find_missing_returns_none():
    assert find(person('Alice', 'f'), 'Nobody') is None


def test_page_size_single_node():
    pw, ph = page_size(person('A', 'f'))
    assert pw == MARGIN_X * 2 + COL_W
    assert ph == MARGIN_TOP + ROW_H + MARGIN_BOT


def test_page_size_grows_with_depth():
    pw_single, _ = page_size(person('A', 'f'))
    pw_deep, _ = page_size(person('A', 'f', kids=[person('B', 'm')]))
    assert pw_deep > pw_single


def test_page_size_grows_with_leaves():
    _, ph_single = page_size(person('A', 'f'))
    _, ph_wide = page_size(person('A', 'f', kids=[person('B', 'm'), person('C', 'f')]))
    assert ph_wide > ph_single
