import warnings

import pandas as pd

from app.data_profiler_type_inference import infer_type, sample_values


def test_type_inference_detects_numeric_columns():
    series = pd.Series(["10", "20", "30", "40"])
    assert infer_type(series) == "numeric"


def test_type_inference_detects_date_columns_without_user_warnings():
    series = pd.Series(["01/02/2026", "15/02/2026", "28/02/2026"])

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        inferred = infer_type(series)

    assert inferred == "date"
    assert [warning for warning in caught if issubclass(warning.category, UserWarning)] == []


def test_type_inference_does_not_treat_mixed_operational_text_as_date():
    series = pd.Series(["Q1 2026", "not confirmed", "pending review"])
    assert infer_type(series) != "date"


def test_sample_values_skips_empty_like_values_and_preserves_order():
    series = pd.Series(["", "Steel", "nan", "Steel", "Plastic", None, "null", "Glass"])
    assert sample_values(series) == ["Steel", "Plastic", "Glass"]
