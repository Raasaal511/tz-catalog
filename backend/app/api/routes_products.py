from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_request_base_url
from app.core.security import require_internal_api_key
from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductList, ProductRead
from app.services import products as product_service
from app.services.s3 import s3_storage

router = APIRouter(prefix="/products", tags=["products"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_BYTES = 10 * 1024 * 1024


@router.get("", response_model=ProductList)
async def list_products(
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> ProductList:
    base_url = get_request_base_url(request)
    return await product_service.list_products(session, base_url=base_url)


@router.post(
    "",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_internal_api_key)],
)
async def create_product(
    request: Request,
    title: str = Form(..., min_length=1, max_length=255),
    created_by: str | None = Form(default=None),
    image: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
) -> ProductRead:
    content_type = (image.content_type or "").lower()
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type: {content_type}",
        )

    data = await image.read()
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty image")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image too large")

    image_key = await s3_storage.upload(
        data=data,
        content_type=content_type,
        filename=image.filename,
    )

    payload = ProductCreate(title=title, created_by=created_by)
    base_url = get_request_base_url(request)
    return await product_service.create_product(
        session,
        payload=payload,
        image_key=image_key,
        content_type=content_type,
        base_url=base_url,
    )


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> ProductRead:
    product = await product_service.get_product(session, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product_service.to_read(product, base_url=get_request_base_url(request))
