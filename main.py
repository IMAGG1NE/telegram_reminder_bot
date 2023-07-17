from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters import Text
from Keyboards import get_kb, get_cancel_kb
from commands import GREETING
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.storage import FSMContext
from datetime import datetime
import asyncio
from database import conn, cursor
from config import TOKEN_API

tasks = {}
storage = MemoryStorage()
bot = Bot(TOKEN_API) # put here your token
disp = Dispatcher(bot, storage=storage)


class ClientStatesGroup(StatesGroup):
    """создание класса состояний бота"""
    
    write_an_event = State()
    write_a_date = State()


@disp.message_handler(commands=["start"])
async def start_cmd(message: types.Message) -> None:
    """обработка команды start

    Args:
        message (types.Message): сообщение пользователя
    """
    
    await message.answer(text=GREETING, reply_markup=get_kb())


@disp.message_handler(Text(equals="❌ Отмена"), state="*")
async def cancel_cmd(message: types.Message, state: FSMContext) -> None:
    """обработка команды отмены действия

    Args:
        message (types.Message): сообщение пользователя
        state (FSMContext): состояние бота
    """
    
    if state is None:
        return 
    
    await message.answer("действие было отменено", reply_markup=get_kb())
    await state.finish()   


@disp.message_handler(Text(equals="✏️ Запланировать задачу"))
async def getting_task(message: types.Message) -> None:
    """обработка команды планирования задачи

    Args:
        message (types.Message): сообщение пользователя
    """
    
    await message.answer("Введите задачу которую вы бы хотели запланировать", reply_markup=get_cancel_kb())
    await ClientStatesGroup.write_an_event.set()


@disp.message_handler(Text(equals="📄 Показать список задач"))
async def show_all(message: types.Message) -> None:
    """обработка команды показа задач пользователя

    Args:
        message (types.Message): сообщение пользователя
    """
    cursor.execute("SELECT task_time, task_text FROM tasks")
    tasks_list = cursor.fetchall()
    
    #у пользователя еще нет добавленных задач
    if len(tasks) < 1:
        await message.answer("У вас еще нет задач 🫤")
    
    # проход по словарю tasks и отправка задач пользователя    
    else:
        tasks_list = "\n".join(f"{time}: {task}" for time, task in tasks.items())
        await message.answer(f"Список задач:\n{tasks_list}")


@disp.message_handler(state=ClientStatesGroup.write_an_event)
async def writing_task(message: types.Message, state: FSMContext) -> None:
    """сохранение задачи пользователя

    Args:
        message (types.Message): сообщение пользователя
        state (FSMContext): состояние бота
    """
    async with state.proxy() as data:
        data["task"] = message.text
         
    await message.answer(f"событие {data['task']} было сохранено, теперь введите дату когда его напомнить в формате ДД.ЧЧ:MM")
    await ClientStatesGroup.next()


async def send_reminder(message: types.Message, state: FSMContext, task_time, data: dict) -> None:
    """функция отправки напоминания пользователю в указанное им время"""
    
    cursor.execute("INSERT INTO tasks (task_text, task_time) VALUES (?, ?)",
    (data['task'], task_time.strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
        
    tasks[task_time] = data['task']   
    await message.answer(f"задача запланирована на {task_time}", reply_markup=get_kb())
    await state.finish()

    await asyncio.sleep((task_time - datetime.now()).seconds)     
    await bot.send_message(chat_id=message.chat.id, text = f"Напоминание: {data['task']}")
    del tasks[task_time]
            

@disp.message_handler(state=ClientStatesGroup.write_a_date)
async def writing_date(message: types.Message, state: FSMContext) -> None:
    """фунция  записи даты 

    Args:
        message (types.Message): сообщение пользователя
        state (FSMContext): состояние бота
    """
    #пользователь ввел дату согласно формату
    try:  
        time =datetime.strptime(message.text, "%d.%H:%M").time()
        task_time = datetime.combine(datetime.now().date(), time)
        
        async with state.proxy() as data:
            data["time"] = time
        
        if task_time <= datetime.now():
            await message.answer("Указанное время уже прошло")
            
        else:
            await send_reminder(message, state, task_time, data)
      
    # пользователь ввел дату не следуя формату        
    except (ValueError, IndexError):
        await message.reply("Некорректный формат сообщения. Пожалуйста, укажите время и текст задачи в формате ДД.ЧЧ:MM")      


if __name__ == "__main__":
    try:
        executor.start_polling(disp, skip_updates=True)
    finally:
        conn.close()