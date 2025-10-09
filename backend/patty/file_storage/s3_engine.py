import io
import itertools
import typing
import urllib.parse

import boto3
import botocore.client

s3 = boto3.client("s3", config=botocore.client.Config(region_name="eu-west-3", signature_version="s3v4"))


class S3FileStorageEngine:
    def __init__(self, prefix_url: str) -> None:
        target = urllib.parse.urlparse(prefix_url)
        assert target.scheme == "s3"
        self.bucket = target.netloc
        assert target.path.startswith("/")
        self.prefix = target.path[1:]
        assert not self.prefix.endswith("/")

    def store_sync(self, key: str, data: bytes) -> None:
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

    def load_sync(self, key: str) -> bytes:
        object = s3.get_object(Bucket=self.bucket, Key=self.__make_key(key))
        return typing.cast(bytes, object["Body"].read())

    def get_get_url(self, key: str) -> str:
        return typing.cast(
            str,
            s3.generate_presigned_url(
                "get_object", Params={"Bucket": self.bucket, "Key": self.__make_key(key)}, ExpiresIn=3600
            ),
        )

    def delete_sync(self, key: str) -> None:
        try:
            s3.delete_object(Bucket=self.bucket, Key=self.__make_key(key))
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "NoSuchKey":
                pass
            else:
                raise

    def delete_all(self) -> None:
        assert "patty/dev" in self.prefix
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
