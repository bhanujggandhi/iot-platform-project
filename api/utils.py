import os
from zipfile import ZipFile


def verify_zip(path: str):
    with ZipFile(path) as zip_file:
        filelist = []
        for member in zip_file.namelist():
            member = member.split("/")
            if member[1] == "main.py":
                # os.remove(path)
                # Upload to cloud
                return True

        os.remove(path)
        return False
