import pytest

from src.features import RF_FEATURES, assert_no_leakage


def test_approved_rf_features_have_no_leakage():
    assert_no_leakage(RF_FEATURES, "RF_FEATURES")


def test_label_component_is_rejected():
    with pytest.raises(ValueError):
        assert_no_leakage(["energy_kcal", "hba1c"], "bad X")

