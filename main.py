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

# web_scraper.load_and_save_main_page(main_page_url, headers)
#
# web_scraper.parse_main_page(start_url)
#
# web_scraper.create_faculty_dirs()

print(len(group_parser.get_all_group_numbers()))
# group_parser.get_group(group, headers)




