
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta
from Parser import Parser

router = Router()

# Клавиатура с кнопками
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Расписание на неделю")],
        [KeyboardButton(text="Расписание на 2 недели")],
        [KeyboardButton(text="Расписание на 3 недели")],
        [KeyboardButton(text="Все расписание")],
        [KeyboardButton(text="Узнать расписание на конкретный день")]
    ], resize_keyboard=True, one_time_keyboard=False
)

@router.message(F.command("start"))
async def cmd_start(message: Message):
    # Отправляем сообщение с клавиатурой
    await message.answer(
        "Привет! Я помогу тебе с расписанием. Выбери нужный вариант ниже:\n\n"
        "1️⃣ Расписание на неделю\n"
        "2️⃣ Расписание на 2 недели\n"
        "3️⃣ Расписание на 3 недели\n"
        "4️⃣ Все расписание\n"
        "5️⃣ Узнать расписание на конкретный день\n\n"
        "Нажми на кнопку или введи команду!",
        reply_markup=keyboard  # Убедимся, что клавиатура передаётся
    )

@router.message(F.text)
async def handle_message(message: Message):
    text = message.text.lower()

    if text == "расписание на неделю":
        await send_schedule_for_weeks(message, weeks=1)
    elif text == "расписание на 2 недели":
        await send_schedule_for_weeks(message, weeks=2)
    elif text == "расписание на 3 недели":
        await send_schedule_for_weeks(message, weeks=3)
    elif text == "все расписание":
        await send_full_schedule(message)
    elif text == "узнать расписание на конкретный день":
        await message.answer(
            "Введите дату в формате ДД.ММ.ГГГГ, чтобы узнать расписание на этот день. Например: 25.01.2025"
        )
    else:
        # Проверяем, не ввел ли пользователь дату
        try:
            date = datetime.strptime(message.text, '%d.%m.%Y')
            await send_schedule_for_date(message, date)
        except ValueError:
            await message.answer(
                "Пожалуйста, выберите один из предложенных вариантов или введите дату в формате ДД.ММ.ГГГГ."
            )

async def send_schedule_for_weeks(message: Message, weeks: int):
    """
    Получить расписание на указанное количество недель.
    """
    parser = Parser(Parser.url)
    soup = parser.parse()

    if soup:
        full_schedule = parser.extract_schedule(soup)
        response = f"📅 Расписание на {weeks} {'неделю' if weeks == 1 else 'недели'}:\n\n"

        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=weeks)

        current_date = start_date
        while current_date < end_date:
            day_name = current_date.strftime('%A')  # Название дня недели
            formatted_date = current_date.strftime('%d.%m.%Y')  # Формат даты

            # Получаем расписание для текущего дня
            if day_name in full_schedule:
                day_schedule = full_schedule[day_name]
                response += f"📅 **{day_name} ({formatted_date})**\n"

                for item in day_schedule:
                    time = item['time']
                    subject = item['subject']
                    response += f"🕒 {time} - {subject}\n"

                response += "\n"  # Разделитель между днями
            else:
                response += f"📅 **{day_name} ({formatted_date})** - ❌ Нет занятий\n\n"

            current_date += timedelta(days=1)

            # Отправляем сообщение, если оно становится слишком длинным
            if len(response) > 3000:
                await message.answer(response)
                response = ""  # Очищаем для следующей части

        # Отправляем остаток, если он есть
        if response:
            await message.answer(response)
    else:
        await message.answer("Не удалось загрузить расписание. Попробуйте позже.")

async def send_full_schedule(message: Message):
    """
    Отправить пользователю все расписание.
    """
    parser = Parser(Parser.url)
    soup = parser.parse()

    if soup:
        full_schedule = parser.extract_schedule(soup)
        response = "📅 Полное расписание:\n\n"

        for day, schedule in full_schedule.items():
            response += f"📅 **{day}**\n"
            for item in schedule:
                time = item['time']
                subject = item['subject']
                response += f"🕒 {time} - {subject}\n"
            response += "\n"  # Разделитель между днями

            # Отправляем сообщение, если оно становится слишком длинным
            if len(response) > 3000:
                await message.answer(response)
                response = ""  # Очищаем для следующей части

        # Отправляем остаток, если он есть
        if response:
            await message.answer(response)
    else:
        await message.answer("Не удалось загрузить расписание. Попробуйте позже.")

async def send_schedule_for_date(message: Message, date: datetime):
    """
    Отправить расписание на конкретную дату.
    """
    parser = Parser(Parser.url)
    soup = parser.parse()

    if soup:
        full_schedule = parser.extract_schedule(soup)
        day_name = date.strftime('%A')  # Название дня недели
        formatted_date = date.strftime('%d.%m.%Y')

        if day_name in full_schedule:
            day_schedule = full_schedule[day_name]
            response = f"📅 Расписание на {formatted_date} ({day_name}):\n\n"
            for item in day_schedule:
                time = item['time']
                subject = item['subject']
                response += f"🕒 {time} - {subject}\n"
        else:
            response = f"📅 Расписание на {formatted_date} ({day_name}) отсутствует."

        await message.answer(response)
    else:
        await message.answer("Не удалось загрузить расписание. Попробуйте позже.")
