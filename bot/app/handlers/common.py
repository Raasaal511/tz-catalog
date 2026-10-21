from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from app.keyboards import admin_help_keyboard, catalog_hint_text, catalog_keyboard

router = Router(name="common")


@router.message(CommandStart())
@router.message(Command("help"))
@router.message(Command("catalog"))
async def cmd_start(message: Message, is_admin: bool) -> None:
    text = "У меня есть товар" + catalog_hint_text()
    if is_admin:
        text += (
            "\n\nВы администратор.\n"
            "Чтобы создать товар, отправьте одно сообщение с фото и подписью (названием).\n"
            "Команда /create — подсказка."
        )
        await message.answer(text, reply_markup=admin_help_keyboard())
        return

    await message.answer(text, reply_markup=catalog_keyboard())


@router.callback_query(F.data == "admin:create_help")
async def create_help_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(  # type: ignore[union-attr]
        "Создание товара:\n"
        "1. Отправьте фото товара\n"
        "2. В подписи (caption) укажите название\n"
        "Всё в одном сообщении."
    )
