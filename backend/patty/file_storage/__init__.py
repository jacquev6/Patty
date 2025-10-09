from .. import settings
from .s3_engine import S3FileStorageEngine

external_exercises = S3FileStorageEngine(settings.EXTERNAL_EXERCISES_URL)
pdf_files = S3FileStorageEngine(settings.PDF_FILES_URL)
exercise_images = S3FileStorageEngine(settings.EXERCISE_IMAGES_URL)
