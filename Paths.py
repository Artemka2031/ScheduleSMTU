import json
from pathlib import Path


class PathBase:
    cwd: Path
    save_directory: Path
    schedule_smtu_dir: Path
    main_page: Path
    faculty_data: Path
    faculties_dir: Path
    schedule_smtu_json: Path
    schedule_smtu_min_json: Path
    db_path: Path

    def __init__(self):
        self.cwd = Path("P:\Python\pars_smtu")
        self.save_directory = self.cwd / Path("WebScrapingData")
        self.schedule_smtu_dir = self.cwd / Path("Schedule_smtu")
        self.main_page = self.save_directory / "listschedule.html"
        self.faculty_data = self.save_directory / "faculty_data.json"
        self.faculties_dir = self.save_directory / "faculties"
        self.schedule_smtu_json = self.schedule_smtu_dir / 'Schedule_smtu.json'
        self.schedule_smtu_min_json = self.schedule_smtu_dir / 'Schedule_smtu.min.json'


path_base = PathBase()


def get_group_json_path(group_number):
    group_dir = find_group_dir_by_group_number(group_number)
    if group_dir:
        # Формируем имя файла базы данных
        json_file_name = f"{group_number}.json"
        json_file_path = group_dir / json_file_name
        return json_file_path
    else:
        print(f"Директория для группы {group_number} не найдена.")
        return None


def get_all_group_numbers():
    try:
        with open(path_base.faculty_data, 'r', encoding='utf-8') as json_file:
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


def get_group_html_path(group_number):
    group_dir = find_group_dir_by_group_number(group_number)
    if group_dir:
        # Формируем имя файла базы данных
        html_file_name = f"{group_number}.html"
        html_file_path = group_dir / html_file_name
        return html_file_path
    else:
        print(f"Директория для группы {group_number} не найдена.")
        return None


def find_schedule_link_by_group_number(group_number):
    group_number = str(group_number)

    # Путь к JSON-файлу с данными о группах
    json_file_path = path_base.faculty_data

    if json_file_path.is_file():
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            faculty_data = json.load(json_file)

        # Поиск ссылки на расписание по номеру группы
        for faculty, groups in faculty_data.items():
            for group_data in groups:
                if 'group' in group_data and 'link' in group_data:
                    if group_data['group'] == group_number:
                        return group_data['link']

    return None


def find_group_dir_by_group_number(group_number):
    # Преобразуем group_number в строку
    group_number = str(group_number)

    # Проверяем, существует ли JSON-файл с данными о факультетах и группах
    if not path_base.faculty_data.is_file():
        raise FileNotFoundError("JSON-файл с данными о факультетах и группах не найден.")

    try:
        with open(path_base.faculty_data, 'r', encoding='utf-8') as json_file:
            faculty_data = json.load(json_file)

        # Поиск группы по номеру в данных о факультетах и группах
        for faculty, groups in faculty_data.items():
            for group_data in groups:
                if 'group' in group_data and 'link' in group_data:
                    if group_data['group'] == group_number:
                        # Формируем путь к папке группы
                        group_dir = path_base.faculties_dir / faculty / group_number
                        if group_dir.is_dir():
                            return group_dir

        # Если группы с указанным номером не найдено, вызываем исключение
        raise FileNotFoundError(f"Директория для группы {group_number} не найдена.")

    except FileNotFoundError as e:
        # Можно обработать FileNotFoundError отдельно
        raise e
    except Exception as e:
        # Любые другие исключения обработать как общие ошибки
        raise Exception(f"Произошла ошибка при поиске директории группы {group_number}: {str(e)}")


def get_faculties_and_groups():
    try:
        with open(path_base.faculty_data, 'r', encoding='utf-8') as json_file:
            faculty_data = json.load(json_file)

        faculties_and_groups = {}

        for faculty, groups in faculty_data.items():
            faculty_name = faculty
            group_numbers = [group_data['group'] for group_data in groups if 'group' in group_data]
            faculties_and_groups[faculty_name] = group_numbers

        return faculties_and_groups

    except Exception as e:
        print(f"Произошла ошибка при получении информации о факультетах и группах: {str(e)}")
        return {}


if __name__ == "__main__":
    pass
