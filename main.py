import json
import time

from Parsing import get_main_page
from Parsing.GroupParser import load_group_from_site
from Paths import get_all_group_numbers, get_group_json_path

start_url = "https://www.smtu.ru/ru/"
main_page_name = "listschedule"

main_page_url = start_url + main_page_name + "/"

# Загрузка расписания в свои папки
# get_main_page()

# Парсинг всех групп и запись в свои папки
# groups = get_all_group_numbers()
#
# for group in groups:
#     load_group_from_site(group)
#     time.sleep(1)

# Создание папки с расписанием в папке расписания
# group_data.create_smtu_schedule()


