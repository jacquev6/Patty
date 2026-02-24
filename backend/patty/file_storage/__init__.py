# MALIN Platform https://malin.cahiersfantastiques.fr/
# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
