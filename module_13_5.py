# Задача "Меньше текста, больше кликов"

import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Настраиваем логирование для отслеживания работы бота
logging.basicConfig(level=logging.INFO)

# Создаем экземпляр бота с API-токеном и диспетчера
api = '7933847033:AAGwNQzC9IusxY1cIe0svYwfzevGXLMtFMQ'
bot = Bot(token = api)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Создаем клавиатуру (ReplyKeyboardMarkup) и 2 кнопки (KeyboardButton) на ней с текстом: 'Рассчитать' и 'Информация',
# так, чтобы клавиатура подстраивалась под размеры интерфейса устройства при помощи параметра resize_keyboard
button1 = KeyboardButton(text='Информация')
button2 = KeyboardButton(text='Рассчитать')
kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button1, button2)

# Определение состояний. Создаем класс UserState, наследованный от StatesGroup с тремя состояниями:
# age, growth, weight (возраст, рост, вес)
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(commands = ['start'])
async def start(message):
    await message.answer('Привет! Я бот, помогающий твоему здоровью.', reply_markup=kb)

@dp.message_handler(text = ['Информация'])
async def inform(message):
    await message.answer('Информация о боте!')


# Функция для обработки команды 'Расчитать'
@dp.message_handler(text=['Рассчитать'])
async def cmd_calculate(message: types.Message):
    await message.answer("Введите свой возраст:")

    # Устанавливаем состояние age
    await UserState.age.set()


# Функция для обработки ввода возраста
@dp.message_handler(state=UserState.age)
async def set_age(message: types.Message, state: FSMContext):

    # Получаем введенный возраст
    age = message.text

    # Сохраняем возраст в состоянии
    await state.update_data(age=age)
    await message.answer("Введите свой рост (в см):")

    # Переход к следующему состоянию
    await UserState.growth.set()


# Функция для обработки ввода роста
@dp.message_handler(state=UserState.growth)
async def set_growth(message: types.Message, state: FSMContext):

    # Получаем введенный рост
    growth = message.text

    # Сохраняем рост в состоянии
    await state.update_data(growth=growth)
    await message.answer("Введите свой вес (в кг):")

    # Переход к следующему состоянию
    await UserState.weight.set()


# Функция для обработки ввода веса и расчета нормы калорий
@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):

    # Получаем введенный вес
    weight = message.text

    # Сохраняем вес в состоянии
    await state.update_data(weight=weight)

    # Получаем все данные пользователя
    data = await state.get_data()
    age = int(data.get('age'))
    growth = int(data.get('growth'))
    weight = int(data.get('weight'))

    # Формула Миффлина - Сан Жеора для мужчин:
    calories = 10 * weight + 6.25 * growth - 5 * age + 5

    await message.answer(f"Ваша норма калорий: {calories:.2f} ккал.")

    # Завершаем, чтобы сохранить состояние
    await state.finish()

@dp.message_handler()
async def all_messages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)