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

import io
import itertools
import typing
import urllib.parse

import boto3
import botocore.client

s3 = boto3.client("s3", config=botocore.client.Config(region_name="eu-west-3", signature_version="s3v4"))


class S3FileStorageEngine:
    def __init__(self, target: urllib.parse.ParseResult) -> None:
        assert target.scheme == "s3"
        self.bucket = target.netloc
        assert target.path.startswith("/")
        assert not target.path.endswith("/")
        self.prefix = target.path[1:]

    def store(self, key: str, data: bytes) -> None:
        file = io.BytesIO(data)
        s3.put_object(Bucket=self.bucket, Key=self.__make_key(key), Body=file)

    def get_put_url(self, key: str) -> str:
        return typing.cast(
            str,
            s3.generate_presigned_url(
                "put_object", Params={"Bucket": self.bucket, "Key": self.__make_key(key)}, ExpiresIn=300
            ),
        )

    def has(self, key: str) -> bool:
        try:
            s3.head_object(Bucket=self.bucket, Key=self.__make_key(key))
            return True
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "404":
                return False
            else:
                raise

    def load(self, key: str) -> bytes:
        object = s3.get_object(Bucket=self.bucket, Key=self.__make_key(key))
        return typing.cast(bytes, object["Body"].read())

    def get_get_url(self, key: str) -> str:
        return typing.cast(
            str,
            s3.generate_presigned_url(
                "get_object", Params={"Bucket": self.bucket, "Key": self.__make_key(key)}, ExpiresIn=3600
            ),
        )

    def delete(self, key: str) -> None:
        try:
            s3.delete_object(Bucket=self.bucket, Key=self.__make_key(key))
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "NoSuchKey":
                pass
            else:
                raise

    def delete_all(self) -> None:
        assert "patty/dev" in self.prefix  # Avoid accidental use outside the development environment
        for batch in itertools.batched(
            (
                {"Key": obj["Key"]}
                for page in s3.get_paginator("list_objects_v2").paginate(Bucket=self.bucket, Prefix=self.prefix)
                if "Contents" in page
                for obj in page["Contents"]
            ),
            1000,
        ):
            s3.delete_objects(Bucket=self.bucket, Delete={"Objects": batch})

    def __make_key(self, key: str) -> str:
        return f"{self.prefix}/{key}"
