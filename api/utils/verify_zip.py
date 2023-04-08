import os
from zipfile import ZipFile


def verify_zip(path: str):
    """
    Function to verify if the must have files mentioned in docs/deployement.md are present
    """
    filechecks = {"requirements.txt": False, "main.py": False, "package.json": False}
    with ZipFile(path) as zip_file:
        for member in zip_file.namelist():
            member = member.split("/")
            if member[1] in filechecks.keys():
                filechecks[member[1]] = True

    if False in filechecks.values():
        return False
    else:
        return True
