import subprocess
import os

if __name__ == '__main__':
    # Путь к Python в виртуальном окружении
    venv_python = os.path.join('venv', 'Scripts', 'python.exe')  # Windows


    # Запуск Django
    subprocess.Popen([venv_python, 'manage.py', 'runserver'])

    # Запуск RabbitMQConsumer
    subprocess.Popen([venv_python, './djcore/apps/database/rabbitmq_consumer.py'])

    # Запуск Celery Worker
    subprocess.Popen(['venv/Scripts/celery', '-A', 'djcore', 'worker', '--loglevel=debug', '--pool=solo', '-Q', 'bot_queue'])
