import asyncio
import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)

bot = Bot(token="YOUR_API_TOKEN")
admin_id = "YOUR_ADMIN_ID"

dp = Dispatcher()
my_router = Router(name=__name__)
dp.include_router(my_router)

button = InlineKeyboardButton(text='ДА!', callback_data='button_pressed')


class FormState(StatesGroup):
    full_name = State()
    phone_number = State()
    comment = State()


# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_name = message.from_user.first_name
    await message.answer(f"{user_name}, Добро пожаловать в компанию DamnIt")
    await state.set_state(FormState.full_name)
    await message.answer("Напишите свое ФИО")


# Хэндлер для ФИО
@dp.message(FormState.full_name)
async def fio_message(message: types.Message, state: FSMContext):
    full_name = message.text

    if not (any(ch.isdigit() for ch in full_name)):
        await state.update_data(full_name=full_name)
        await state.set_state(FormState.phone_number)
        await message.answer("Укажите ваш номер телефона в формате 7 999 999 99 99:")
    else:
        await message.answer("Неверный формат ФИО. Попробуйте еще раз.")


# Хэндлер для номера телефона
@dp.message(FormState.phone_number)
async def get_phone_number(message: types.Message, state: FSMContext):
    phone_number = message.text.replace(" ", "")
    if len(phone_number) == 11 and phone_number.isdigit() and phone_number.startswith("7"):
        await state.update_data(phone_number=phone_number)
        await state.set_state(FormState.comment)
        await message.answer("Напишите любой комментарий")
    else:
        await message.answer("Неверный формат номера телефона. Попробуйте еще раз.")


# Хэндлер для комментария
@dp.message(FormState.comment)
async def get_comment(message: types.Message, state: FSMContext):
    comment = message.text
    await state.update_data(comment=comment)
    await message.answer("Последний шаг! Ознакомьтесь с вводными положениями")
    await message.answer_document(document=FSInputFile('test.pdf'))
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    await message.answer("Ознакомился", reply_markup=keyboard)


@my_router.callback_query(lambda c: c.data == 'button_pressed')
async def final_step(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    full_name = data.get('full_name')
    phone_number = data.get('phone_number')
    comment = data.get('comment')
    registration_info = (f"Новая заявка, Мой Господин\nФИО: {full_name}\n"
                         f"Номер телефона: {phone_number}\nКомментарий: {comment}")
    await bot.send_message(chat_id=admin_id, text=registration_info)
    await callback.message.answer("Спасибо за успешную регистрацию")
    await callback.message.answer_photo(photo=FSInputFile('photo.jpg'))
    await state.clear()


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())