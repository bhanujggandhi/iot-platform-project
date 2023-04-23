import hashlib
import os
from zipfile import ZipFile


def verify_zip(path: str):
    """
    Function to verify if the must have files mentioned in docs/deployement.md are present and create hash for all the files to verify the version
    """
    sha256_hash = hashlib.sha256()
    filechecks = {
        "requirements.txt": False,
        "main.py": False,
        "package.yml": False,
        "sensor_info.yml": False,
        "schedule.yml": False,
    }
    with ZipFile(path, "r") as zip_file:
        for member in zip_file.namelist():
            with zip_file.open(member) as file:
                file_contents = file.read()
                sha256_hash.update(file_contents)
            member = member.split("/")
            if member[1] in filechecks.keys():
                filechecks[member[1]] = True

    if False in filechecks.values():
        return False
    else:
        return sha256_hash.hexdigest()
