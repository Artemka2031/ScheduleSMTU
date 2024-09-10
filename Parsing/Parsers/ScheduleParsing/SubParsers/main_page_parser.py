import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from config import start_url


def get_main_page(main_page_url: str, headers: dict, save_directory: Path, main_page_file_path: Path,
                  faculty_data_file_path: Path, faculties_dir: Path):
    """
    Main function that orchestrates loading, parsing, and directory creation for the start_bot page.
    Nested functions use provided parameters to handle their specific tasks.

    Params:
    - main_page_url (str): URL of the start_bot page to fetch.
    - headers (dict): Request headers for the HTTP GET request.
    - save_directory (Path): Directory where the start_bot page HTML will be saved.
    - main_page_file_path (Path): Full path to save the start_bot page HTML file.
    - faculty_data_file_path (Path): Path to save the extracted faculty data as JSON.
    - faculties_dir (Path): Base directory where faculty and group directories will be created.
    """

    def load_and_save_main_page():
        """
        Fetches the start_bot page using requests and saves it to a file.
        """
        # Ensure the directory exists before saving
        save_directory.mkdir(parents=True, exist_ok=True)

        response = requests.get(main_page_url, headers=headers)
        if response.status_code == 200:
            html = response.text

            with open(main_page_file_path, 'w', encoding='utf-8') as file:
                file.write(html)
            print(f"Markup saved in {main_page_file_path}")
        else:
            print("Failed to load page. Status code:", response.status_code)

    def read_main_page():
        """
        Reads the content of the start_bot page from a file.
        """
        if main_page_file_path.is_file():
            with open(main_page_file_path, 'r', encoding='utf-8') as file:
                return file.read()
        else:
            print("Main markup file not found.")
            return ""

    def parse_main_page():
        """
        Parses the HTML content of the start_bot page and saves extracted data as JSON.
        """
        html_content = read_main_page()
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            faculty_data = {}

            h3_elements = soup.find_all('h3', style="clear:both;padding-top:10px;")

            for h3 in h3_elements:
                faculty_name = h3.text.strip()
                faculty_data[faculty_name] = []

                next_element = h3.find_next_sibling()
                while next_element and next_element.name != 'h3':
                    if next_element.name == 'div' and 'gr' in next_element.get('class', []):
                        group_name = next_element.a.text.strip()
                        group_link = next_element.a.get('href').replace('/ru/', '')
                        faculty_data[faculty_name].append({'group': group_name, 'link': start_url + group_link})
                    next_element = next_element.find_next_sibling()

            with open(faculty_data_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(faculty_data, json_file, ensure_ascii=False, indent=4)

            print(f"Data saved in {faculty_data_file_path}")
        else:
            print("HTML content is empty. Please provide valid HTML content for parsing.")

    def create_faculty_dirs():
        """
        Reads faculty data from a JSON file and creates directories for each faculty and group.
        """
        if faculty_data_file_path.is_file():
            with open(faculty_data_file_path, 'r', encoding='utf-8') as json_file:
                faculty_data = json.load(json_file)

            faculties_dir.mkdir(exist_ok=True)

            for faculty, groups in faculty_data.items():
                faculty_dir = faculties_dir / faculty
                faculty_dir.mkdir(exist_ok=True)

                for group_data in groups:
                    group_name = group_data['group']
                    group_dir = faculty_dir / group_name
                    group_dir.mkdir(exist_ok=True)

            print("Directories for Schedule and groups created in 'Schedule'.")
        else:
            print(f"File {faculty_data_file_path} not found. Execute data parsing first.")

    # Execute the nested functions in order
    load_and_save_main_page()
    parse_main_page()
    create_faculty_dirs()
