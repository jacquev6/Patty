from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "429d2fb463dd"
down_revision: Union[str, None] = "194496f6cfd3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Custom collation: https://dba.stackexchange.com/a/285230
    op.execute(sa.text("CREATE COLLATION exercise_number (provider = icu, locale = 'en-u-kn-true')"))
