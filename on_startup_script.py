#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import time

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
    print(f"Запускаем docker-compose из директории: {docker_compose_dir}")
    subprocess.check_call(["docker-compose", "down", "-v"], cwd=docker_compose_dir)
    print("Docker-compose запущен.")

def run_django(venv_python):
    project_dir = os.path.abspath("djcore")
    print(f"Запускаем Django-проект из директории: {project_dir}")
    #Выполним миграции (для перового развертывания это очень важно, если БД запускается в контейнере)

    command_migrate = [venv_python, "manage.py", "migrate"]
    subprocess.run(command_migrate, cwd=project_dir)
    print(f'Миграция выполнена')
    command = [venv_python, "manage.py", "runserver", "127.0.0.1:8000", "--noreload"]
    process = subprocess.Popen(command, cwd=project_dir)
    print("Django-проект запущен.")
    run_rabbit_consumer = [venv_python, f'{project_dir}\\apps\\database\\rabbitmq_consumer_runner.py']
    subprocess.Popen(run_rabbit_consumer, cwd=project_dir, preexec_fn=os.setpgrp if platform.system() != "Windows" else None)

    return process

def run_celery():
    project_dir = os.path.abspath(".")
    print(f"Запускаем Celery-воркеры из директории: {project_dir}")
    command = ["celery", "-A", "djcore", "worker", "--loglevel=info", "--pool=solo", "-Q", "celery", "--hostname=worker1"]
    subprocess.Popen(command, cwd=project_dir, preexec_fn=os.setpgrp if platform.system() != "Windows" else None)
    print("Celery-воркеры запущены.")

if __name__ == "__main__":
    print(f"Текущая директория: {os.getcwd()}")
    print(f"Абсолютный путь к проекту: {os.path.abspath('.')}")
    try:
        # create_virtualenv()
        venv_python = activate_virtualenv()
        # subprocess.check_call([venv_python, "-m", "pip", "install", "-r", "requirements.txt"])
        check_docker()
        check_docker_compose()
        run_docker_compose()
        django_process = run_django(venv_python)
        time.sleep(1)
        run_celery()
        django_process.wait()
    except KeyboardInterrupt:
        print("Прерывание. Завершаем процессы...")
        stop_docker_compose()
        sys.exit(0)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
