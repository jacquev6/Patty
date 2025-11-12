import os
import typing
import urllib.parse

import fastapi
import jwt

from .. import settings
from ..api_utils import ApiModel


class Token(ApiModel):
    version: typing.Literal["1"] = "1"
    operation: typing.Literal["put", "get"]
    prefix: str
    key: str


def make_path(prefix: str, key: str) -> str:
    assert ".." not in key
    assert "/" not in key
    return os.path.join(prefix, key)


def make_url(operation: typing.Literal["put", "get"], prefix: str, key: str) -> str:
    token = jwt.encode(
        Token(operation=operation, prefix=prefix, key=key).model_dump(mode="json"),
        settings.SECRET_JWT_KEY,
        algorithm="HS256",
    )
    return f"/api/files/{key}?token={urllib.parse.quote(token)}"


def check_token(raw_token: str, operation: typing.Literal["put", "get"], key: str) -> Token:
    try:
        token = Token.model_validate(jwt.decode(raw_token, settings.SECRET_JWT_KEY, algorithms=["HS256"]))
    except jwt.exceptions.InvalidTokenError:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="File not found")
    else:
        if token.operation != operation or token.key != key:
            raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="File not found")
        return token


router = fastapi.APIRouter()


@router.put("/api/files/{key}")
async def put_file(key: str, token: str, request: fastapi.Request) -> None:
    with open(make_path(check_token(token, "put", key).prefix, key), "wb") as f:
        async for chunk in request.stream():
            f.write(chunk)


@router.get("/api/files/{key}")
async def get_file(key: str, token: str) -> fastapi.responses.FileResponse:
    return fastapi.responses.FileResponse(make_path(check_token(token, "get", key).prefix, key))


class FileSystemStorageEngine:
    def __init__(self, target: urllib.parse.ParseResult) -> None:
        assert target.scheme == "file"
        assert target.netloc == ""
        assert target.path.startswith("/")
        assert not target.path.endswith("/")
        self.prefix = target.path
        os.makedirs(self.prefix, exist_ok=True)

    def store(self, key: str, data: bytes) -> None:
        with open(self._make_path(key), "wb") as file:
            file.write(data)

    def get_put_url(self, key: str) -> str:
        return make_url("put", self.prefix, key)

    def has(self, key: str) -> bool:
        return os.path.exists(self._make_path(key))

    def load(self, key: str) -> bytes:
        with open(self._make_path(key), "rb") as file:
            return file.read()

    def get_get_url(self, key: str) -> str:
        return make_url("get", self.prefix, key)

    def delete(self, key: str) -> None:
        try:
            os.remove(self._make_path(key))
        except FileNotFoundError:
            pass

    def delete_all(self) -> None:
        assert "support/dev-env" in self.prefix  # Avoid accidental use outside the development environment
        for filename in os.listdir(self.prefix):
            if filename != ".gitignore":
                os.remove(os.path.join(self.prefix, filename))

    def _make_path(self, key: str) -> str:
        return make_path(self.prefix, key)
