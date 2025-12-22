# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

import dataclasses
import datetime
import os

import pydantic


################
# Introduction #
################

# This file is a reference of all environment variables used by Patty.
# (We use code as documentation to avoid discrepancies.)

# Variables marked as optional must *not* be set to an empty string value.
# They must be either unset or set to a correct value.

# This file is designed to fail fast if (at import time):
# - a required variable is missing
# - an optional variable set to an empty string


#################
# External LLMs #
#################

# MistralAI API key, from https://console.mistral.ai/api-key
# Required.
# Looks like: an opaque string.
MISTRALAI_API_KEY = os.environ["PATTY_MISTRALAI_API_KEY"]

# OpenAI API key, from https://platform.openai.com/api-keys
# Required.
# Looks like: an opaque string.
OPENAI_API_KEY = os.environ["PATTY_OPENAI_API_KEY"]

# GoogleAI API key, from https://aistudio.google.com/app/apikey
# Required.
# Looks like: an opaque string.
GEMINIAI_KEY = os.environ["PATTY_GEMINIAI_KEY"]


#######################
# Models used locally #
#######################

# Absolute path to the images detection model.
# Required.
# Looks like: `/absolute/path/to/2025-09-15-detImages.pt`.
# You must put this file there yourself.
IMAGES_DETECTION_MODEL_2025_09_15_PATH = os.environ["PATTY_2025_09_15_IMAGES_DETECTION_PT_PATH"]

# Absolute path to the exercises classification model.
# Required.
# Looks like: `/absolute/path/to/2025-05-20-classification_camembert.pt`.
# You must put this file there yourself.
CLASSIFICATION_CAMEMBERT_2025_05_20_PATH = os.environ["PATTY_2025_05_20_CLASSIFICATION_CAMEMBERT_PT_PATH"]


################
# Data storage #
################

# PostgreSQL database URL.
# Required.
# Looks like: `postgresql+psycopg2://user:password@host:port/database`.
DATABASE_URL = os.environ["PATTY_DATABASE_URL"]

# URL prefix where Patty will store database backups.
# Required.
# Looks like: `s3://bucket/path/to/backups` or `file:///absolute/path/to/backups`.
DATABASE_BACKUPS_URL = os.environ["PATTY_DATABASE_BACKUPS_URL"]
assert not DATABASE_BACKUPS_URL.endswith("/")

# URL prefix where Patty will store files for external exercises (Word, Excel, etc.).
# Required.
# Looks like: `s3://bucket/path/to/exercises` or `file:///absolute/path/to/exercises`.
EXTERNAL_EXERCISES_URL = os.environ["PATTY_EXTERNAL_EXERCISES_URL"]
assert not EXTERNAL_EXERCISES_URL.endswith("/")

# URL prefix where Patty will store files for lessons (Word, PDF).
# Required.
# Looks like: `s3://bucket/path/to/lessons` or `file:///absolute/path/to/lessons`.
LESSONS_URL = os.environ["PATTY_LESSONS_URL"]
assert not LESSONS_URL.endswith("/")

# URL prefix where Patty will store textbook PDF files.
# Required.
# Looks like: `s3://bucket/path/to/pdfs` or `file:///absolute/path/to/pdfs`.
PDF_FILES_URL = os.environ["PATTY_PDF_FILES_URL"]
assert not PDF_FILES_URL.endswith("/")

# URL prefix where Patty will store images detected and extracted from textbooks.
# Required.
# Looks like: `s3://bucket/path/to/images` or `file:///absolute/path/to/images`.
EXERCISE_IMAGES_URL = os.environ["PATTY_EXERCISE_IMAGES_URL"]
assert not EXERCISE_IMAGES_URL.endswith("/")

# Path where Patty will save detected images and annotated pages, for debugging purposes.
# Optional.
# Looks like: `/absolute/path/to/detected/images`.
# This is only used during development. Keep it unset in production.
DETECTED_IMAGES_SAVE_PATH = os.environ.get("PATTY_DETECTED_IMAGES_SAVE_PATH")
assert DETECTED_IMAGES_SAVE_PATH != ""

if any(
    url.startswith("s3://")
    for url in [DATABASE_BACKUPS_URL, EXTERNAL_EXERCISES_URL, PDF_FILES_URL, EXERCISE_IMAGES_URL]
):
    # Key to an AWS IAM user with permissions to write to any S3 bucket used above.
    # Required if an s3:// URL has been configured above.
    # Looks like: two opaque strings.
    assert "AWS_ACCESS_KEY_ID" in os.environ
    assert "AWS_SECRET_ACCESS_KEY" in os.environ


##############
# Monitoring #
##############

# Pulse monitor URL from https://updown.io/checks for monitoring that database backups are performed periodically.
# Optional.
# Looks like: `https://pulse.updown.io/opaque-path`.
DATABASE_BACKUP_PULSE_MONITORING_URL = os.environ.get("PATTY_DATABASE_BACKUP_PULSE_MONITORING_URL")
assert DATABASE_BACKUP_PULSE_MONITORING_URL != ""

# Pulse monitor URL from https://updown.io/checks for monitoring that the submission daemon checks for new tasks periodically.
# Optional.
# Looks like: `https://pulse.updown.io/opaque-path`.
SUBMISSION_DAEMON_PULSE_MONITORING_URL = os.environ.get("PATTY_SUBMISSION_DAEMON_PULSE_MONITORING_URL")
assert SUBMISSION_DAEMON_PULSE_MONITORING_URL != ""


#######################
# User authentication #
#######################

# A secret key used to sign JWT tokens for user authentication.
# Required.
# Looks like: an opaque string.
SECRET_JWT_KEY = os.environ["PATTY_SECRET_JWT_KEY"]

# Hashed password for the single user.
# Required.
# Can be generated with `python -m patty hash-password <password>`.
# Looks like: `$argon2id$v=19$m=65536,t=3,p=4$opaque-string$opaque-string`.
HASHED_PASSWORD = os.environ["PATTY_HASHED_PASSWORD"]

# Maximum validity duration for authentication tokens.
# Required.
# In [ISO 8601 duration format](https://en.wikipedia.org/wiki/ISO_8601#Durations).
# Looks like: `PT3H` (three hours) or `P365D` (one year).
AUTHENTICATION_MAX_VALIDITY = (
    pydantic.RootModel[datetime.timedelta].model_validate(os.environ["PATTY_AUTHENTICATION_MAX_VALIDITY"]).root
)


###########
# Mailing #
###########


@dataclasses.dataclass
class OutboundMailingSettings:
    MAIL_SENDER: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str


# Settings for outbound mailing.
# Optional.
# If unset, no email will be sent.
# If set, all fields must be set.
OUTBOUND_MAILING: OutboundMailingSettings | None
try:
    OUTBOUND_MAILING = OutboundMailingSettings(
        # Email address used as sender for outgoing emails.
        # Optional.
        # Looks like: `user@gmail.com`.
        MAIL_SENDER=os.environ["PATTY_MAIL_SENDER"],
        # SMTP server host name.
        # Optional.
        # Looks like: `some.host-name.com`.
        # Maybe: `smtp.gmail.com`.
        SMTP_HOST=os.environ["PATTY_SMTP_HOST"],
        # SMTP server port.
        # Optional.
        # Looks like: an integer.
        # Maybe: `465`.
        SMTP_PORT=int(os.environ["PATTY_SMTP_PORT"]),
        # SMTP user name.
        # Optional.
        # Looks like: maybe an email address, maybe an opaque string.
        # Maybe: `user@gmail.com`.
        SMTP_USER=os.environ["PATTY_SMTP_USER"],
        # SMTP password.
        # Optional.
        # Looks like: an opaque string.
        # Maybe an 'App password' from https://myaccount.google.com/apppasswords
        SMTP_PASSWORD=os.environ["PATTY_SMTP_PASSWORD"],
    )
except KeyError:
    OUTBOUND_MAILING = None
