import logging

import httpx
from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards import catalog_hint_text, catalog_keyboard
from app.services.catalog_api import catalog_api

logger = logging.getLogger(__name__)
router = Router(name="admin")


@router.message(Command("create"))
async def cmd_create(message: Message, is_admin: bool) -> None:
    if not is_admin:
        await message.answer("Команда доступна только администраторам.")
        return

    await message.answer(
        "Отправьте одно сообщение: фото товара + название в подписи (caption)."
    )


@router.message(F.photo)
async def create_product_from_photo(message: Message, bot: Bot, is_admin: bool) -> None:
    if not is_admin:
        # Regular users still get the catalog CTA on any photo
        await message.answer(
            "У меня есть товар" + catalog_hint_text(),
            reply_markup=catalog_keyboard(),
        )
        return

    title = (message.caption or "").strip()
    if not title:
        await message.answer(
            "Нужно название в подписи к фото.\n"
            "Отправьте фото и название одним сообщением."
        )
        return

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    if not file.file_path:
        await message.answer("Не удалось получить файл изображения из Telegram.")
        return

    buffer = await bot.download_file(file.file_path)
    image_bytes = buffer.read() if buffer else b""
    if not image_bytes:
        await message.answer("Пустой файл изображения.")
        return

    status = await message.answer("Сохраняю товар…")
    try:
        created_by = str(message.from_user.id) if message.from_user else "unknown"
        product = await catalog_api.create_product(
            title=title,
            image_bytes=image_bytes,
            filename=f"{photo.file_unique_id}.jpg",
            content_type="image/jpeg",
            created_by=created_by,
        )
    except httpx.HTTPStatusError as exc:
        logger.exception("API rejected product create")
        detail = exc.response.text[:300]
        await status.edit_text(f"Ошибка API ({exc.response.status_code}): {detail}")
        return
    except Exception:
        logger.exception("Failed to create product")
        await status.edit_text("Не удалось создать товар. Попробуйте позже.")
        return

    await status.edit_text(
        f"Товар создан: «{product.get('title')}» (id={product.get('id')})."
        + catalog_hint_text(),
        reply_markup=catalog_keyboard(),
    )
