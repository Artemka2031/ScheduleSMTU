import asyncio
from aiohttp import ClientSession
from Parsing.Parsers.ScheduleParsing.SubParsers import load_group, get_main_page, create_schedule_file
from Path.path_base import path_base
from Path.schedule_path_functions import get_all_group_numbers
from config import main_page_url, headers


async def load_group_with_rate_limiting(group: str, semaphore: asyncio.Semaphore):
    """
    Asynchronously loads schedule data for a specified group, adhering to a rate limit.

    Args:
        group (str): Identifier of the group to load schedule data for.
        semaphore (asyncio.Semaphore): Controls the concurrency level to enforce rate limiting.
    """
    async with semaphore:
        await load_group(group)


async def set_schedule_data():
    """
    Orchestrates the asynchronous fetching and setting of schedule data for all groups listed on the start_bot page.

    Steps performed:
    1. Synchronously fetches the start_bot page and parses all group numbers.
    2. Initializes a semaphore to limit the number of concurrent `load_group` operations.
    3. Asynchronously schedules and executes `load_group` calls for each group within the rate limit.
    4. Upon completion of all group data fetching, generates the final schedule file.

    Configuration for fetching and file generation are obtained from global settings, including URLs, headers, and file paths.
    """
    # Fetch the start_bot page and parse group numbers synchronously
    get_main_page(main_page_url, headers, path_base.save_directory, path_base.main_page, path_base.faculty_data,
                  path_base.faculties_dir)
    groups = get_all_group_numbers()

    # Establish a semaphore to limit concurrent load_group operations to 20
    semaphore = asyncio.Semaphore(20)

    # Asynchronously schedule and execute load_group calls within rate limits
    tasks = [load_group_with_rate_limiting(group, semaphore) for group in groups]
    await asyncio.gather(*tasks)

    # Finalize by creating the schedule file after all groups have been processed
    await create_schedule_file()


if __name__ == "__main__":
    asyncio.run(set_schedule_data())
