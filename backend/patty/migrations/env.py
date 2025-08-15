from alembic import context

from patty import database_utils
from patty import errors  # noqa: F401 to populate the metadata
from patty import external_exercises  # noqa: F401
from patty import sandbox  # noqa: F401
from patty import settings
from patty import textbooks  # noqa: F401
from patty import to_be_deleted  # noqa: F401


assert not context.is_offline_mode()

engine = database_utils.create_engine(settings.DATABASE_URL)

with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=database_utils.OrmBase.metadata)

    with context.begin_transaction():
        context.run_migrations()
