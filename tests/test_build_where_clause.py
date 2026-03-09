"""Unit tests for build_where_clause helper function."""

from api.routes.reports import build_where_clause


def test_no_filters_returns_empty():
    """No filters produces empty WHERE clause and empty params."""
    where_sql, params = build_where_clause(None, None, None, None)
    assert where_sql == ""
    assert params == []


def test_single_filter_area():
    """Single area filter produces correct WHERE clause."""
    where_sql, params = build_where_clause(area="IT", initiative=None, status=None, owner=None)
    assert where_sql == "WHERE area = ?"
    assert params == ["IT"]


def test_single_filter_initiative():
    where_sql, params = build_where_clause(area=None, initiative="Deep", status=None, owner=None)
    assert where_sql == "WHERE initiative = ?"
    assert params == ["Deep"]


def test_single_filter_status():
    where_sql, params = build_where_clause(area=None, initiative=None, status="active", owner=None)
    assert where_sql == "WHERE status = ?"
    assert params == ["active"]


def test_single_filter_owner():
    where_sql, params = build_where_clause(area=None, initiative=None, status=None, owner="Ana")
    assert where_sql == "WHERE owner = ?"
    assert params == ["Ana"]


def test_two_filters():
    """Two filters are joined with AND."""
    where_sql, params = build_where_clause(area="IT", initiative=None, status="active", owner=None)
    assert where_sql == "WHERE area = ? AND status = ?"
    assert params == ["IT", "active"]


def test_all_filters():
    """All four filters produce a full WHERE clause."""
    where_sql, params = build_where_clause(area="IT", initiative="Deep", status="active", owner="Ana")
    assert where_sql == "WHERE area = ? AND initiative = ? AND status = ? AND owner = ?"
    assert params == ["IT", "Deep", "active", "Ana"]


def test_empty_string_treated_as_no_filter():
    """Empty strings are falsy and should not produce conditions."""
    where_sql, params = build_where_clause(area="", initiative="", status="", owner="")
    assert where_sql == ""
    assert params == []


def test_returns_tuple_of_str_and_list():
    """Return type is always (str, list)."""
    result = build_where_clause(None, None, None, None)
    assert isinstance(result, tuple)
    assert isinstance(result[0], str)
    assert isinstance(result[1], list)
