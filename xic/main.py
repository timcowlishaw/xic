import datetime             # for timestamping
from pathlib import Path    # for handling file paths
import os                   # for interacting with the operating system
import sys                  # popping the hood on variables used or maintained by the interpreter

def get_current_timestamp():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()

# `Jotter` class initialised with a `login` parameter that
# generates a folder unique to each user in the `.xic` directory
# Jotter, here, is one of Xic's "tiny tools"
# a class is capitalised, which gives it a certain heft and substance
class Jotter:
    def __init__(self, login):
        self.folder_name = f"./.xic/{login}"

    # creates the folder if it doesn't exist already
    # [?] not sure what the `parents` boolean is doing here; need to investigate
    # [?] as a function, could `create_folder_structure` be better named?
    # on the other hand, it does exactly what it says on the tin
    def create_folder_structure(self):
        path = Path(self.folder_name)
        path.mkdir(parents=True, exist_ok=True)

    # defines a method that takes the `fieldnote` and `timestamp` as parameters
    # the note is titled with the retrieved timestamp; the "w" grants write permission
    # [?] where did the `write` function come from?
    def write_fieldnote(self, fieldnote, timestamp):
        with open(f"{self.folder_name}/{timestamp}.md", "w") as file:
            file.write(fieldnote)


jotter = Jotter(os.getlogin())
jotter.create_folder_structure()
jotter.write_fieldnote(sys.argv[2], get_current_timestamp())

# no idea what `sys.argv[2]` is doing, at first glance; not the foggiest
# [?] okay, we know its a function that comes from the imported `sys` library, is it an argument?
# no, it's a list / specifically, a list of arguments
# which get "passed" to the script (I'm imagining a bucket chain or relay baton)
# [?] but what is an argument?
# any value that is passed to the script when it's run from the command line
# and by having `sys.argv` as a list, rather than anything more structured or complicated
# it makes life easier (or, rather, more direct) for the programme's end user
# while leaving much of the interpretation and error handling to the developer
# so `sys.argv[2]` gets the second argument passed to the script, which is the fieldnote to be written (saved)