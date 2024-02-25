import json
from datetime import datetime, timedelta
import asyncio

import aiohttp
from bs4 import BeautifulSoup
from aiolimiter import AsyncLimiter

from Path.path_base import path_base

limiter = AsyncLimiter(10, 1)  # 10 запросов в секунду


async def fetch_page(url: str, session: aiohttp.ClientSession, params=None):
    async with limiter:
        async with session.get(url, params=params) as response:
            return await response.text()


async def parse_department_page(url: str, session: aiohttp.ClientSession):
    # Пример использования параметров запроса, если они необходимы
    params = {'example_param': 'value'}  # Пример параметров
    html = await fetch_page(url, session, params=params)
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
    async with aiohttp.ClientSession() as session:
        input_path = path_base.department_data
        output_path = path_base.employees_data

        with open(input_path, 'r', encoding='utf-8') as file:
            faculties_data = json.load(file)

        updated_faculties_data = await process_faculties(faculties_data, session)

        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(updated_faculties_data, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    asyncio.run(get_employees_data())
