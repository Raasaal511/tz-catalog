from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from typing import AsyncIterator

import aioboto3
from botocore.exceptions import ClientError

from app.core.config import Settings, get_settings


class S3Storage:
    """Stateless S3/MinIO client. Safe for multi-instance deployments."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._session = aioboto3.Session()

    @asynccontextmanager
    async def _client(self):
        async with self._session.client(
            "s3",
            endpoint_url=self.settings.s3_endpoint_url,
            aws_access_key_id=self.settings.s3_access_key,
            aws_secret_access_key=self.settings.s3_secret_key,
            region_name=self.settings.s3_region,
        ) as client:
            yield client

    async def ensure_bucket(self) -> None:
        async with self._client() as client:
            try:
                await client.head_bucket(Bucket=self.settings.s3_bucket)
            except ClientError:
                await client.create_bucket(Bucket=self.settings.s3_bucket)

    def build_object_key(self, filename: str | None = None) -> str:
        ext = ""
        if filename and "." in filename:
            ext = "." + filename.rsplit(".", 1)[-1].lower()[:10]
        return f"products/{uuid.uuid4().hex}{ext}"

    async def upload(
        self,
        *,
        data: bytes,
        content_type: str,
        filename: str | None = None,
        object_key: str | None = None,
    ) -> str:
        key = object_key or self.build_object_key(filename)
        async with self._client() as client:
            await client.put_object(
                Bucket=self.settings.s3_bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
            )
        return key

    async def head(self, object_key: str) -> dict:
        async with self._client() as client:
            return await client.head_object(Bucket=self.settings.s3_bucket, Key=object_key)

    async def download(self, object_key: str) -> tuple[bytes, str]:
        async with self._client() as client:
            response = await client.get_object(Bucket=self.settings.s3_bucket, Key=object_key)
            body = await response["Body"].read()
            content_type = response.get("ContentType") or "application/octet-stream"
            return body, content_type

    async def stream(self, object_key: str) -> AsyncIterator[bytes]:
        async with self._client() as client:
            response = await client.get_object(Bucket=self.settings.s3_bucket, Key=object_key)
            body = response["Body"]
            while True:
                chunk = await body.read(64 * 1024)
                if not chunk:
                    break
                yield chunk


s3_storage = S3Storage()
