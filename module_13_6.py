# Задача "Ещё больше выбора"

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Создаем экземпляр бота с API-токеном и диспетчера
API_TOKEN = ''

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Определение состояний. Создаем класс UserState, наследованный от StatesGroup с тремя состояниями:
# age, growth, weight (возраст, рост, вес)
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


# Функция основного меню
@dp.message_handler(commands=['start'])
async def start_menu(message: types.Message):
    await message.answer('Привет! Я бот, помогающий твоему здоровью.')
    await message.answer("Выберите опцию:", reply_markup=main_menu())


# Создаем Inline клавиатуру
def main_menu():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Рассчитать', callback_data='calculate'))
    keyboard.add(InlineKeyboardButton('Информация', callback_data='info'))
    return keyboard


# Асинхронная функция обработки нажатия на кнопку 'Информация'
@dp.callback_query_handler(lambda call: call.data == 'info')
async def main_menu_INFO(call: types.CallbackQuery):
    await call.message.answer('Информация о боте...')


# Асинхронная функция обработки нажатия на кнопку 'Рассчитать'
@dp.callback_query_handler(lambda call: call.data == 'calculate')
async def main_menu_CALC(call: types.CallbackQuery):
    await call.message.answer("Выберите опцию:", reply_markup=inline_menu())


# Создание Inline меню для расчёта
def inline_menu():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Рассчитать норму калорий', callback_data='calories'))
    keyboard.add(InlineKeyboardButton('Формулы расчёта', callback_data='formulas'))
    return keyboard


# Асинхронная функция обработки нажатия на кнопку 'Формулы расчёта'
@dp.callback_query_handler(lambda call: call.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    formula_message = "Формула Миффлина-Сан Жеора:\n" \
                      "Для мужчин: BMR = 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) + 5\n" \
                      "Для женщин: BMR = 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) - 161"
    await call.message.answer(formula_message)


# Асинхронная функция обработки нажатия на кнопку 'Рассчитать норму калорий'. Показ двух кнопок с выбором пола
@dp.callback_query_handler(lambda call: call.data == 'calories')
async def choose_gender(call: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Для женщин', callback_data='female'))
    keyboard.add(InlineKeyboardButton('Для мужчин', callback_data='male'))
    await call.message.answer("Выберите пол:", reply_markup=keyboard)


# Асинхронная функция обработки выбора пола
@dp.callback_query_handler(lambda call: call.data in ['female', 'male'])
async def set_gender(call: types.CallbackQuery, state: FSMContext):
    # Сохраняем выбранный пол
    await state.update_data(gender=call.data)

    await call.message.answer("Введите свой возраст:")

    # Устанавливаем состояние age
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_age(message: types.Message, state: FSMContext):
    # Получаем введенный возраст
    age = message.text

    # Сохраняем возраст в состоянии
    await state.update_data(age=age)

    # Запрашиваем рост
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

    # Получаем данные о пользователе
    user_data = await state.get_data()

    age = int(user_data['age'])
    gender = user_data['gender']
    growth = int(user_data.get('growth'))
    weight = int(user_data.get('weight'))

    # Производим расчет нормы калорий по формуле Миффлина-Сан Жеора в зависимости от выбора пола
    if gender == 'female':
        bmr = 10 * weight + 6.25 * growth - 5 * age - 161
        await message.answer(f"Ваша норма калорий (BMR): {bmr:.2f} ккал.")

    elif gender == 'male':
        bmr = 10 * weight + 6.25 * growth - 5 * age + 5
        await message.answer(f"Ваша норма калорий (BMR): {bmr:.2f} ккал.")

    # Завершаем, чтобы сохранить состояние
    await state.finish()


@dp.message_handler()
async def all_messages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
