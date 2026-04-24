# tests/test_patients.py

from datetime import date

import pytest  # type: ignore[import]

import clinical.patients as patients


class FixedDate(date):
    @classmethod
    def today(cls) -> "FixedDate":
        return cls(2026, 4, 24)


def test_calculate_age_birthday_passed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(patients, "date", FixedDate)

    assert patients.calculate_age("1980-03-15") == 46


def test_calculate_age_birthday_not_passed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(patients, "date", FixedDate)

    assert patients.calculate_age("2000-06-05") == 25


def test_calculate_age_on_birthday(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(patients, "date", FixedDate)

    assert patients.calculate_age("2000-04-24") == 26


def test_calculate_age_invalid_date() -> None:
    with pytest.raises(ValueError):
        patients.calculate_age("not-a-date")
