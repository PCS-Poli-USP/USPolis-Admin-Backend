from pydantic import BaseModel, field_validator


class JupiterLoginRequest(BaseModel):
    n_usp: str
    password: str

    @field_validator("n_usp")
    def validate_n_usp(cls, n_usp: str) -> str:
        n_usp_clean = n_usp.strip()
        if not n_usp_clean:
            raise ValueError("n_usp must not be empty")
        return n_usp_clean

    @field_validator("password")
    def validate_password(cls, password: str) -> str:
        password_clean = password.strip()
        if not password_clean:
            raise ValueError("password must not be empty")
        return password_clean
