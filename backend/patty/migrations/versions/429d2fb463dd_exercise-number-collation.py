from typing import Sequence, Union

from alembic import op

from patty.database_utils import create_exercise_number_collation


revision: str = "429d2fb463dd"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(create_exercise_number_collation)
