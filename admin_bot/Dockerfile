# Используем базовый образ Python 3.9
FROM python:3.10-slim

# Указываем рабочую директорию внутри контейнера
WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
        git \
        locales && \
    sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    sed -i '/ru_RU.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
RUN apt-get install -y bash

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# Копируем файл с зависимостями в контейнер
COPY admin_bot/requirements.txt /app/requirements.txt

# Устанавливаем зависимости через pip
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в контейнер
COPY admin_bot /app/admin_bot
COPY admin_bot/wait-for-it.sh /app/admin_bot/wait-for-it.sh

RUN chmod +x /app/admin_bot/wait-for-it.sh
# Устанавливаем переменную окружения PYTHONPATH
ENV PYTHONPATH=/app

# Даем права на выполнение скриптов, если это необходимо
RUN chmod +x /app/admin_bot/start_bot.py

# Указываем команду для запуска бота
CMD ["python", "admin_bot/start_bot.py"]
