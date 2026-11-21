import logging
import multiprocessing
import queue
from pathlib import Path

import pytest

from server.logger import DroppingQueueHandler, LockedRotatingFileHandler, QueuedLogger

LINES_PER_PROCESS = 400
PROCESSES = 4
MAX_BYTES = 4096


def make_record(message: str) -> logging.LogRecord:
    return logging.LogRecord("test", logging.INFO, __file__, 0, message, None, None)


def _write_lines(path: str, worker: int) -> None:
    # Like a gunicorn worker: its own handler on the shared file.
    handler = LockedRotatingFileHandler(path, max_bytes=MAX_BYTES, backup_count=1000)
    handler.setFormatter(logging.Formatter("%(message)s"))
    for i in range(LINES_PER_PROCESS):
        handler.handle(make_record(f"worker={worker} line={i:04d} " + "x" * 40))
    handler.close()


class TestLockedRotatingFileHandler:
    # Forking with the app's log listener threads running is what
    # register_at_fork in server/logger.py handles.
    @pytest.mark.filterwarnings("ignore:This process .* is multi-threaded")
    def test_processes_sharing_a_file_lose_no_line_and_rotate_once_each_time(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "api.log"
        context = multiprocessing.get_context("fork")
        processes = [
            context.Process(target=_write_lines, args=(str(path), worker))
            for worker in range(PROCESSES)
        ]
        for process in processes:
            process.start()
        for process in processes:
            process.join(timeout=60)
            assert process.exitcode == 0

        files = [p for p in tmp_path.iterdir() if not p.name.endswith(".lock")]
        lines = [line for f in files for line in f.read_text().splitlines()]
        assert len(lines) == PROCESSES * LINES_PER_PROCESS
        assert len(set(lines)) == len(lines)
        # Rotation decided on the real size: no file grows past the limit,
        # and none was left nearly empty by a duplicate rotation.
        rotated = [f for f in files if f.name != "api.log"]
        assert rotated
        assert all(f.stat().st_size <= MAX_BYTES for f in files)
        assert all(f.stat().st_size > MAX_BYTES // 2 for f in rotated)

    def test_reopens_the_file_another_process_rotated(self, tmp_path: Path) -> None:
        path = tmp_path / "api.log"
        handler = LockedRotatingFileHandler(path, max_bytes=0, backup_count=1)
        handler.setFormatter(logging.Formatter("%(message)s"))
        handler.handle(make_record("before"))
        path.rename(tmp_path / "api.log.1")  # what another worker's rollover does

        handler.handle(make_record("after"))
        handler.close()

        assert path.read_text() == "after\n"
        assert (tmp_path / "api.log.1").read_text() == "before\n"


class TestDroppingQueueHandler:
    def test_drops_instead_of_blocking_and_reports_the_count(self) -> None:
        log_queue: queue.Queue[logging.LogRecord] = queue.Queue(maxsize=2)
        handler = DroppingQueueHandler(log_queue, "app_logger")

        for i in range(5):
            handler.handle(make_record(f"line {i}"))

        assert log_queue.qsize() == 2
        assert handler.dropped == 3

        log_queue.get_nowait()
        log_queue.get_nowait()
        handler.handle(make_record("after"))

        messages = [log_queue.get_nowait().getMessage() for _ in range(2)]
        assert messages == ["after", "Log queue full: 3 records dropped"]
        assert handler.dropped == 0


class _ListHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


class TestQueuedLogger:
    def test_stop_writes_everything_still_queued(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("server.logger.CONFIG.log_queue_max_size", 1000)
        target = _ListHandler()
        queued = QueuedLogger("test_queued", [target])
        test_logger = logging.getLogger("test_queued")
        test_logger.propagate = False
        test_logger.addHandler(queued.queue_handler)
        try:
            queued.start()
            for i in range(100):
                test_logger.warning("line %d", i)
            queued.stop()
        finally:
            test_logger.removeHandler(queued.queue_handler)

        assert target.messages == [f"line {i}" for i in range(100)]
        assert not queued.running
