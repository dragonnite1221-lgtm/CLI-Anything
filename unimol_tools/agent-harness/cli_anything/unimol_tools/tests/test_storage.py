# ruff: noqa: F403, F405, E501
from .test_storage_helpers import *  # noqa: F403


class TestFormatSize:
    """Test size formatting"""

    def test_format_bytes(self):
        assert format_size(512) == "512.0B"

    def test_format_kilobytes(self):
        assert format_size(1024) == "1.0KB"
        assert format_size(1536) == "1.5KB"

    def test_format_megabytes(self):
        assert format_size(1024 * 1024) == "1.0MB"
        assert format_size(1024 * 1024 * 2.5) == "2.5MB"

    def test_format_gigabytes(self):
        assert format_size(1024 * 1024 * 1024) == "1.0GB"

    def test_zero_size(self):
        assert format_size(0) == "0.0B"


class TestGetDirectorySize:
    """Test directory size calculation"""

    def test_empty_directory(self, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        assert get_directory_size(str(empty_dir)) == 0

    def test_directory_with_files(self, tmp_path):
        test_dir = tmp_path / "test"
        test_dir.mkdir()

        # Create 10KB file
        (test_dir / "file1.txt").write_bytes(b"0" * 10240)

        size = get_directory_size(str(test_dir))
        assert size == 10240

    def test_nested_directories(self, tmp_path):
        parent = tmp_path / "parent"
        parent.mkdir()
        child = parent / "child"
        child.mkdir()

        (parent / "file1.txt").write_bytes(b"0" * 5000)
        (child / "file2.txt").write_bytes(b"0" * 3000)

        total_size = get_directory_size(str(parent))
        assert total_size == 8000

    def test_nonexistent_directory(self):
        size = get_directory_size("/nonexistent/path")
        assert size == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
