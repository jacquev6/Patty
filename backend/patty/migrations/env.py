from alembic import context

from patty import database_utils
from patty import orm_models  # noqa: F401 to populate the metadata
from patty import settings


assert not context.is_offline_mode()

engine = database_utils.create_engine(settings.DATABASE_URL)

with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=database_utils.OrmBase.metadata)

    with context.begin_transaction():
        context.run_migrations()
