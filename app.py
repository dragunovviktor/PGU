import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handels import router

async def main():
    TOKEN_API = '7824936199:AAHO8j-aGUszBF2_gibOV0tD_V5KzDsacfs'  # Укажи свой токен
    bot = Bot(token=TOKEN_API)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
