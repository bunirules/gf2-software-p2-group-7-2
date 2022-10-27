import pytest

from names import Names
import builtins
import wx

builtins._ = wx.GetTranslation


@pytest.fixture
def new_names():
    """Return a new names instance."""
    return Names()


@pytest.fixture
def name_string_list():
    """Return a list of example names."""
    return ["Alice", "Bob", "Eve"]


@pytest.fixture
def used_names(name_string_list):
    """Return a names instance, after three names have been added."""
    name = Names()
    name.lookup(name_string_list)
    return name


def test_get_string_raises_exceptions(used_names):
    """Test if get_string raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.get_name_string(1.4)
    with pytest.raises(TypeError):
        used_names.get_name_string("hello")
    with pytest.raises(ValueError):
        used_names.get_name_string(-1)


def test_lookup_raises_exceptions(used_names):
    """Test if get_string raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.lookup(1.4)
    with pytest.raises(TypeError):
        used_names.lookup(1)


@pytest.mark.parametrize(
    "name_id, string", [(0, "Alice"), (1, "Bob"), (2, "Eve"), (3, None)]
)
def test_get_string(used_names, new_names, name_id, string):
    """Test if get_name_string returns the expected string."""
    # Name is present
    assert used_names.get_name_string(name_id) == string
    # Name is absent
    assert new_names.get_name_string(name_id) is None


@pytest.mark.parametrize(
    "name_id, string", [(0, "Alice"), (1, "Bob"), (2, "Eve")]
)
def test_query(used_names, new_names, name_id, string):
    """Test if query function returns the expected name ID"""
    # Name is present
    assert used_names.query(string) == name_id
    # Name is absent
    assert new_names.query("Robbie") is None


def test_lookup(name_string_list):
    name = Names()
    assert name.lookup(name_string_list) == [0, 1, 2]
