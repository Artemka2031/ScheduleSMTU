import json

from Paths import get_group_json_path, path_base


def create_smtu_schedule():
    try:
        # Проверяем, существует ли JSON-файл с данными о факультетах и группах
        if not path_base.faculty_data.is_file():
            raise FileNotFoundError("JSON-файл с данными о факультетах и группах не найден.")

        # Открываем JSON-файл с данными о факультетах и группах
        with open(path_base.faculty_data, 'r', encoding='utf-8') as json_file:
            faculty_data = json.load(json_file)

        # Создаем пустой словарь для хранения данных о расписаниях
        schedule_data = {}

        # Проходим по факультетам и их группам
        for faculty, groups in faculty_data.items():
            faculty_schedule = {}  # Создаем словарь для текущего факультета
            for group_data in groups:
                if 'group' in group_data and 'link' in group_data:
                    group_id = group_data['group']
                    link = group_data['link']

                    schedule_path = get_group_json_path(group_id)
                    with open(schedule_path, 'r', encoding='utf-8') as schedule_file:
                        schedule = json.load(schedule_file)

                    # Добавляем данные о группе в словарь факультета
                    faculty_schedule[group_id] = {
                        'link': link,
                        'schedule': schedule
                    }

            # Добавляем словарь факультета в общий словарь
            schedule_data[faculty] = faculty_schedule

        # Создаем папку, если она не существует
        path_base.schedule_smtu_dir.mkdir(parents=True, exist_ok=True)

        # Создаем и записываем файл Schedule_smtu.json
        file_path = path_base.schedule_smtu_dir / 'Schedule_smtu.json'
        with open(file_path, 'w', encoding='utf-8') as schedule_file:
            json.dump(schedule_data, schedule_file, ensure_ascii=False, indent=4)

        file_path = path_base.schedule_smtu_dir / 'Schedule_smtu.min.json'
        with open(file_path, 'w', encoding='utf-8') as schedule_file:
            json.dump(schedule_data, schedule_file, ensure_ascii=False, separators=(',', ':'))

    except FileNotFoundError as e:
        # Можно обработать FileNotFoundError отдельно
        raise e
    except Exception as e:
        # Любые другие исключения обрабатывать как общие ошибки
        raise Exception(f"Произошла ошибка при создании файла расписания: {str(e)}")
