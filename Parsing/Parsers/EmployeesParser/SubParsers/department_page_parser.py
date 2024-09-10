import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from Path.path_base import path_base
from config import employee_page_url, start_url  # Предполагается, что config.py содержит начальные URL


def get_department_page(url=employee_page_url, path=path_base.employees_data,
                        employees_directory=path_base.employees_dir):
    """
    Fetches and processes the department page from the specified URL to extract faculty and department information,
    then saves the data as JSON.

    Args:
        url (str): URL of the department page to process. Defaults to employee_page_url from config.
        path (Path): Path object where the JSON data will be saved. Defaults to path_base.employees_data.
        employees_directory (Path): Directory to save the JSON file. Defaults to path_base.employees_dir.
    """

    def fetch_section_markup(url):
        """Fetches the necessary markup from the web page."""
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
        faculty_titles = parent_div.find_all('h3', class_='h5 mt-4')

        for faculty_title in faculty_titles:
            faculty_name = faculty_title.text.strip()
            departments = []

            if faculty_name != "Колледж СПбГМТУ (СТФ)":
                departments_list = faculty_title.find_next_sibling('ul', class_='list-group list-group-flush mt-3')

                if departments_list:
                    for li in departments_list.find_all('li', class_='list-group-item'):
                        department_name = li.find('h4', class_='h6').text.strip()
                        department_url = li.find('a')['href']
                        department_url = department_url.replace('/ru/', '')
                        department_url = start_url + department_url
                        departments.append({'name': department_name, 'url': department_url})

                faculties_data.append({'faculty': faculty_name, 'departments': departments})
            else:
                department_url = faculty_title.find('a')['href']
                department_url = department_url.replace('/ru/', '')
                department_url = start_url + department_url
                faculties_data.append(
                    {'faculty': faculty_name, 'departments': [{'name': 'Колледж СПбГМТУ (СТФ)', 'url': department_url}]})

        return faculties_data

    parent_div = fetch_section_markup(url)
    data = parse_section_to_json(parent_div)

    # Ensure the directory exists before saving the file
    employees_directory.mkdir(parents=True, exist_ok=True)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
