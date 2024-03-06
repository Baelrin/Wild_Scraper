from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import Base, engine, User, ProductQuery, save_product_query, get_product_info
from sqlalchemy.orm import sessionmaker

# Настройка бота и диспетчера
bot = Bot(token='YOUR_BOT_TOKEN')
dp = Dispatcher(bot, storage=MemoryStorage())

# Создание сессии для работы с базой данных
Session = sessionmaker(bind=engine)

# Определение состояний для FSM


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
        # Реализация логики остановки уведомлений
        pass
    elif callback_query.data == 'get_db_info':
        # Реализация логики получения информации из БД
        pass

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

# Запуск бота
if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
