from typing import Sequence, Union

from alembic import op
import sqlalchemy as sql


revision: str = "429d2fb463dd"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(sql.text("CREATE COLLATION exercise_number (provider = icu, locale = 'en-u-kn-true')"))
