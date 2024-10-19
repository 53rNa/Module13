# Задача "Асинхронные силачи"

import asyncio


# Асинхронная функция start_strongman(name, power), в которой name - имя силача, power - его подъёмная мощность
async def start_strongman(name, power):
    print(f'Силач {name} начал соревнования')

    # Цикл повторяется 5 раз для имитации поднятия 5 шаров
    for ball_num in range(1, 6):
        # Реализация задержки обратно пропорциональной подъемной мощности силача
        # Чем больше мощность, тем меньше задержка
        delay = 1 / power

        # Асинхронно приостанавливаем выполнение функции на время delay, чтобы другие задачи могли выполняться
        await asyncio.sleep(delay)
        print(f'Силач {name} поднял {ball_num} шар')

    print(f'Силач {name} закончил соревнования')


# Асинхронная функция start_tournament, в которой создаются 3 задачи для функций start_strongman
async def start_tournament():
    # Создаем список задач для трех силачей с разными именами и мощностью (tasks):
    tasks = [
        start_strongman('Иван', 3),
        start_strongman('Петр', 4),
        start_strongman('Сергей', 5)
    ]

    # Ожидаем завершения всех задач из списка tasks для одновременного выполнения всех задач
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    # Запускаем асинхронную функцию start_tournament для инитации соревнования между силачами
    asyncio.run(start_tournament())
