import asyncio

from Parsing.Parsers.ScheduleParsing import get_main_page, load_group, create_schedule_file
from Path.schedule_path_functions import get_all_group_numbers, path_base
from config import main_page_url, headers


async def load_group_with_rate_limiting(group, semaphore):
    """
    Wrapper around load_group to use with rate limiting.
    """
    async with semaphore:
        await load_group(group)


async def main():
    # Synchronously get main page and parse all group numbers
    get_main_page(main_page_url, headers, path_base.save_directory, path_base.main_page, path_base.faculty_data,
                  path_base.faculties_dir)
    groups = get_all_group_numbers()

    # # Create a semaphore to limit the number of concurrent load_group calls to 20
    # semaphore = asyncio.Semaphore(5)
    #
    # # Schedule load_group calls for each group with rate limiting
    # tasks = [load_group_with_rate_limiting(group, semaphore) for group in groups]
    # await asyncio.gather(*tasks)
    #
    # # Once all groups are processed, create the schedule directory
    # await create_schedule_file()


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
