import json
from pathlib import Path


class PathBase:
    def __init__(self):
        self.save_directory = Path("WebScrapingData")
        self.schedule_smtu_dir = Path("Schedule_smtu")
        self.main_page = self.save_directory / "listschedule.html"
        self.faculty_data = self.save_directory / "faculty_data.json"
        self.faculties_dir = self.save_directory / "faculties"
        self.schedule_smtu_json = self.schedule_smtu_dir / 'Schedule_smtu.json'
        self.schedule_smtu_min_json = self.schedule_smtu_dir / 'Schedule_smtu.min.json'


class Paths(PathBase):
    def get_all_group_numbers(self):
        try:
            with open(self.faculty_data, 'r', encoding='utf-8') as json_file:
                faculty_data = json.load(json_file)

            group_numbers = []

            for groups in faculty_data.values():
                for group_data in groups:
                    if 'group' in group_data:
                        group_number = group_data['group']
                        group_numbers.append(group_number)

            return group_numbers

        except Exception as e:
            print(f"Произошла ошибка при получении номеров групп: {str(e)}")
            return []

    def create_faculty_dirs(self):
        json_file_path = self.faculty_data

        self.faculties_dir.mkdir(exist_ok=True)

        if json_file_path.is_file():
            with open(json_file_path, 'r', encoding='utf-8') as json_file:
                faculty_data = json.load(json_file)

            for faculty, groups in faculty_data.items():
                faculty_dir = self.faculties_dir / faculty
                faculty_dir.mkdir(exist_ok=True)

                for group_data in groups:
                    group_name = group_data['group']
                    group_dir = faculty_dir / group_name
                    group_dir.mkdir(exist_ok=True)

            print("Директории для факультетов и групп созданы в 'faculties'.")
        else:
            print(f"Файл {json_file_path} не найден. Сначала выполните парсинг данных.")

    def find_group_dir_by_group_id(self, group_id):
        # Преобразуем group_id в строку
        group_id = str(group_id)

        # Проверяем, существует ли JSON-файл с данными о факультетах и группах
        if not self.faculty_data.is_file():
            raise FileNotFoundError("JSON-файл с данными о факультетах и группах не найден.")

        try:
            with open(self.faculty_data, 'r', encoding='utf-8') as json_file:
                faculty_data = json.load(json_file)

            # Поиск группы по номеру в данных о факультетах и группах
            for faculty, groups in faculty_data.items():
                for group_data in groups:
                    if 'group' in group_data and 'link' in group_data:
                        if group_data['group'] == group_id:
                            # Формируем путь к папке группы
                            group_dir = self.faculties_dir / faculty / group_id
                            if group_dir.is_dir():
                                return group_dir

            # Если группы с указанным номером не найдено, вызываем исключение
            raise FileNotFoundError(f"Директория для группы {group_id} не найдена.")

        except FileNotFoundError as e:
            # Можно обработать FileNotFoundError отдельно
            raise e
        except Exception as e:
            # Любые другие исключения обработать как общие ошибки
            raise Exception(f"Произошла ошибка при поиске директории группы {group_id}: {str(e)}")

    def find_schedule_link_by_group_id(self, group_id):
        # Путь к JSON-файлу с данными о группах
        json_file_path = self.faculty_data

        if json_file_path.is_file():
            with open(json_file_path, 'r', encoding='utf-8') as json_file:
                faculty_data = json.load(json_file)

            # Поиск ссылки на расписание по номеру группы
            for faculty, groups in faculty_data.items():
                for group_data in groups:
                    if 'group' in group_data and 'link' in group_data:
                        if group_data['group'] == group_id:
                            return group_data['link']

        return None

    def get_group_html_path(self, group_id):
        group_dir = self.find_group_dir_by_group_id(group_id)
        if group_dir:
            # Формируем имя файла базы данных
            html_file_name = f"{group_id}.html"
            html_file_path = group_dir / html_file_name
            return html_file_path
        else:
            print(f"Директория для группы {group_id} не найдена.")
            return None

    def get_group_json_path(self, group_id):
        group_dir = self.find_group_dir_by_group_id(group_id)
        if group_dir:
            # Формируем имя файла базы данных
            json_file_name = f"{group_id}.json"
            json_file_path = group_dir / json_file_name
            return json_file_path
        else:
            print(f"Директория для группы {group_id} не найдена.")
            return None


db = Path("ORM") / "datebase.db"
schedule_smtu_min_json = Path("Schedule_smtu") / "Schedule_smtu.min.json"
