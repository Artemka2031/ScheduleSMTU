import json

import requests
from bs4 import BeautifulSoup

from Path.path_base import path_base
from config import employee_page_url


def get_employee_page(url, path):
    def fetch_section_markup(url):
        """Получение необходимой разметки с веб-страницы."""
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        target_h2 = soup.find('h2', class_='h3 pt-4 mb-2',
                              text="ГРУППА СТРУКТУРНЫХ ПОДРАЗДЕЛЕНИЙ, ПОДЧИНЕННЫХ ПРОРЕКТОРУ ПО ОБРАЗОВАТЕЛЬНОЙ ДЕЯТЕЛЬНОСТИ")
        parent_div = target_h2.find_next_sibling('div', class_='card mb-4')
        return parent_div

    def parse_section_to_json(parent_div):
        """Парсинг разметки и формирование данных в формате JSON."""
        faculties_data = []
        for card_body in parent_div.find_all('div', class_='card-body'):
            faculty_name = card_body.find('h3', class_='h5 mt-4').text.strip()
            departments = []
            for li in card_body.find_all('li', class_='list-group-item'):
                department_name = li.find('h4', class_='h6').text.strip()
                department_url = li.find('a')['href']
                departments.append({'name': department_name, 'url': department_url})
            faculties_data.append({'faculty': faculty_name, 'departments': departments})
        return faculties_data

    def write_json(data, path):
        """Запись данных в файл JSON."""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    parent_div = fetch_section_markup(url)
    data = parse_section_to_json(parent_div)
    write_json(data, path)


def main():
    get_employee_page(employee_page_url, path_base.employees_data)

main() # Вызов основной функции закомментирован для предотвращения автоматического выполнения
