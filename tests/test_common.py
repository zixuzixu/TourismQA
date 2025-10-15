"""
Tests for utils/common.py utilities
"""
import json
import pickle
import pytest
from pathlib import Path
from utils import common


class TestProjectRootPath:
    """Tests for getProjectRootPath function"""

    def test_returns_path_object(self):
        """Test that function returns a Path object"""
        result = common.getProjectRootPath()
        assert isinstance(result, Path)

    def test_path_exists(self):
        """Test that returned path exists"""
        result = common.getProjectRootPath()
        assert result.exists()

    def test_path_contains_utils(self):
        """Test that project root contains utils directory"""
        root = common.getProjectRootPath()
        assert (root / "utils").exists()


class TestCreate:
    """Tests for create function"""

    def test_creates_directory(self, temp_dir):
        """Test that create function creates a directory"""
        new_dir = temp_dir / "test" / "nested" / "dir"
        common.create(new_dir)
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_creates_parent_directories(self, temp_dir):
        """Test that create function creates parent directories"""
        new_dir = temp_dir / "a" / "b" / "c"
        common.create(new_dir)
        assert (temp_dir / "a").exists()
        assert (temp_dir / "a" / "b").exists()
        assert new_dir.exists()

    def test_does_not_fail_if_exists(self, temp_dir):
        """Test that create function doesn't fail if directory exists"""
        new_dir = temp_dir / "existing"
        new_dir.mkdir()
        common.create(new_dir)  # Should not raise exception
        assert new_dir.exists()


class TestLoadJSON:
    """Tests for loadJSON function"""

    def test_loads_json_file(self, sample_json_file):
        """Test that loadJSON loads a JSON file"""
        result = common.loadJSON(sample_json_file)
        assert result["test"] == "data"
        assert result["items"] == [1, 2, 3]

    def test_handles_unicode(self, temp_dir):
        """Test that loadJSON handles unicode characters"""
        data = {"text": "Hello 世界 🌍"}
        file_path = temp_dir / "unicode.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        result = common.loadJSON(file_path)
        assert result["text"] == "Hello 世界 🌍"

    def test_raises_error_for_nonexistent_file(self, temp_dir):
        """Test that loadJSON raises error for nonexistent file"""
        with pytest.raises(FileNotFoundError):
            common.loadJSON(temp_dir / "nonexistent.json")


class TestDumpJSON:
    """Tests for dumpJSON function"""

    def test_writes_json_file(self, temp_dir):
        """Test that dumpJSON writes a JSON file"""
        data = {"key": "value", "number": 42}
        file_path = temp_dir / "output.json"

        common.dumpJSON(data, file_path)

        assert file_path.exists()
        with open(file_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        assert loaded == data

    def test_creates_parent_directories(self, temp_dir):
        """Test that dumpJSON creates parent directories"""
        data = {"test": "data"}
        file_path = temp_dir / "nested" / "deep" / "file.json"

        common.dumpJSON(data, file_path)

        assert file_path.exists()
        assert file_path.parent.exists()

    def test_formats_with_indent(self, temp_dir):
        """Test that dumpJSON formats with indentation"""
        data = {"key": "value"}
        file_path = temp_dir / "formatted.json"

        common.dumpJSON(data, file_path)

        with open(file_path, "r") as f:
            content = f.read()
        assert "\n" in content  # Has newlines (formatted)
        assert "    " in content  # Has indentation

    def test_sorts_keys_when_requested(self, temp_dir):
        """Test that dumpJSON sorts keys when sort_keys=True"""
        data = {"z": 1, "a": 2, "m": 3}
        file_path = temp_dir / "sorted.json"

        common.dumpJSON(data, file_path, sort_keys=True)

        with open(file_path, "r") as f:
            content = f.read()
        # Check that 'a' appears before 'z' in the file
        assert content.index('"a"') < content.index('"z"')

    def test_preserves_unicode(self, temp_dir):
        """Test that dumpJSON preserves unicode characters"""
        data = {"text": "Hello 世界 🌍"}
        file_path = temp_dir / "unicode.json"

        common.dumpJSON(data, file_path)

        loaded = common.loadJSON(file_path)
        assert loaded["text"] == "Hello 世界 🌍"


class TestDumpPickle:
    """Tests for dumpPickle function"""

    def test_writes_pickle_file(self, temp_dir):
        """Test that dumpPickle writes a pickle file"""
        data = {"key": "value", "list": [1, 2, 3]}
        file_path = temp_dir / "data.pkl"

        common.dumpPickle(data, file_path)

        assert file_path.exists()
        with open(file_path, "rb") as f:
            loaded = pickle.load(f)
        assert loaded == data

    def test_creates_parent_directories(self, temp_dir):
        """Test that dumpPickle creates parent directories"""
        data = {"test": "data"}
        file_path = temp_dir / "nested" / "data.pkl"

        common.dumpPickle(data, file_path)

        assert file_path.exists()
        assert file_path.parent.exists()


class TestUpdate:
    """Tests for update function"""

    def test_updates_simple_values(self):
        """Test that update updates simple values"""
        d = {"a": 1, "b": 2}
        u = {"b": 3, "c": 4}
        result = common.update(d, u)
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_updates_nested_dicts(self):
        """Test that update handles nested dictionaries"""
        d = {"a": {"x": 1, "y": 2}}
        u = {"a": {"y": 3, "z": 4}}
        result = common.update(d, u)
        assert result == {"a": {"x": 1, "y": 3, "z": 4}}

    def test_appends_to_lists(self):
        """Test that update appends unique items to lists"""
        d = {"items": [1, 2, 3]}
        u = {"items": [3, 4, 5]}
        result = common.update(d, u)
        assert result == {"items": [1, 2, 3, 4, 5]}

    def test_does_not_duplicate_list_items(self):
        """Test that update doesn't duplicate existing list items"""
        d = {"items": [1, 2, 3]}
        u = {"items": [2, 3]}
        result = common.update(d, u)
        assert result == {"items": [1, 2, 3]}

    def test_complex_nested_update(self):
        """Test update with complex nested structure"""
        d = {
            "a": {"x": 1},
            "b": [1, 2],
            "c": 3
        }
        u = {
            "a": {"y": 2},
            "b": [3, 4],
            "d": 5
        }
        result = common.update(d, u)
        assert result == {
            "a": {"x": 1, "y": 2},
            "b": [1, 2, 3, 4],
            "c": 3,
            "d": 5
        }
