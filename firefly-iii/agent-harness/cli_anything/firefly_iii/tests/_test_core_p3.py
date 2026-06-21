# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestValidation:
    """Test input validation"""

    def test_date_format(self):
        """Test date format validation"""
        valid_date = "2024-01-15"
        try:
            datetime.strptime(valid_date, "%Y-%m-%d")
            assert True
        except ValueError:
            assert False

    def test_invalid_date_format(self):
        """Test invalid date format"""
        invalid_date = "01-15-2024"
        with pytest.raises(ValueError):
            datetime.strptime(invalid_date, "%Y-%m-%d")

    def test_amount_format(self):
        """Test amount format"""
        valid_amounts = ["100.00", "50.5", "0.01", "1000"]
        for amount in valid_amounts:
            try:
                float(amount)
                assert True
            except ValueError:
                assert False
