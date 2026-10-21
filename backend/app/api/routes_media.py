from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from botocore.exceptions import ClientError

from app.services.s3 import s3_storage

router = APIRouter(prefix="/media", tags=["media"])


@router.get("/{object_key:path}")
async def get_media(object_key: str) -> StreamingResponse:
    try:
        head = await s3_storage.head(object_key)
        content_type = head.get("ContentType") or "application/octet-stream"
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if code in {"404", "NoSuchKey", "NotFound"}:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found") from exc
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Storage error") from exc

    return StreamingResponse(
        s3_storage.stream(object_key),
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=86400"},
    )
