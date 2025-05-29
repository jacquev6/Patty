import datetime
import typing
import unittest

from starlette import status
import argon2
import jwt
import fastapi
import fastapi.security
import fastapi.testclient

from . import settings
from .api_utils import ApiModel


router = fastapi.APIRouter()


class PostTokenRequest(ApiModel):
    password: str
    validity: datetime.timedelta = settings.AUTHENTICATION_MAX_VALIDITY


class PostTokenResponse(ApiModel):
    access_token: str
    valid_until: datetime.datetime
    token_type: str = "bearer"


class Token(ApiModel):
    version: typing.Literal["1"] = "1"
    valid_until: datetime.datetime


password_hasher = argon2.PasswordHasher()


@router.post("/token")
def login(req: PostTokenRequest) -> PostTokenResponse:
    try:
        password_hasher.verify(settings.HASHED_PASSWORD, req.password)
    except argon2.exceptions.VerifyMismatchError:
        raise fastapi.HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect password")
    else:
        validity = settings.AUTHENTICATION_MAX_VALIDITY
        if req.validity is not None and req.validity < validity:
            validity = req.validity
        valid_until = datetime.datetime.now(tz=datetime.timezone.utc) + validity
        token = jwt.encode(
            Token(valid_until=valid_until).model_dump(mode="json"), settings.SECRET_JWT_KEY, algorithm="HS256"
        )
        return PostTokenResponse(access_token=token, valid_until=valid_until)


def check_token_validity(token: str) -> typing.Literal[True]:
    try:
        token_ = Token(**jwt.decode(token, settings.SECRET_JWT_KEY, algorithms=["HS256"]))
    except jwt.exceptions.InvalidTokenError:
        raise fastapi.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    else:
        if datetime.datetime.now(tz=datetime.timezone.utc) > token_.valid_until:
            raise fastapi.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
        else:
            return True


def auth_bearer_dependable(
    token: typing.Annotated[
        str, fastapi.Depends(fastapi.security.OAuth2PasswordBearer(tokenUrl="token", auto_error=False))
    ],
) -> typing.Literal[True]:
    return check_token_validity(token)


AuthBearerDependable = typing.Annotated[typing.Literal[True], fastapi.Depends(auth_bearer_dependable)]


def auth_param_dependable(token: str) -> typing.Literal[True]:
    return check_token_validity(token)


AuthParamDependable = typing.Annotated[typing.Literal[True], fastapi.Depends(auth_param_dependable)]


class AuthenticationApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.app = fastapi.FastAPI()
        self.app.include_router(router)

        @self.app.get("/bearer")
        def bearer(token_is_valid: AuthBearerDependable) -> typing.Literal[True]:
            return token_is_valid

        @self.app.get("/param")
        def param(token_is_valid: AuthParamDependable) -> typing.Literal[True]:
            return token_is_valid

        self.client = fastapi.testclient.TestClient(self.app)

    def test_unauthenticated(self) -> None:
        response = self.client.get("http://server/bearer")
        self.assertEqual(response.status_code, 401, response.json())

        response = self.client.get("http://server/param", params={"token": ""})
        self.assertEqual(response.status_code, 401, response.json())

    def test_wrong_password(self) -> None:
        response = self.client.post("http://server/token", json={"password": "not-the-password"})
        self.assertEqual(response.status_code, 403, response.json())
        self.assertEqual(response.json(), {"detail": "Incorrect password"})

    def test_password_flow_success(self) -> None:
        response = self.client.post("http://server/token", json={"password": "password"})
        self.assertEqual(response.status_code, 200, response.json())
        token = response.json()["accessToken"]

        response = self.client.get("http://server/bearer", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(response.json(), True)

        response = self.client.get("http://server/param", params={"token": token})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(response.json(), True)

    def test_token_expiration(self) -> None:
        before = datetime.datetime.now(tz=datetime.timezone.utc)
        response = self.client.post("http://server/token", json={"password": "password", "validity": "PT0S"})
        after = datetime.datetime.now(tz=datetime.timezone.utc)
        self.assertEqual(response.status_code, 200, response.json())
        json_response = PostTokenResponse(**response.json())
        self.assertGreater(json_response.valid_until, before)
        self.assertLess(json_response.valid_until, after)
        token = json_response.access_token

        response = self.client.get("http://server/bearer", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 401, response.json())
        self.assertEqual(response.json(), {"detail": "Invalid or expired token"})

        response = self.client.get("http://server/param", params={"token": token})
        self.assertEqual(response.status_code, 401, response.json())
        self.assertEqual(response.json(), {"detail": "Invalid or expired token"})

    def test_tempering_with_token_validity(self) -> None:
        before = datetime.datetime.now(tz=datetime.timezone.utc)
        # Request a token with longer-than-default validity
        response = self.client.post("http://server/token", json={"password": "password", "validity": "P1D"})
        after = datetime.datetime.now(tz=datetime.timezone.utc)
        self.assertEqual(response.status_code, 200, response.json())
        json_response = PostTokenResponse(**response.json())

        # Validity is the default one despite the tempering attempt
        self.assertGreater(json_response.valid_until, before + datetime.timedelta(hours=3))
        self.assertLess(json_response.valid_until, after + datetime.timedelta(hours=3))
        token_string = json_response.access_token
        token = Token(**jwt.decode(token_string, options={"verify_signature": False}))
        self.assertGreater(token.valid_until, before + datetime.timedelta(hours=3))
        self.assertLess(token.valid_until, after + datetime.timedelta(hours=3))

        # Try to set 'validUntil' in the token
        tempered_token = jwt.encode(
            Token(valid_until=token.valid_until + datetime.timedelta(hours=24)).model_dump(mode="json"),
            "not-the-secret",
            algorithm="HS256",
        )

        # Be detected
        response = self.client.get("http://server/bearer", headers={"Authorization": f"Bearer {tempered_token}"})
        self.assertEqual(response.status_code, 401, response.json())
        self.assertEqual(response.json(), {"detail": "Invalid or expired token"})

        response = self.client.get("http://server/param", params={"token": tempered_token})
        self.assertEqual(response.status_code, 401, response.json())
        self.assertEqual(response.json(), {"detail": "Invalid or expired token"})
