import json

import aiofiles
import aiohttp
import requests
from bs4 import BeautifulSoup

from Path.schedule_path_functions import find_group_dir_by_group_number, find_schedule_link_by_group_number, get_group_json_path_sync, \
    find_group_dir_by_group_number_sync, find_schedule_link_by_group_number_sync, get_group_json_path


async def load_group(group_id: int):
    """
        Asynchronously loads a group's schedule from the site, parses it, and saves it as a JSON file.

        :param group_id: The ID of the group to load the schedule for.
    """

    async def get_group_schedule_markup():
        """
        Asynchronously fetches and returns the HTML markup of the schedule for a specified group.

        :return: HTML markup of the schedule.
        """

        # Async call to find the group directory (though this example returns the markup,
        # keeping this for demonstration)
        group_dir = await find_group_dir_by_group_number(group_id)
        if not group_dir:
            raise FileNotFoundError(f"Directory for group {group_id} not found.")

        # Async call to find the schedule link
        schedule_link = await find_schedule_link_by_group_number(group_id)
        if not schedule_link:
            raise ValueError(f"Schedule link for group {group_id} not found.")

        # Perform an asynchronous HTTP GET request
        async with aiohttp.ClientSession() as session:
            async with session.get(schedule_link) as response:
                if response.status != 200:
                    raise ConnectionError(
                        f"Failed to load schedule for group {group_id}. Status code: {response.status}")

                html = await response.text()

        # Process the HTML content
        soup = BeautifulSoup(html, 'html.parser')
        schedule_div = soup.find('div', class_='collapse js-view-mode-container', id='table-container')
        if not schedule_div:
            raise ValueError("Schedule block not found on the page.")

        # Return the markup directly
        return str(schedule_div)

    async def parse_schedule_html(html, json_path):
        """
        Parses the HTML markup of a group's schedule and saves the schedule data in JSON format asynchronously.

        :param html: HTML markup of the schedule.
        :param json_path: Path where the JSON file should be saved.
        """
        if not html.strip():
            print(f"HTML markup for group {group_id} is empty.")
            return

        try:
            soup = BeautifulSoup(html, 'html.parser')
            day_blocks = soup.find_all('div', class_='card my-4')
            schedule_data = []

            for day_block in day_blocks:
                day_name = day_block.find('h3', class_='h5 my-0').text
                table = day_block.find('table', class_='table mb-0 table-responsive')
                day_schedule = []

                if table:
                    rows = table.find_all('tr')[1:]  # Skipping table header

                    for row in rows:
                        columns = row.find_all(['th', 'td'])
                        if len(columns) == 6:
                            time = columns[0].text.strip()
                            week = columns[1].find('i')['data-bs-title']
                            classroom_info = columns[2].text.strip()
                            classroom_parts = classroom_info.split()
                            classroom = {
                                'Корпус': classroom_parts[0],
                                'Номер аудитории': classroom_parts[1] if len(classroom_parts) == 2 else ''
                            }
                            group = columns[3].text.strip()
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
                            teacher_info = columns[5].text.strip().split()
                            teacher_dict = {
                                "Фамилия": teacher_info[0] if len(teacher_info) >= 1 else '',
                                "Имя": teacher_info[1] if len(teacher_info) >= 2 else '',
                                "Отчество": teacher_info[2] if len(teacher_info) >= 3 else ''
                            }

                            day_schedule.append({
                                'Время': time,
                                'Неделя': week,
                                'Аудитория': classroom,
                                'Группа': group,
                                'Предмет': subject_dict,
                                'Преподаватель': teacher_dict
                            })

                    schedule_data.append({
                        'День недели': day_name,
                        'Расписание': day_schedule
                    })

            # Asynchronously save the schedule data in JSON format
            json_dump = json.dumps(schedule_data, ensure_ascii=False, indent=2)
            async with aiofiles.open(json_path, 'w', encoding='utf-8') as json_file:
                await json_file.write(json_dump)
            print(f"Schedule for group {group_id} successfully saved in JSON.")
        except Exception as e:
            print(f"An error occurred while parsing the HTML markup: {str(e)}")

    markup = await get_group_schedule_markup()
    json_path = await get_group_json_path(group_id)

    await parse_schedule_html(markup, json_path)

    print(f"Schedule for group {group_id} has been successfully loaded and saved to {json_path}.")


def load_group_sync(group_id: int):
    """
    Synchronously loads a group's schedule from the site, parses it, and saves it as a JSON file.

    :param group_id: The ID of the group to load the schedule for.
    """

    def get_group_schedule_markup():
        """
        Synchronously fetches and returns the HTML markup of the schedule for a specified group.

        :return: HTML markup of the schedule.
        """
        # Synchronous call to find the group directory
        group_dir = find_group_dir_by_group_number_sync(group_id)
        if not group_dir:
            raise FileNotFoundError(f"Directory for group {group_id} not found.")

        # Synchronous call to find the schedule link
        schedule_link = find_schedule_link_by_group_number_sync(group_id)
        if not schedule_link:
            raise ValueError(f"Schedule link for group {group_id} not found.")

        # Perform a synchronous HTTP GET request
        response = requests.get(schedule_link)
        if response.status_code != 200:
            raise ConnectionError(f"Failed to load schedule for group {group_id}. Status code: {response.status_code}")

        return response.text

    def parse_schedule_html(html, json_path):
        """
        Parses the HTML markup of a group's schedule and saves the schedule data in JSON format synchronously.

        :param html: HTML markup of the schedule.
        :param json_path: Path where the JSON file should be saved.
        """
        soup = BeautifulSoup(html, 'html.parser')
        day_blocks = soup.find_all('div', class_='card my-4')  # Adjust class names as needed
        schedule_data = []

        for day_block in day_blocks:
            day_name = day_block.find('h3', class_='h5 my-0').text
            table = day_block.find('table', class_='table mb-0 table-responsive')
            day_schedule = []

            if table:
                rows = table.find_all('tr')[1:]  # Skipping table header

                for row in rows:
                    columns = row.find_all(['th', 'td'])
                    if len(columns) == 6:
                        time = columns[0].text.strip()
                        week = columns[1].find('i')['data-bs-title']
                        classroom_info = columns[2].text.strip()
                        classroom_parts = classroom_info.split()
                        classroom = {
                            'Корпус': classroom_parts[0],
                            'Номер аудитории': classroom_parts[1] if len(classroom_parts) == 2 else ''
                        }
                        group = columns[3].text.strip()
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
                        teacher_info = columns[5].text.strip().split()
                        teacher_dict = {
                            "Фамилия": teacher_info[0] if len(teacher_info) >= 1 else '',
                            "Имя": teacher_info[1] if len(teacher_info) >= 2 else '',
                            "Отчество": teacher_info[2] if len(teacher_info) >= 3 else ''
                        }

                        day_schedule.append({
                            'Время': time,
                            'Неделя': week,
                            'Аудитория': classroom,
                            'Группа': group,
                            'Предмет': subject_dict,
                            'Преподаватель': teacher_dict
                        })

                schedule_data.append({
                    'День недели': day_name,
                    'Расписание': day_schedule
                })

        # Saving the parsed data to a JSON file
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(schedule_data, json_file, ensure_ascii=False, indent=4)

    markup = get_group_schedule_markup()
    json_path = get_group_json_path_sync(group_id)  # Adjust to use the synchronous version

    parse_schedule_html(markup, json_path)

    print(f"Schedule for group {group_id} has been successfully loaded and saved to {json_path}.")
