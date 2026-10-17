from fastapi import HTTPException, status
from sqlmodel import Session, col, func, select

from server.models.database.api_client_db_model import ApiClient
from server.models.database.user_db_model import User
from server.models.http.requests.api_key_request_models import (
    ApiClientRegister,
    ApiClientUpdate,
)
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.must_be_int import must_be_int


class ApiClientRepository:
    @classmethod
    def get_by_id(cls, *, id: int, session: Session) -> ApiClient:
        client = session.get(ApiClient, id)
        if client is None:
            raise ApiClientNotFound(id=id)
        return client

    @classmethod
    def get_all(cls, *, session: Session) -> list[ApiClient]:
        statement = select(ApiClient).order_by(col(ApiClient.name))
        return list(session.exec(statement).all())

    @classmethod
    def create(
        cls, *, input: ApiClientRegister, user: User, session: Session
    ) -> ApiClient:
        cls.__ensure_name_available(name=input.name, session=session)
        client = ApiClient(
            name=input.name,
            organization=input.organization,
            contact_name=input.contact_name,
            contact_email=input.contact_email,
            description=input.description,
            created_by_id=must_be_int(user.id),
        )
        session.add(client)
        session.flush()
        return client

    @classmethod
    def update(cls, *, id: int, input: ApiClientUpdate, session: Session) -> ApiClient:
        client = cls.get_by_id(id=id, session=session)
        if input.name.lower() != client.name.lower():
            cls.__ensure_name_available(name=input.name, session=session)
        client.name = input.name
        client.organization = input.organization
        client.contact_name = input.contact_name
        client.contact_email = input.contact_email
        client.description = input.description
        client.updated_at = BrazilDatetime.now_utc()
        session.add(client)
        return client

    @classmethod
    def set_active(cls, *, id: int, is_active: bool, session: Session) -> ApiClient:
        """Activate or deactivate a client: deactivating rejects all of its
        keys at once, without revoking them one by one."""
        client = cls.get_by_id(id=id, session=session)
        client.is_active = is_active
        client.updated_at = BrazilDatetime.now_utc()
        session.add(client)
        return client

    @classmethod
    def __ensure_name_available(cls, *, name: str, session: Session) -> None:
        # Case-insensitive, so "Grêmio" and "grêmio" can't both exist.
        statement = select(ApiClient).where(func.lower(ApiClient.name) == name.lower())
        if session.exec(statement).first() is not None:
            raise ApiClientNameAlreadyExists(name=name)


class ApiClientNotFound(HTTPException):
    def __init__(self, id: int) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND, f"Cliente da API com id {id} não encontrado"
        )


class ApiClientNameAlreadyExists(HTTPException):
    def __init__(self, name: str) -> None:
        super().__init__(
            status.HTTP_409_CONFLICT, f"Já existe um cliente da API chamado {name}"
        )
