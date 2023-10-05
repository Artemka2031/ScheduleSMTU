import requests
from bs4 import BeautifulSoup
from pathlib import Path

from WebScraper import web_scraper
from GroupParser import group_parser

start_url = "https://www.smtu.ru/ru/"
main_page_name = "listschedule"

main_page_url = start_url + main_page_name + "/"


# Определите заголовки (headers)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 "
                  "Safari/537.36",  # Замените на свой пользовательский агент
    "Accept": "*/*",  # Пример: указание предпочтительных языков
}

# web_scraper.load_and_save_main_page(main_page_url, headers, main_page_name)

faculty_data_file_name = "faculty_data"
# web_scraper.parse_main_page(start_url, faculty_data_file_name)

# web_scraper.create_faculty_dirs()

# group_parser.save_group_schedule_to_html("2251", headers),


print(group_parser.parse_schedule_html("2251"))



# print(group_parser.find_group_dir_by_group_id("2251"))


