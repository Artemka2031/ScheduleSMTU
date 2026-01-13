import json

import aiofiles

from apps.database.utils.Path.path_base import path_base


async def get_group_json_path(group_number):
    """
    Asynchronously get the JSON file path for a given group number.

    :param group_number: The group number for which to find the JSON file path.
    :return: The path to the JSON file if the group directory exists, None otherwise.
    """
    # Assuming find_group_dir_by_group_number is now an async function
    group_dir = await find_group_dir_by_group_number(group_number)
    if group_dir:
        json_file_name = f"{group_number}.json"
        json_file_path = group_dir / json_file_name
        return json_file_path
    else:
        print(f"Directory for group {group_number} not found.")
        return None


def get_group_json_path_sync(group_number):
    """
    Get the JSON file path for a given group number synchronously.

    :param group_number: The group number for which to find the JSON file path.
    :return: The path to the JSON file if the group directory exists, None otherwise.
    """
    group_dir = find_group_dir_by_group_number_sync(group_number)  # Assuming this is now a synchronous call
    if group_dir:
        json_file_name = f"{group_number}.json"
        json_file_path = group_dir / json_file_name  # Ensure that group_dir is a Path object for this to work
        return json_file_path
    else:
        print(f"Directory for group {group_number} not found.")
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


async def find_schedule_link_by_group_number(group_number):
    """
    Asynchronously finds the schedule link for a given group number by reading through a JSON file.

    :param group_number: The group number to find the schedule link for.
    :return: The schedule link as a string if found, otherwise None.
    """
    group_number = str(group_number)
    json_file_path = path_base.faculty_data

    if json_file_path.is_file():
        # Asynchronously read from the JSON file
        async with aiofiles.open(json_file_path, 'r', encoding='utf-8') as json_file:
            faculty_data = json.loads(await json_file.read())

        # Search for the schedule link by group number
        for faculty, groups in faculty_data.items():
            for group_data in groups:
                if 'group' in group_data and 'link' in group_data:
                    if group_data['group'] == group_number:
                        return group_data['link']

    return None


def find_schedule_link_by_group_number_sync(group_number):
    """
    Synchronously finds the schedule link for a given group number by reading through a JSON file.

    :param group_number: The group number to find the schedule link for.
    :return: The schedule link as a string if found, otherwise None.
    """
    group_number = str(group_number)
    json_file_path = path_base.faculty_data

    if json_file_path.is_file():
        try:
            # Synchronously read from the JSON file
            with open(json_file_path, 'r', encoding='utf-8') as json_file:
                faculty_data = json.load(json_file)

            # Search for the schedule link by group number
            for faculty, groups in faculty_data.items():
                for group_data in groups:
                    if 'group' in group_data and 'link' in group_data:
                        if group_data['group'] == group_number:
                            return group_data['link']
        except Exception as e:
            print(f"An error occurred while searching for the schedule link for group number {group_number}: {e}")

    return None


async def find_group_dir_by_group_number(group_number):
    """
    Asynchronously finds the directory for a given group number by reading and searching through a JSON file.

    :param group_number: The group number to find the directory for.
    :return: A Path object pointing to the group's directory if found.
    """
    group_number = str(group_number)

    # Check if the JSON file with faculty and group data exists
    if not path_base.faculty_data.is_file():
        raise FileNotFoundError("JSON file with faculty and group data not found.")

    try:
        # Asynchronously read from the JSON file
        async with aiofiles.open(path_base.faculty_data, 'r', encoding='utf-8') as json_file:
            faculty_data = json.loads(await json_file.read())

        # Search for the group by number in the faculty and group data
        for faculty, groups in faculty_data.items():
            for group_data in groups:
                if 'group' in group_data and 'link' in group_data:
                    if group_data['group'] == group_number:
                        group_dir = path_base.faculties_dir / faculty / group_number
                        # Asynchronous check for directory existence might not be directly available,
                        # so this remains a synchronous operation
                        if group_dir.is_dir():
                            return group_dir

        raise FileNotFoundError(f"Directory for group {group_number} not found.")
    except FileNotFoundError as e:
        raise e
    except Exception as e:
        raise Exception(f"An error occurred while searching for the group directory {group_number}: {str(e)}")


def find_group_dir_by_group_number_sync(group_number):
    """
    Finds the directory for a given group number by reading and searching through a JSON file.

    :param group_number: The group number to find the directory for.
    :return: A Path object pointing to the group's directory if found, raises FileNotFoundError otherwise.
    """
    group_number = str(group_number)

    # Check if the JSON file with faculty and group data exists
    if not path_base.faculty_data.is_file():
        raise FileNotFoundError("JSON file with faculty and group data not found.")

    try:
        # Synchronously read from the JSON file
        with open(path_base.faculty_data, 'r', encoding='utf-8') as json_file:
            faculty_data = json.load(json_file)

        # Search for the group by number in the faculty and group data
        for faculty, groups in faculty_data.items():
            for group_data in groups:
                if 'group' in group_data and 'link' in group_data:
                    if group_data['group'] == group_number:
                        group_dir = path_base.faculties_dir / faculty / group_number
                        if group_dir.is_dir():
                            return group_dir

        raise FileNotFoundError(f"Directory for group {group_number} not found.")
    except FileNotFoundError as e:
        raise e
    except Exception as e:
        raise Exception(f"An error occurred while searching for the group directory {group_number}: {str(e)}")


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
