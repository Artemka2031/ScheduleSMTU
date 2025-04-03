import os
import subprocess

def main():
    project_dir = os.path.abspath(".")
    command = ["docker-compose", "up", "-d", "--build"]
    subprocess.Popen(command, cwd=project_dir)

if __name__ == '__main__':
    main()