import asyncio

from .Parsers import fetch_employees_data, set_schedule_data


async def parsing():
    print("Starting university data parsing...")

    try:
        print("Fetching employees data from faculties and departments...")
        await fetch_employees_data()
        print("Successfully fetched employees data.")
    except Exception as e:
        print(f"An error occurred while fetching employees data: {e}")
        # Дополнительные действия при возникновении ошибки (например, логгирование или повторный вызов)
        return  # Прерывание выполнения, если обработка данных о сотрудниках не удалась

    try:
        print("Setting schedule data for all available groups...")
        await set_schedule_data()
        print("Successfully set schedule data for all groups.")
    except Exception as e:
        print(f"An error occurred while setting schedule data: {e}")
        # Дополнительные действия при возникновении ошибки
        return  # Прерывание выполнения, если установка расписания не удалась

    print("University data parsing completed successfully.")


if __name__ == "__main__":
    asyncio.run(parsing())
