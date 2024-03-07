from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import engine, ProductQuery, save_product_query, get_product_info, save_subscription
from sqlalchemy.orm import sessionmaker
import asyncio

# Настройка бота и диспетчера без MemoryStorage
bot = Bot(token='YOUR_BOT_TOKEN')
dp = Dispatcher(bot, storage=MemoryStorage())

# Создание сессии для работы с базой данных
Session = sessionmaker(bind=engine)

# Опреде��ение состояний для FSM


class ProductQueryForm(StatesGroup):
    product_code = State()

# Обработчик команды /start


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        "Получить информацию по товару", callback_data='get_product_info'))
    keyboard.add(InlineKeyboardButton("Остановить уведомления",
                 callback_data='stop_notifications'))
    keyboard.add(InlineKeyboardButton(
        "Получить информацию из БД", callback_data='get_db_info'))
    await message.answer("Выберите действие:", reply_markup=keyboard)

# Обработчик нажатия на кнопку


@dp.callback_query_handler(lambda c: c.data in ['get_product_info', 'stop_notifications', 'get_db_info'])
async def process_callback_button1(callback_query: types.CallbackQuery):
    if callback_query.data == 'get_product_info':
        await ProductQueryForm.product_code.set()
        await bot.send_message(callback_query.from_user.id, "Введите артикул товара:")
    elif callback_query.data == 'stop_notifications':
        user_id = callback_query.from_user.id
        product_code = "example_product_code"  # Замените на реальный код товара
        remove_subscription(user_id, product_code)
        await bot.send_message(user_id, "Уведомления остановлены.")
    elif callback_query.data == 'get_db_info':
        records = get_last_5_records()
        message = "Последние 5 записей:\n"
        for record in records:
            message += f"ID: {record.id}, Пользователь: {record.user_id}, Артикул: {
                record.product_code}, Время запроса: {record.query_time}\n"
        await bot.send_message(callback_query.from_user.id, message)

# Обработчик ввода артикула товара


@dp.message_handler(state=ProductQueryForm.product_code)
async def process_product_code(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        product_code = data['product_code']
        user_id = message.from_user.id
    save_product_query(user_id, product_code)
    product_info = get_product_info(product_code)
    await bot.send_message(user_id, product_info)
    await state.finish()

# Обработчик подписки


@dp.callback_query_handler(lambda c: c.data == 'subscribe')
async def subscribe_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    product_code = callback_query.message.text.split('\n')[1].split(': ')[1]
    save_subscription(user_id, product_code)
    await bot.send_message(user_id, "Вы успешно подписались на уведомления.")

# Функция для отправки уведомлений


async def send_notifications():
    while True:
        session = Session()
        subscriptions = session.query(Subscription).all()
        for subscription in subscriptions:
            product_info = get_product_info(subscription.product_code)
            await bot.send_message(subscription.user_id, product_info)
        await asyncio.sleep(300)  # 5 минут

# Функция для получения последних 5 записей из БД


def get_last_5_records():
    session = Session()
    records = session.query(ProductQuery).order_by(
        ProductQuery.query_time.desc()).limit(5).all()
    session.close()
    return records


# Запуск бота
if __name__ == '__main__':
    from aiogram import executor
    from asyncio import create_task
    create_task(send_notifications())
    executor.start_polling(dp, skip_updates=True)
