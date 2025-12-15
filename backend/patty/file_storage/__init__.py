# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

import urllib.parse

from .. import settings
from .s3_engine import S3FileStorageEngine
from .file_system_engine import FileSystemStorageEngine


def make_storage_engine(prefix_url: str) -> S3FileStorageEngine | FileSystemStorageEngine:
    target = urllib.parse.urlparse(prefix_url)
    if target.scheme == "s3":
        return S3FileStorageEngine(target)
    elif target.scheme == "file":
        return FileSystemStorageEngine(target)
    else:
        raise ValueError(f"Unsupported storage scheme: {target.scheme}")


external_exercises = make_storage_engine(settings.EXTERNAL_EXERCISES_URL)
lessons = make_storage_engine(settings.LESSONS_URL)
pdf_files = make_storage_engine(settings.PDF_FILES_URL)
exercise_images = make_storage_engine(settings.EXERCISE_IMAGES_URL)
