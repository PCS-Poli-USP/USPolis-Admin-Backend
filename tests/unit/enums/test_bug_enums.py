import pytest

from server.utils.enums.bug_enums import BugPriority, BugStatus, BugType


def test_bug_priority_values_returns_every_member() -> None:
    assert set(BugPriority.values()) == set(BugPriority)


@pytest.mark.parametrize(
    ("priority", "expected"),
    [
        (BugPriority.LOW, "Baixa"),
        (BugPriority.AVERAGE, "Média"),
        (BugPriority.HIGH, "Alta"),
        (BugPriority.URGENT, "Urgente"),
    ],
)
def test_bug_priority_to_ptBr_translates_every_member(
    priority: BugPriority, expected: str
) -> None:
    assert BugPriority.to_ptBr(priority) == expected


def test_bug_status_values_returns_every_member() -> None:
    assert set(BugStatus.values()) == set(BugStatus)


def test_bug_type_values_returns_every_member() -> None:
    assert set(BugType.values()) == set(BugType)


@pytest.mark.parametrize(
    ("bug_type", "expected"),
    [
        (BugType.FUNCTIONALITY, "Funcionalidade"),
        (BugType.PERFORMANCE, "Desempenho"),
        (BugType.SECURITY, "Segurança"),
        (BugType.CRASH_ERROR, "Erro inesperado"),
        (BugType.UI, "Interface"),
        (BugType.OTHER, "Outro"),
    ],
)
def test_bug_type_to_ptBr_translates_every_member(
    bug_type: BugType, expected: str
) -> None:
    assert BugType.to_ptBr(bug_type) == expected
