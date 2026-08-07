"""Regression lock for a reported false-positive conflict bug: the frontend
showed a conflict for touching-but-not-overlapping bookings like
[14:00-16:00] vs [16:00-18:00]. These tests exercise the backend's sole
time-overlap primitive (`Occurrence.conflicts_with_time`/`conflicts_with`/
`conflicts_with_time_and_date`) directly, with no DB/session needed, to prove
it correctly treats touching boundaries as non-conflicting. See also
tests/api/authenticated/test_classroom_authenticated_routes.py, which drives
the same scenario through the actual `with-conflict-count` HTTP route.
"""

from datetime import date, time

import pytest

from server.models.database.occurrence_db_model import Occurrence


def make_occurrence(
    start_time: time,
    end_time: time,
    date_: date = date(2026, 1, 1),
    classroom_id: int | None = 1,
) -> Occurrence:
    return Occurrence(
        start_time=start_time, end_time=end_time, date=date_, classroom_id=classroom_id
    )


# Checked
@pytest.mark.parametrize(
    ("self_range", "other_range", "expected"),
    [
        pytest.param(
            (time(14, 0), time(16, 0)),
            (time(14, 0), time(16, 0)),
            True,
            id="identical-ranges",
        ),
        pytest.param(
            (time(14, 0), time(18, 0)),
            (time(15, 0), time(16, 0)),
            True,
            id="other-fully-inside-self",
        ),
        pytest.param(
            (time(15, 0), time(16, 0)),
            (time(14, 0), time(18, 0)),
            True,
            id="self-fully-inside-other",
        ),
        pytest.param(
            (time(14, 0), time(16, 0)),
            (time(13, 0), time(15, 0)),
            True,
            id="other-starts-before-ends-inside",
        ),
        pytest.param(
            (time(14, 0), time(16, 0)),
            (time(15, 0), time(17, 0)),
            True,
            id="other-starts-inside-ends-after",
        ),
        pytest.param(
            (time(14, 0), time(16, 0)),
            (time(16, 0), time(18, 0)),
            False,
            id="touching-boundary-reported-bug",
        ),
        pytest.param(
            (time(16, 0), time(18, 0)),
            (time(14, 0), time(16, 0)),
            False,
            id="touching-boundary-reversed",
        ),
        pytest.param(
            (time(14, 0), time(16, 0)),
            (time(12, 0), time(14, 0)),
            False,
            id="touching-boundary-before",
        ),
        pytest.param(
            (time(14, 0), time(16, 0)),
            (time(15, 55), time(17, 55)),
            True,
            id="near-miss-15h55-genuine-overlap",
        ),
        pytest.param(
            (time(14, 0), time(16, 0)),
            (time(15, 59), time(17, 59)),
            True,
            id="near-miss-15h59-genuine-overlap",
        ),
        pytest.param(
            (time(14, 0), time(16, 0)),
            (time(16, 1), time(18, 0)),
            False,
            id="just-past-boundary-no-overlap",
        ),
        pytest.param(
            (time(14, 0), time(16, 0)),
            (time(12, 0), time(13, 59)),
            False,
            id="just-before-boundary-no-overlap",
        ),
        pytest.param(
            (time(8, 0), time(9, 0)),
            (time(12, 0), time(13, 0)),
            False,
            id="large-gap-no-overlap",
        ),
        pytest.param(
            (time(14, 0), time(14, 0)),
            (time(14, 0), time(16, 0)),
            False,
            id="zero-width-interval-never-overlaps",
        ),
        pytest.param(
            (time(15, 0), time(16, 0)),
            (time(14, 0), time(18, 0)),
            True,
            id="commutativity-check",
        ),
    ],
)
def test_conflicts_with_time(
    self_range: tuple[time, time], other_range: tuple[time, time], expected: bool
) -> None:
    """`conflicts_with_time` is the sole overlap comparison in the codebase:
    `self.start_time < end_time and start_time < self.end_time`. It is a
    strict half-open-interval test, so two ranges that only touch at a
    boundary (one's end == the other's start) never conflict — this is what
    makes [14:00-16:00] vs [16:00-18:00] correctly non-conflicting.
    """
    occurrence = make_occurrence(*self_range)
    assert occurrence.conflicts_with_time(*other_range) is expected


# Checked
def test_conflicts_with_returns_true_for_same_date_classroom_and_overlap() -> None:
    self_occurrence = make_occurrence(time(14, 0), time(16, 0), classroom_id=1)
    other_occurrence = make_occurrence(time(15, 0), time(17, 0), classroom_id=1)
    assert self_occurrence.conflicts_with(other_occurrence) is True


# Checked
def test_conflicts_with_returns_false_for_touching_times() -> None:
    self_occurrence = make_occurrence(time(14, 0), time(16, 0), classroom_id=1)
    other_occurrence = make_occurrence(time(16, 0), time(18, 0), classroom_id=1)
    assert self_occurrence.conflicts_with(other_occurrence) is False


# Checked
def test_conflicts_with_returns_false_for_different_dates() -> None:
    self_occurrence = make_occurrence(
        time(14, 0), time(16, 0), date_=date(2026, 1, 1), classroom_id=1
    )
    other_occurrence = make_occurrence(
        time(14, 0), time(16, 0), date_=date(2026, 1, 2), classroom_id=1
    )
    assert self_occurrence.conflicts_with(other_occurrence) is False


# Checked
def test_conflicts_with_returns_false_for_different_classrooms() -> None:
    self_occurrence = make_occurrence(time(14, 0), time(16, 0), classroom_id=1)
    other_occurrence = make_occurrence(time(14, 0), time(16, 0), classroom_id=2)
    assert self_occurrence.conflicts_with(other_occurrence) is False


# Checked
def test_conflicts_with_returns_false_when_one_side_has_no_classroom() -> None:
    self_occurrence = make_occurrence(time(14, 0), time(16, 0), classroom_id=None)
    other_occurrence = make_occurrence(time(14, 0), time(16, 0), classroom_id=1)
    assert self_occurrence.conflicts_with(other_occurrence) is False


# Checked
def test_conflicts_with_treats_both_unassigned_as_matching_classroom() -> None:
    """Existing behavior, not something changed by this test: `classroom_id`
    is compared with plain equality, so two occurrences that are both
    unallocated (`classroom_id=None`) register as sharing a "classroom" and
    do conflict if their times overlap. Documented here rather than silently
    assumed — not a bug this task is meant to fix.
    """
    self_occurrence = make_occurrence(time(14, 0), time(16, 0), classroom_id=None)
    other_occurrence = make_occurrence(time(15, 0), time(17, 0), classroom_id=None)
    assert self_occurrence.conflicts_with(other_occurrence) is True


# Checked
def test_conflicts_with_time_and_date_returns_true_for_same_date_and_overlap() -> None:
    occurrence = make_occurrence(time(14, 0), time(16, 0), date_=date(2026, 1, 1))
    assert (
        occurrence.conflicts_with_time_and_date(
            time(15, 0), time(17, 0), date(2026, 1, 1)
        )
        is True
    )


# Checked
def test_conflicts_with_time_and_date_returns_false_for_touching_times() -> None:
    occurrence = make_occurrence(time(14, 0), time(16, 0), date_=date(2026, 1, 1))
    assert (
        occurrence.conflicts_with_time_and_date(
            time(16, 0), time(18, 0), date(2026, 1, 1)
        )
        is False
    )


# Checked
def test_conflicts_with_time_and_date_returns_false_for_different_date() -> None:
    occurrence = make_occurrence(time(14, 0), time(16, 0), date_=date(2026, 1, 1))
    assert (
        occurrence.conflicts_with_time_and_date(
            time(14, 0), time(16, 0), date(2026, 1, 2)
        )
        is False
    )


# Checked
def test_conflicts_with_time_and_date_returns_false_for_non_overlapping_time() -> None:
    occurrence = make_occurrence(time(14, 0), time(16, 0), date_=date(2026, 1, 1))
    assert (
        occurrence.conflicts_with_time_and_date(
            time(8, 0), time(9, 0), date(2026, 1, 1)
        )
        is False
    )


# No cross-midnight cases: `Occurrence` pairs a `time` with a separate `date`
# column, so a class spanning midnight (e.g. 23:00-01:00) isn't representable
# by this schema at all — out of scope because the model doesn't support it,
# not because it was overlooked.
