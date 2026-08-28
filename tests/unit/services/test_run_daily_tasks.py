from unittest.mock import MagicMock, patch

from server.services.cron.daily_tasks import run_daily_tasks


def test_run_daily_tasks_runs_each_task_and_commits() -> None:
    """Uses a mocked Session/engine on purpose - run_daily_tasks opens its
    own session via server.db.engine (like middlewares.py's access-log
    persistence), which points at the real configured database rather than
    the test one, so it must never actually run against a live engine here."""
    mock_session = MagicMock()
    mock_session_cm = MagicMock()
    mock_session_cm.__enter__.return_value = mock_session
    mock_session_cm.__exit__.return_value = False

    fake_task = MagicMock()

    with (
        patch(
            "server.services.cron.daily_tasks.Session", return_value=mock_session_cm
        ),
        patch("server.services.cron.daily_tasks.DAILY_TASKS", [fake_task]),
    ):
        run_daily_tasks()

    fake_task.assert_called_once_with(mock_session)
    mock_session.commit.assert_called_once()
