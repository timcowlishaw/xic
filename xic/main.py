import datetime
from pathlib import Path
import os
import sys

def get_current_timestamp():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()

class Jotter:
    def __init__(self, login):
        self.folder_name = f"./.xic/{login}"

    def create_folder_structure(self):
        path = Path(self.folder_name)
        path.mkdir(parents=True, exist_ok=True)

    def write_fieldnote(self, fieldnote, timestamp):
        with open(f"{self.folder_name}/{timestamp}.md", "w") as file:
            file.write(fieldnote)


jotter = Jotter(os.getlogin())
jotter.create_folder_structure()
jotter.write_fieldnote(sys.argv[2], get_current_timestamp())
