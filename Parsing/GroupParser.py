import json
import requests
from bs4 import BeautifulSoup

from Parsing.Paths import Paths


class GroupParser(Paths):

    def save_group_schedule_to_html(self, group_id, headers):
        # Находим директорию группы по её ID
        group_dir = self.find_group_dir_by_group_id(group_id)
        if not group_dir:
            raise FileNotFoundError(f"Директория для группы {group_id} не найдена.")

        # Находим ссылку на расписание для группы
        schedule_link = self.find_schedule_link_by_group_id(group_id)
        if not schedule_link:
            raise ValueError(f"Ссылка на расписание для группы {group_id} не найдена.")

        # Отправляем GET-запрос для загрузки расписания
        response = requests.get(schedule_link, headers=headers)

        # Проверяем успешность запроса
        if response.status_code != 200:
            raise ConnectionError(
                f"Не удалось загрузить расписание для группы {group_id}. Код состояния: {response.status_code}")

        # Получаем содержимое расписания
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # Находим блок с расписанием
        schedule_div = soup.find('div', class_='collapse js-view-mode-container', id='table-container')
        if not schedule_div:
            raise ValueError(f"Блок с расписанием не найден на странице.")

        # Определяем имя файла для сохранения (например, "1111.html")
        file_name = f"{group_id}.html"

        # Сохраняем расписание в файл
        file_path = group_dir / file_name
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(str(schedule_div))

        print(f"Расписание для группы {group_id} сохранено в {file_path}")

    def parse_schedule_html(self, group_id):
        html_path = self.get_group_html_path(group_id)
        json_path = self.get_group_json_path(group_id)

        try:
            with open(html_path, 'r', encoding='utf-8') as file:
                html = file.read()

            # Проверяем, что HTML-файл не пустой
            if not html.strip():
                print(f"HTML-файл для группы {group_id} пуст.")
                return
        except FileNotFoundError:
            print(f"HTML-файл для группы {group_id} не найден.")
            return

        try:
            # Создаем объект Beautiful Soup для разбора разметки
            soup = BeautifulSoup(html, 'html.parser')

            # Находим все блоки с расписанием для разных дней недели
            day_blocks = soup.find_all('div', class_='card my-4')

            schedule_data = []

            # Проходим по блокам с расписанием
            for day_block in day_blocks:
                # Извлекаем день недели из заголовка
                day_name = day_block.find('h3', class_='h5 my-0').text

                # Ищем таблицу с расписанием
                table = day_block.find('table', class_='table mb-0 table-responsive')

                day_schedule = []

                if table:
                    rows = table.find_all('tr')[1:]  # Пропускаем заголовок таблицы

                    # Проходим по строкам таблицы
                    for row in rows:
                        columns = row.find_all(['th', 'td'])  # Извлекаем все столбцы в текущей строке

                        # Проверяем, что в строке есть 6 столбцов
                        if len(columns) == 6:
                            # Извлекаем данные из столбцов
                            time = columns[0].text.strip()
                            week = columns[1].find('i')['data-bs-title']

                            # Извлекаем аудиторию и разбиваем ее на корпус и номер аудитории
                            classroom_info = columns[2].text.strip()
                            classroom_parts = classroom_info.split()
                            classroom = {
                                'Корпус': classroom_parts[0],
                                'Номер аудитории': classroom_parts[1] if len(classroom_parts) == 2 else ''
                            }

                            group = columns[3].text.strip()

                            # Извлекаем информацию о предмете и его типе
                            subject_info = columns[4].find('span').text.strip()
                            subject_type_info = columns[4].find_all('small')

                            subject_name = subject_info
                            subject_type = subject_type_info[0].text.strip()

                            subject_additional_parts = subject_type_info[1].text.strip() if len(
                                subject_type_info) == 2 else ''

                            subject_dict = {
                                "Наименование предмета": subject_name,
                                "Тип занятия": subject_type,
                                "Дополнительная информация": subject_additional_parts
                            }

                            # Извлекаем информацию о преподавателе
                            teacher_info = columns[5].text.strip().split()
                            teacher_dict = {
                                "Фамилия": teacher_info[0] if len(teacher_info) >= 1 else '',
                                "Имя": teacher_info[1] if len(teacher_info) >= 2 else '',
                                "Отчество": teacher_info[2] if len(teacher_info) >= 3 else ''
                            }

                            # Добавляем данные о паре в расписание для дня
                            day_schedule.append({
                                'Время': time,
                                'Неделя': week,
                                'Аудитория': classroom,
                                'Группа': group,
                                'Предмет': subject_dict,
                                'Преподаватель': teacher_dict
                            })

                    # Добавляем данные о дне в общее расписание
                    schedule_data.append({
                        'День недели': day_name,
                        'Расписание': day_schedule
                    })

            # Возвращаем расписание в формате JSON
            json_dump = json.dumps(schedule_data, ensure_ascii=False, indent=2)
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json_file.write(json_dump)
            print(f"Расписание для группы {group_id} успешно сохранено в JSON.")
        except Exception as e:
            print(f"Произошла ошибка при разборе HTML-разметки: {str(e)}")

    def get_group(self, group_id, headers):
        self.save_group_schedule_to_html(group_id, headers)
        self.parse_schedule_html(group_id)


group_parser = GroupParser()
