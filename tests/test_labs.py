# tests/test_labs.py

from clinical.labs import get_reference_range, is_abnormal


def test_is_abnormal_false_for_normal_value() -> None:
    assert is_abnormal("glucose", 95.0) is False


def test_is_abnormal_true_for_high_value() -> None:
    assert is_abnormal("glucose", 210.0) is True


def test_is_abnormal_true_for_low_value() -> None:
    assert is_abnormal("glucose", 58.0) is True


def test_is_abnormal_inclusive_lower_boundary() -> None:
    assert is_abnormal("glucose", 70.0) is False


def test_is_abnormal_inclusive_upper_boundary() -> None:
    assert is_abnormal("glucose", 99.0) is False


def test_is_abnormal_case_insensitive_and_strips_spaces() -> None:
    assert is_abnormal("  GLUCOSE  ", 95.0) is False


def test_is_abnormal_unknown_lab_raises_value_error() -> None:
    try:
        is_abnormal("unknown_test", 100.0)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_get_reference_range_known_lab() -> None:
    ref = get_reference_range("glucose")

    assert ref is not None
    assert ref.low == 70.0
    assert ref.high == 99.0


def test_get_reference_range_unknown_lab() -> None:
    assert get_reference_range("unknown_test") is None
