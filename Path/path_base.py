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
    department_data: Path
    employees_data: Path

    def __init__(self):
        self.cwd = Path("/root/SMTU/ScheduleSMTU")
        self.parsing = self.cwd / Path("Parsing")
        self.data = self.parsing / Path("Data")

        self.save_directory = self.data / Path("ScheduleByFaculties")
        self.schedule_smtu_dir = self.save_directory / Path("ScheduleSMTU")
        self.main_page = self.save_directory / "listschedule.html"
        self.faculty_data = self.save_directory / "faculty_data.json"
        self.faculties_dir = self.save_directory / "Schedule"
        self.schedule_smtu_json = self.schedule_smtu_dir / 'Schedule_smtu.json'
        self.schedule_smtu_min_json = self.schedule_smtu_dir / 'Schedule_smtu.min.json'

        self.employees_dir = self.data / Path("EmployeesByFaculties")
        self.department_data = self.employees_dir / "department_data.json"
        self.employees_data = self.employees_dir / "employees_data.json"

        self.db_path = self.cwd / Path("ORM") / Path("database.db")
        self.db_backups = self.cwd / Path("ORM") / Path("BackUps")


path_base = PathBase()
