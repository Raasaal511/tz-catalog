from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductList, ProductRead


def to_read(product: Product, *, base_url: str) -> ProductRead:
    return ProductRead(
        id=product.id,
        title=product.title,
        image_url=f"{base_url.rstrip('/')}/api/v1/media/{product.image_key}",
        created_at=product.created_at,
    )


async def list_products(session: AsyncSession, *, base_url: str) -> ProductList:
    total = await session.scalar(select(func.count()).select_from(Product)) or 0
    result = await session.scalars(select(Product).order_by(Product.created_at.desc()))
    items = [to_read(product, base_url=base_url) for product in result.all()]
    return ProductList(items=items, total=total)


async def create_product(
    session: AsyncSession,
    *,
    payload: ProductCreate,
    image_key: str,
    content_type: str,
    base_url: str,
) -> ProductRead:
    product = Product(
        title=payload.title.strip(),
        image_key=image_key,
        content_type=content_type,
        created_by=payload.created_by,
    )
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return to_read(product, base_url=base_url)


async def get_product(session: AsyncSession, product_id: int) -> Product | None:
    return await session.get(Product, product_id)


async def get_product_by_image_key(session: AsyncSession, image_key: str) -> Product | None:
    result = await session.scalars(select(Product).where(Product.image_key == image_key))
    return result.first()
