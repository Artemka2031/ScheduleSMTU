import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path


class WebScraper:
    def __init__(self, directory_name):
        self.save_directory = Path(directory_name)
        self.main_page = self.save_directory / "listschedule.html"
        self.faculty_data = self.save_directory / "faculty_data.json"
        self.faculties_dir = self.save_directory / "faculties"

    def set_main_page(self, file_name):
        file_path = self.save_directory / f"{file_name}.html"
        if file_path and isinstance(file_path, Path) and file_path.suffix == '.html':
            self.main_page = file_path
        else:
            print("Неверный путь к файлу .html или объект Path")

    def set_faculty_data(self, file_name):
        file_path = self.save_directory / f"{file_name}.json"
        if file_path and isinstance(file_path, Path) and file_path.suffix == '.json':
            self.faculty_data = file_path
        else:
            print("Неверный путь к файлу .json или объект Path")

    def set_faculties_dir(self, dir_name):
        dir_path = self.save_directory / f"{dir_name}"
        if dir_path and isinstance(dir_path, Path):
            self.faculties_dir = dir_path
        else:
            print("Неверный путь к файлу .json или объект Path")

    def create_main_directory(self):
        # Создайте папку, если она не существует
        self.save_directory.mkdir(parents=True, exist_ok=True)

    def load_and_save_main_page(self, url, headers, file_name):
        # Проверяем существование директории перед созданием
        if not self.save_directory.is_dir():
            self.create_main_directory()

        # Отправляем GET-запрос для загрузки страницы
        response = requests.get(url, headers=headers)

        # Проверяем успешность запроса
        if response.status_code == 200:
            # Получаем содержимое страницы
            html = response.text

            # Создаем объект Beautiful Soup для разбора разметки
            soup = BeautifulSoup(html, 'html.parser')

            # Теперь в переменной 'soup' у вас есть доступ к разметке страницы
            # Вы можете использовать Beautiful Soup для извлечения данных

            # Пример: вывести заголовок страницы
            print(soup.title.text)


            # Определяем имя файла для сохранения (например, "главная_страница.html")
            if self.main_page is None:
                self.set_main_page(self.save_directory / file_name)


            # Сохраняем разметку в файл
            with open(self.main_page, 'w', encoding='utf-8') as file:
                file.write(html)

            print(f"Разметка сохранена в {self.main_page}")
        else:
            print("Не удалось загрузить страницу. Код состояния:", response.status_code)

    def read_main_page(self):
        if self.main_page and self.main_page.is_file():
            with open(self.main_page, 'r', encoding='utf-8') as file:
                data = file.read()
                return data
        else:
            print("Файл с главной разметкой не найден.")

    def parse_main_page(self, start_url, file_name):

        data = self.read_main_page()

        if data:
            html = data

            soup = BeautifulSoup(html, 'html.parser')
            faculty_data = {}

            # Находим все заголовки h3
            h3_elements = soup.find_all('h3', style="clear:both;padding-top:10px;")

            for h3 in h3_elements:
                faculty_name = h3.text.strip()
                faculty_data[faculty_name] = []

                # Ищем следующие элементы div с классом 'gr' до следующего заголовка h3
                next_element = h3.find_next_sibling()
                while next_element and next_element.name != 'h3':
                    if next_element.name == 'div' and 'gr' in next_element.get('class', []):
                        group_name = next_element.a.text.strip()
                        group_link = next_element.a.get('href').replace('/ru/', '')  # Убираем /ru/
                        faculty_data[faculty_name].append({'group': group_name, 'link': start_url + group_link})
                    next_element = next_element.find_next_sibling()

            # Создаем JSON-файл и записываем в него данные
            if self.faculty_data is None:
                self.set_faculty_data(file_name)

            json_file_path = self.faculty_data
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(faculty_data, json_file, ensure_ascii=False, indent=4)

            print(f"Данные сохранены в {json_file_path}")
        else:
            print("main_page не определена. Сначала загрузите страницу и установите main_page.")

    def create_faculty_dirs(self):
        json_file_path = self.faculty_data

        if self.faculties_dir is None:
            faculties_dir = self.save_directory / 'faculties'
            faculties_dir.mkdir(exist_ok=True)

        if json_file_path.is_file():
            with open(json_file_path, 'r', encoding='utf-8') as json_file:
                faculty_data = json.load(json_file)

            for faculty, groups in faculty_data.items():
                faculty_dir = faculties_dir / faculty
                faculty_dir.mkdir(exist_ok=True)

                for group_data in groups:
                    group_name = group_data['group']
                    group_dir = faculty_dir / group_name
                    group_dir.mkdir(exist_ok=True)

            print("Директории для факультетов и групп созданы в 'faculties'.")
        else:
            print(f"Файл {json_file_path} не найден. Сначала выполните парсинг данных.")
            
            
# Создайте экземпляр класса и выполните необходимые действия
web_scraper = WebScraper("WebScrapingData")
