import pandas as pd
import pytest

from shift_suite.tasks.shortage import validate_and_cap_shortage


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame({"slot1": [1]}, index=[pd.Timestamp("2024-01-01")])


def test_non_dataframe_input():
    with pytest.raises(TypeError):
        validate_and_cap_shortage([], period_days=1, slot_hours=1)


def test_invalid_period_or_slot():
    df = _sample_df()
    with pytest.raises(ValueError):
        validate_and_cap_shortage(df, period_days=0, slot_hours=1)
    with pytest.raises(ValueError):
        validate_and_cap_shortage(df, period_days=1, slot_hours=0)

