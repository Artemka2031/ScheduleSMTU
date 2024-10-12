# Используем базовый образ Python 3.9
FROM python:3.10-slim

# Указываем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями в контейнер
COPY Bot/requirements.txt /app/requirements.txt

# Устанавливаем зависимости через pip
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в контейнер
COPY ./Bot /app/Bot

RUN chmod +x /app/Bot/wait-for-it.sh
# Устанавливаем переменную окружения PYTHONPATH
ENV PYTHONPATH=/app

# Даем права на выполнение скриптов, если это необходимо
# Даем права на выполнение скриптов, если это необходимо
RUN chmod +x /app/Bot/start_bot.py

# Указываем команду для запуска бота
CMD ["python", "Bot/start_bot.py"]
