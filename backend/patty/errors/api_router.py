import datetime

import fastapi
import sqlalchemy as sql

from .. import authentication
from ..api_utils import ApiModel
from ..database_utils import SessionDependable
from ..mailing import send_mail
from .. import settings
from ..version import PATTY_VERSION
from .orm_models import ErrorCaughtByFrontend


router = fastapi.APIRouter(dependencies=[fastapi.Depends(authentication.auth_bearer_dependable)])


class PostErrorsCaughtByFrontendRequest(ApiModel):
    creator: str | None
    user_agent: str
    window_size: str
    url: str
    caught_by: str
    message: str
    code_location: str | None
    github_issue_number: int | None


class PostErrorsCaughtByFrontendResponse(ApiModel):
    pass


@router.post("")
def create_error(
    req: PostErrorsCaughtByFrontendRequest, session: SessionDependable
) -> PostErrorsCaughtByFrontendResponse:
    if settings.OUTBOUND_MAILING is not None and req.github_issue_number is None:
        send_mail(
            to=settings.OUTBOUND_MAILING.MAIL_SENDER,
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
            github_issue_number=req.github_issue_number,
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
        github_issue_number: int | None

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
                github_issue_number=error.github_issue_number,
            )
            for error in session.execute(sql.select(ErrorCaughtByFrontend).order_by(-ErrorCaughtByFrontend.id))
            .scalars()
            .all()
        ]
    )
