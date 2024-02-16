from pathlib import Path


class PathBase:
    cwd: Path
    parsing: Path
    data: Path

    save_directory: Path
    schedule_smtu_dir: Path
    main_page: Path
    faculty_data: Path
    faculties_dir: Path
    schedule_smtu_json: Path
    schedule_smtu_min_json: Path
    db_path: Path

    employees_dir: Path
    employees_main_page: Path
    employees_data: Path

    def __init__(self):
        self.cwd = Path("C:/Users/perei/PycharmProjects/ScheduleSMTU")
        self.parsing = self.cwd / Path("Parsing")
        self.data = self.cwd / Path("Data")

        self.save_directory = self.data / Path("ScheduleByFaculties")
        self.schedule_smtu_dir = self.save_directory / Path("ScheduleSMTU")
        self.main_page = self.save_directory / "listschedule.html"
        self.faculty_data = self.save_directory / "faculty_data.json"
        self.faculties_dir = self.save_directory / "Schedule"
        self.schedule_smtu_json = self.schedule_smtu_dir / 'Schedule_smtu.json'
        self.schedule_smtu_min_json = self.schedule_smtu_dir / 'Schedule_smtu.min.json'

        self.employees_dir = self.data / Path("EmployeesByFaculties")
        self.employees_main_page = self.employees_dir / "employees_main_page.html"
        self.employees_data = self.employees_dir / "employees_data.json"


path_base = PathBase()
