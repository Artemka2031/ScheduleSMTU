#!/usr/bin/env python3
import asyncio
import os
import sys
import subprocess
import platform
import time

os.environ["PYTHONPATH"] = os.path.abspath(".")

def create_virtualenv():
    if not os.path.exists("venv"):
        print("Создаём виртуальное окружение...")
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])


def activate_virtualenv():
    venv_path = os.path.abspath("venv")
    if platform.system() == "Windows":
        venv_python = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        venv_python = os.path.join(venv_path, "bin", "python")
    if not os.path.exists(venv_python):
        raise FileNotFoundError(f"Python интерпретатор не найден в {venv_python}")
    print(f"Виртуальное окружение активировано. Путь: {venv_python}")
    return venv_python


def install_requirements(venv_python):
    requirements_file = os.path.abspath("requirements.txt")
    if not os.path.exists(requirements_file):
        print("Файл requirements.txt не найден!")
        sys.exit(1)
    print("Устанавливаем библиотеки из requirements.txt...")
    subprocess.check_call([venv_python, "-m", "pip", "install", "-r", requirements_file])
    print("Библиотеки установлены.")


def check_docker():
    try:
        subprocess.check_call(["docker", "--version"], stdout=subprocess.DEVNULL)
        print("Docker установлен.")
    except FileNotFoundError:
        print("Docker не установлен. Установите Docker вручную.")
        sys.exit(1)

def check_docker_compose():
    try:
        subprocess.check_call(["docker-compose", "--version"], stdout=subprocess.DEVNULL)
        print("Docker Compose установлен.")
    except FileNotFoundError:
        print("Docker Compose не установлен. Установите его вручную.")
        sys.exit(1)

def run_docker_compose():
    docker_compose_dir = os.path.abspath("docker_compose")
    print(f"Запускаем docker-compose из директории: {docker_compose_dir}")
    subprocess.check_call(["docker-compose", "up", "--build", "-d"], cwd=docker_compose_dir)
    print("Docker-compose запущен.")

def stop_docker_compose():
    docker_compose_dir = os.path.abspath("docker_compose")
    print(f"Останавливаем docker-compose из директории: {docker_compose_dir}")
    subprocess.check_call(["docker-compose", "stop"], cwd=docker_compose_dir)
    print("Docker-compose остановлен (контейнеры выключены, но не удалены).")

def run_django(venv_python):
    project_dir = os.path.abspath("djcore")
    print(f"Запускаем Django-проект из директории: {project_dir}")
    # Выполним миграции (для первого развертывания это очень важно, если БД запускается в контейнере)
    command_migrate = [venv_python, "manage.py", "migrate"]
    subprocess.run(command_migrate, cwd=project_dir)
    print('Миграция выполнена')

    command = [venv_python, "manage.py", "runserver", "127.0.0.1:8080", "--noreload"]
    process = subprocess.Popen(command, cwd=project_dir)
    print("Django-проект запущен.")
    run_rabbit_consumer = [venv_python, os.path.join(project_dir, "apps", "database", "rabbitmq_consumer_runner.py")]
    subprocess.Popen(run_rabbit_consumer, cwd=project_dir, preexec_fn=os.setpgrp if platform.system() != "Windows" else None)

    return process

def run_celery(venv_python):
    project_dir = os.path.abspath(".")
    print(f"Запускаем Celery-воркеры из директории: {project_dir}")

    if platform.system() != "Windows":
        # Для Linux/Mac – получаем путь до celery из виртуального окружения
        venv_dir = os.path.dirname(venv_python)
        celery_path = os.path.join(venv_dir, "celery")
        if not os.path.exists(celery_path):
            raise FileNotFoundError(f"Celery не найден по пути: {celery_path}")
        command = [celery_path, "-A", "djcore", "worker", "--loglevel=info", "--pool=solo", "-Q", "celery",
                   "--hostname=worker1"]
        command_beat = [celery_path, '-A', 'djcore.celery_app', 'beat', '-l', 'INFO']

    else:
        command = ["celery", "-A", "djcore", "worker", "--loglevel=info", "--pool=solo", "-Q", "celery",
               "--hostname=worker1"]
        command_beat = ["celery", "-A", "djcore.celery_app", "beat", "-l", "INFO"]

    subprocess.Popen(command, cwd=project_dir,
                 preexec_fn=os.setpgrp if platform.system() != "Windows" else None)
    subprocess.Popen(command_beat, cwd=project_dir,
                     preexec_fn=os.setpgrp if platform.system() != "Windows" else None)


    print("Celery-воркеры запущены.")


def install_system_dependencies():
    """Устанавливает системные зависимости перед установкой Python-библиотек."""
    try:
        print("Обновляем пакетный менеджер и устанавливаем зависимости...")
        subprocess.check_call(["apt", "update"])
        subprocess.check_call(["apt", "install", "-y", "pkg-config", "libmariadb-dev"])
        print("Системные зависимости установлены.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при установке системных пакетов: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print(f"Текущая директория: {os.getcwd()}")
    print(f"Абсолютный путь к проекту: {os.path.abspath('.')}")
    try:
        create_virtualenv()
        venv_python = activate_virtualenv()
        #install_system_dependencies()
        subprocess.check_call([venv_python, "-m", "pip", "install", "-r", "requirements.txt"])
        check_docker()
        check_docker_compose()
        run_docker_compose()
        django_process = run_django(venv_python)
        time.sleep(2)
        run_celery(venv_python)
        django_process.wait()
    except KeyboardInterrupt:
        print("Прерывание. Завершаем процессы...")
        stop_docker_compose()
        sys.exit(0)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
