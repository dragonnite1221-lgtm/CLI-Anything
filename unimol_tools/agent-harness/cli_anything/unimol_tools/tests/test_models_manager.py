# ruff: noqa: F403, F405, E501
from .test_models_manager_helpers import *  # noqa: F403


class TestCalculateModelScore:
    """Test model scoring algorithm"""

    def test_auc_based_score(self):
        """Test 100% AUC-based scoring"""
        run = {
            "metrics": {"auc": 0.85},
            "duration_sec": 20,
            "timestamp": datetime.now().isoformat(),
        }

        score = calculate_model_score(run)
        assert score == 8.5  # AUC * 10

    def test_perfect_score(self):
        """Test perfect AUC gives perfect score"""
        run = {
            "metrics": {"auc": 1.0},
            "duration_sec": 20,
            "timestamp": datetime.now().isoformat(),
        }

        score = calculate_model_score(run)
        assert score == 10.0

    def test_poor_score(self):
        """Test poor AUC gives low score"""
        run = {
            "metrics": {"auc": 0.50},
            "duration_sec": 20,
            "timestamp": datetime.now().isoformat(),
        }

        score = calculate_model_score(run)
        assert score == 5.0

    def test_missing_auc_uses_auroc(self):
        """Test fallback to auroc if auc missing"""
        run = {
            "metrics": {"auroc": 0.88},
            "duration_sec": 20,
            "timestamp": datetime.now().isoformat(),
        }

        score = calculate_model_score(run)
        assert score == 8.8

    def test_missing_metrics(self):
        """Test handling of missing metrics"""
        run = {"duration_sec": 20, "timestamp": datetime.now().isoformat()}

        score = calculate_model_score(run)
        # Should default to 0.5 AUC
        assert score == 5.0

    def test_custom_weights(self):
        """Test custom weight configuration"""
        run = {
            "metrics": {"auc": 0.80},
            "duration_sec": 10,
            "timestamp": datetime.now().isoformat(),
        }

        # With time weight
        score = calculate_model_score(
            run, weight_auc=0.7, weight_time=0.3, weight_recency=0.0
        )

        # Should incorporate time component
        assert score != 8.0
        assert 0 <= score <= 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
