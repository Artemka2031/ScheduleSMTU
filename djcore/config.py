start_url = "https://www.smtu.ru/ru/"
main_page_name = "listschedule"
employee_page_name = "listdepartment"

main_page_url = start_url + main_page_name + "/"
employee_page_url = start_url + employee_page_name + "/"

# Определите заголовки (headers)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 "
                  "Safari/537.36",  # Замените на свой пользовательский агент
    "Accept": "*/*",  # Пример: указание предпочтительных языков
}

token = {
    # "token": "6397282799:AAG-kCn6jHua9W9y48L20K_IDM-5kPEY3P0"  # Токен от бота @MyNewTestBotAbot.
    "token": "6523290565:AAGn4cBjfaZjmvFXhEJs9ZYNN6Y2p812gkE"  # Токен от бота  @legoduplo_bot.
    # "token": "6999923210:AAHB6YtJLw7J8CWH3HKPD3sf6MiF-NkZpzU"
    # "token": "6810756058:AAGRxAoevM-v63XJRLzoCSsW3N7bBFv40f4" # Токен от бота @ScheduleSMTU_bot
}
