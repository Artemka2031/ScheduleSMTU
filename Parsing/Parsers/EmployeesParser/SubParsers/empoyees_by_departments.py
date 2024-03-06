import json
from datetime import datetime, timedelta

import aiohttp
from aiolimiter import AsyncLimiter
from bs4 import BeautifulSoup

from Path.path_base import path_base

limiter = AsyncLimiter(10, 1)  # 10 запросов в секунду


async def fetch_page(url: str, session: aiohttp.ClientSession, params=None):
    """
    Asynchronously fetches the content of a webpage.

    Args:
        url (str): The URL of the page to fetch.
        session (aiohttp.ClientSession): The session used to make the HTTP request.
        params (dict, optional): Additional parameters to pass to the request. Defaults to None.

    Returns:
        str: The text content (HTML) of the fetched webpage.
    """
    async with limiter:
        async with session.get(url, params=params) as response:
            return await response.text()


async def parse_department_page(url: str, session: aiohttp.ClientSession):
    """
        Asynchronously parses the department page to extract employee data.

        Args:
            url (str): The URL of the department page to parse.
            session (aiohttp.ClientSession): The session used to fetch the page.

        Returns:
            list: A list of dictionaries, each containing data about an employee.
    """
    html = await fetch_page(url, session)
    soup = BeautifulSoup(html, 'html.parser')

    employees = []
    employee_id = 1

    employee_cards = soup.find_all(class_='card g-col-12 g-col-md-6 g-col-lg-5 g-col-xxl-4 text-bg-light')

    for card in employee_cards:
        full_name = card.find(class_='h5 text-info-dark').text.strip()
        names = full_name.split(' ')

        employee = {
            'id': employee_id,
            'surname': names[0],
            'name': names[1],
            'patronymic': names[2] if len(names) > 2 else '',
        }
        employees.append(employee)
        employee_id += 1

    return employees


async def process_faculties(faculties_data, session: aiohttp.ClientSession):
    """
       Asynchronously processes each faculty's departments to fetch and update employee data.

       Args:
           faculties_data (list): A list of faculty data dictionaries to be processed.
           session (aiohttp.ClientSession): The session used to make HTTP requests.

       Returns:
           list: The updated faculties data with employee information and last accessed timestamps.
    """
    department_count = 0  # Счётчик обработанных кафедр

    for faculty in faculties_data:
        for department in faculty['departments']:
            last_accessed = department.get('last_accessed', None)
            should_update = True

            if last_accessed:
                last_accessed_date = datetime.strptime(last_accessed, '%Y-%m-%d %H:%M:%S')
                should_update = datetime.now() - last_accessed_date > timedelta(days=1)

            if should_update:
                department_url = department['url']
                employees = await parse_department_page(department_url, session)
                department['Employees'] = employees
                department['last_accessed'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                department_count += 1
                print(
                    f"Faculty: {faculty['faculty']}, Department: {department['name']}, Departments processed: {department_count}")
    return faculties_data


async def get_employees_data():
    """
        The main asynchronous function to fetch and update employee data for all faculties and departments.

        This function orchestrates the fetching of faculty and department data, parsing of department pages to
        extract employee information, and updating the data with timestamps. The final updated data is saved
        to a JSON file.

        Utilizes global path configurations from `path_base` for input and output data.
    """
    async with aiohttp.ClientSession() as session:
        input_path = path_base.employees_data
        output_path = path_base.department_data

        with open(input_path, 'r', encoding='utf-8') as file:
            faculties_data = json.load(file)

        updated_faculties_data = await process_faculties(faculties_data, session)

        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(updated_faculties_data, file, ensure_ascii=False, indent=4)
