import json
import aiofiles

from Path.schedule_path_functions import get_group_json_path_sync, get_group_json_path
from Path.path_base import path_base


async def create_schedule_file():
    """
        Synchronously creates a schedule file containing the compiled schedules for all Schedule and groups.

        This function performs several key operations:
        1. Checks if the JSON file with faculty and group data exists. If not, it raises a FileNotFoundError.
        2. Reads the faculty and group data from the JSON file synchronously to avoid blocking.
        3. Iterates through each faculty and their respective groups, fetching the group's schedule synchronously.
        4. Compiles all fetched schedules into a single dictionary, organized by faculty and group.
        5. Creates the necessary directory (if it doesn't exist) to store the compiled schedule files.
        6. Writes two versions of the compiled schedule to the filesystem:
           - A pretty-printed JSON file for human readability.
           - A minified JSON file for efficient storage and transfer.

        The function handles FileNotFoundError for missing data files and catches general exceptions
        to report errors encountered during the schedule compilation process.

        Preconditions:
        - The faculty and group data JSON file must exist at the specified path.
        - All group schedules must be accessible and in a format that can be parsed into JSON.

        Postconditions:
        - Two JSON files (`Schedule_smtu.json` and `Schedule_smtu.min.json`) are created in the specified directory.
        - The directory structure necessary to store the files is ensured to exist.

        Raises:
        - FileNotFoundError: If the faculty and group data JSON file does not exist.
        - Exception: For any other errors encountered during execution.
        """
    try:
        # Check if the JSON file with faculty and group data exists
        if not path_base.faculty_data.is_file():
            raise FileNotFoundError("JSON file with faculty and group data not found.")

        # Asynchronously open and read the JSON file with faculty and group data
        async with aiofiles.open(path_base.faculty_data, 'r', encoding='utf-8') as json_file:
            faculty_data = json.loads(await json_file.read())

        schedule_data = {}

        for faculty, groups in faculty_data.items():
            faculty_schedule = {}
            for group_data in groups:
                if 'group' in group_data and 'link' in group_data:
                    group_id = group_data['group']
                    link = group_data['link']

                    schedule_path = await get_group_json_path(group_id)
                    async with aiofiles.open(schedule_path, 'r', encoding='utf-8') as schedule_file:
                        schedule = json.loads(await schedule_file.read())

                    faculty_schedule[group_id] = {
                        'link': link,
                        'schedule': schedule
                    }

            schedule_data[faculty] = faculty_schedule

        # Create the directory if it doesn't exist
        path_base.schedule_smtu_dir.mkdir(parents=True, exist_ok=True)

        # Asynchronously write the Schedule_smtu.json file
        file_path = path_base.schedule_smtu_dir / 'Schedule_smtu.json'
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as schedule_file:
            await schedule_file.write(json.dumps(schedule_data, ensure_ascii=False, indent=4))

        file_path = path_base.schedule_smtu_dir / 'Schedule_smtu.min.json'
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as schedule_file:
            await schedule_file.write(json.dumps(schedule_data, ensure_ascii=False, separators=(',', ':')))

    except FileNotFoundError as e:
        raise e
    except Exception as e:
        raise Exception(f"An error occurred while creating the schedule file: {str(e)}")
