import asyncio

from .SubParsers import get_employees_data, get_department_page


async def fetch_employees_data():
    """
    Orchestrates the fetching and processing of university department and employee data.

    This function sequentially calls:
    1. get_department_page() to fetch and save data about departments.
    2. get_employees_data() to fetch and save data about employees within each department.

    Error handling is implemented to ensure graceful degradation in case of failures.
    """
    try:
        # Step 1: Fetch and process department page
        print("Starting to fetch department data...")
        get_department_page()
        print("Department data fetched and saved successfully.")

        # Step 2: Fetch and process employee data
        print("Starting to fetch employees data...")
        await get_employees_data()  # This function is asynchronous
        print("Employees data fetched and saved successfully.")

    except Exception as e:
        # Basic error handling, log or handle errors as appropriate for your use case
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(fetch_employees_data())
