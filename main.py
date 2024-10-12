#!/root/SMTU/ScheduleSMTU/venv/bin/python

import asyncio
import logging

from Bot.start_bot import start_bot

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# async def run_parsing_and_refresh():
#     try:
#         # Засекаем время для парсинга
#         start_parsing_time = time.time()
#         await parsing()
#         parsing_time = time.time() - start_parsing_time
#         logging.info(f"Parsing completed successfully in {parsing_time:.2f} seconds.")
#
#         # Засекаем время для обновления базы данных
#         start_refresh_time = time.time()
#         refresh_database()
#         refresh_time = time.time() - start_refresh_time
#         logging.info(f"Database refresh completed successfully in {refresh_time:.2f} seconds.")
#     except Exception as e:
#         logging.error(f"An error occurred: {e}")


async def main():
    # scheduler = AsyncIOScheduler()
    # scheduler.add_job(run_parsing_and_refresh, 'cron', hour=4, minute=0, second=0)
    #
    # scheduler.start()

    # Запуск асинхронной функции бота в бесконечном цикле
    await start_bot()


if __name__ == "__main__":
    asyncio.run(main())
