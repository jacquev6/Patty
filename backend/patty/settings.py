import datetime
import os

import pydantic


DATABASE_URL = os.environ["PATTY_DATABASE_URL"]
DATABASE_BACKUPS_URL = os.environ["PATTY_DATABASE_BACKUPS_URL"]
assert not DATABASE_BACKUPS_URL.endswith("/")
DATABASE_BACKUP_PULSE_MONITORING_URL = os.environ["PATTY_DATABASE_BACKUP_PULSE_MONITORING_URL"]
SUBMISSION_DAEMON_PULSE_MONITORING_URL = os.environ["PATTY_SUBMISSION_DAEMON_PULSE_MONITORING_URL"]
SECRET_JWT_KEY = os.environ["PATTY_SECRET_JWT_KEY"]
# Hashed password can be generated with 'python -m patty hash-password <password>'
HASHED_PASSWORD = os.environ["PATTY_HASHED_PASSWORD"]
AUTHENTICATION_MAX_VALIDITY = pydantic.RootModel[datetime.timedelta](
    os.environ["PATTY_AUTHENTICATION_MAX_VALIDITY"]  # type: ignore[arg-type]
).root
EXTERNAL_EXERCISES_URL = os.environ["PATTY_EXTERNAL_EXERCISES_URL"]
assert not EXTERNAL_EXERCISES_URL.endswith("/")
PDF_FILES_URL = os.environ["PATTY_PDF_FILES_URL"]
assert not PDF_FILES_URL.endswith("/")
