import datetime

import fastapi
import sqlalchemy as sql

from ..api_utils import ApiModel
from ..database_utils import SessionDependable
from ..mailing import send_mail
from ..settings import MAIL_SENDER
from ..version import PATTY_VERSION
from .orm_models import ErrorCaughtByFrontend


router = fastapi.APIRouter()


class PostErrorsCaughtByFrontendRequest(ApiModel):
    creator: str | None
    user_agent: str
    window_size: str
    url: str
    caught_by: str
    message: str
    code_location: str | None


class PostErrorsCaughtByFrontendResponse(ApiModel):
    pass


@router.post("")
def create_error(
    req: PostErrorsCaughtByFrontendRequest, session: SessionDependable
) -> PostErrorsCaughtByFrontendResponse:
    if PATTY_VERSION != "dev":
        send_mail(
            to=MAIL_SENDER,
            subject=f"Patty version {PATTY_VERSION}: error caught by frontend",
            body=req.model_dump_json(indent=2),
        )
    session.add(
        ErrorCaughtByFrontend(
            created_at=datetime.datetime.now(datetime.timezone.utc),
            created_by_username=req.creator,
            patty_version=PATTY_VERSION,
            user_agent=req.user_agent,
            window_size=req.window_size,
            url=req.url,
            caught_by=req.caught_by,
            message=req.message,
            code_location=req.code_location,
        )
    )
    return PostErrorsCaughtByFrontendResponse()


class GetErrorsCaughtByFrontendResponse(ApiModel):
    class Error(ApiModel):
        id: str
        created_by: str | None
        created_at: datetime.datetime
        patty_version: str
        user_agent: str
        window_size: str
        url: str
        caught_by: str
        message: str
        code_location: str | None

    errors: list[Error]


@router.get("")
def retrieve_errors(session: SessionDependable) -> GetErrorsCaughtByFrontendResponse:
    return GetErrorsCaughtByFrontendResponse(
        errors=[
            GetErrorsCaughtByFrontendResponse.Error(
                id=str(error.id),
                created_by=error.created_by_username,
                created_at=error.created_at,
                patty_version=error.patty_version,
                user_agent=error.user_agent,
                window_size=error.window_size,
                url=error.url,
                caught_by=error.caught_by,
                message=error.message,
                code_location=error.code_location,
            )
            for error in session.execute(sql.select(ErrorCaughtByFrontend).order_by(-ErrorCaughtByFrontend.id))
            .scalars()
            .all()
        ]
    )
