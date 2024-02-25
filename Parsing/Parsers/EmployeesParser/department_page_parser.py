import json

import requests
from bs4 import BeautifulSoup

from Path.path_base import path_base
from config import employee_page_url, start_url


def get_department_page(url, path, employees_directory=path_base.employees_dir):
    def fetch_section_markup(url):
        """Получение необходимой разметки с веб-страницы."""
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        target_h2 = soup.find('h2', class_='h3 pt-4 mb-2',
                              string="ГРУППА СТРУКТУРНЫХ ПОДРАЗДЕЛЕНИЙ, ПОДЧИНЕННЫХ ПРОРЕКТОРУ ПО ОБРАЗОВАТЕЛЬНОЙ "
                                     "ДЕЯТЕЛЬНОСТИ")
        parent_div = target_h2.find_next_sibling('div', class_='card mb-4')
        return parent_div

    def parse_section_to_json(parent_div):
        """Parses the markup and forms data into JSON format."""
        faculties_data = []
        # Find all faculty titles
        faculty_titles = parent_div.find_all('h3', class_='h5 mt-4')

        for faculty_title in faculty_titles:
            faculty_name = faculty_title.text.strip()
            departments = []

            # Immediately following ul contains the departments for this faculty
            departments_list = faculty_title.find_next_sibling('ul', class_='list-group list-group-flush mt-3')
            if departments_list:
                for li in departments_list.find_all('li', class_='list-group-item'):
                    department_name = li.find('h4', class_='h6').text.strip()
                    department_url = li.find('a')['href']
                    department_url = department_url.replace('/ru/', '')
                    department_url = start_url + department_url
                    departments.append({'name': department_name, 'url': department_url})

            faculties_data.append({'faculty': faculty_name, 'departments': departments})

        return faculties_data

    parent_div = fetch_section_markup(url)
    data = parse_section_to_json(parent_div)

    employees_directory.mkdir(parents=True, exist_ok=True)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    get_department_page(employee_page_url, path_base.department_data)


main()  # Вызов основной функции закомментирован для предотвращения автоматического выполнения
