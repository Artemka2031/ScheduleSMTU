import json
import time

from Parsing import get_main_page
from Parsing.GroupParser import get_group
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
#     get_group(group)
#     time.sleep(1)

# Создание папки с расписанием в папке расписания
# group_data.create_smtu_schedule()

print(get_group_json_path(2251))

