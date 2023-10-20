import json
import os
import subprocess
import threading
import time
from multiprocessing import Pool


def run_command(path):
    command = "screen python3 {}".format(path)

    subprocess.Popen(command, shell=True)


if __name__ == "__main__":
    json_file_path = "../files.json"
    # Load the file paths from the JSON file
    with open(json_file_path, "r") as f:
        file_paths = json.load(f)
    flag = 1
    # Validate that the file paths exist
    for file_path in file_paths:
        if not os.path.exists(file_path):
            flag = 0
            raise ValueError(f"File path does not exist: {file_path}")
    # check if all paths are correct
    if flag:
        # pool for different python scripts
        with open("../config.json", "w") as fp:
            pass
        with open("../log.txt", "w") as f:
            pass

        pool = Pool()
        pool.map(run_command, file_paths)
