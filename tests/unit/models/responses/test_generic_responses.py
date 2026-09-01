from server.models.http.responses.generic_responses import Message


class TestMessage:
    def test_from_message(self) -> None:
        data = Message.from_message("Operação concluída")

        assert data.message == "Operação concluída"
