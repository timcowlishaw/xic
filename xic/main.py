import datetime             # for timestamping
from pathlib import Path    # for handling file paths
import os                   # for interacting with the operating system
import sys                  # popping the hood on variables used or maintained by the interpreter

def get_current_timestamp():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace(':', '-')
# tweaked this code to replace colons with dashes because Windows can't handle colons in file names, apparently

# `Jotter` class initialised with a `login` parameter that
# generates a folder unique to each user in the `.xic` directory
# Jotter, here, is one of Xic's "tiny tools"
# a class is capitalised, which gives it a certain heft and substance
class Jotter:
    def __init__(self, login):
        self.folder_name = f"./.xic/{login}"

    # creates the folder if it doesn't exist already
    # wasn't sure what the `parents` boolean was doing; but it's to make sure directory hierarchies make sense
    # [?] as a function, could `create_folder_structure` be better named?
    # on the other hand, it does exactly what it says on the tin
    def create_folder_structure(self):
        path = Path(self.folder_name)
        path.mkdir(parents=True, exist_ok=True)

    # defines a method that takes the `fieldnote` and `timestamp` as parameters
    # no longer actually writes the fieldnote
    # instead, takes the argument and makes a phonecall to someone who knows _where_ the fieldnote should be written
    def write_fieldnote(self, fieldnote, timestamp):
        timestamp = get_current_timestamp()
        file_path = self.get_file_path()
        self.determine_append_or_create(file_path, fieldnote, timestamp)

    # [!] Pickard-added in-class function to get a `file_path`
    # that can be passed (?) as an argument (?) to other functions
    # should be most recently created/modified file, if it exists
    # [?] still have /literally/ no idea what a `lambda` function is λλλλλλλλ
    # a `lambda` is an anonymous function (how?); seems liminal, controversial within the Python community
    # "part syntactic sugar, part functional programming tool, part compromise between programming paradigms" (lol)
    def get_file_path(self):
        files = os.listdir(self.folder_name) # so far, so good; assigns a list of directory contents to `files`
        files.sort(key=lambda x: os.path.getctime(os.path.join(self.folder_name, x))) # paths, not just the file names (x)
        return os.path.join(self.folder_name, files[-1]) if files else None # this made my head hurt, didn't like it
        
    # [!] Pickard-created organisational function, for piping things in the right direction
    # [?] `file_path` is defined in `write_fieldnote`, but maybe that's ugly?
    def determine_append_or_create(self, file_path, fieldnote, timestamp): # [!] terrible, terrible name
        if self.should_append(file_path):
            self.append(file_path, fieldnote, timestamp)
        else:
            self.create_new_file(fieldnote, timestamp)

    # [!] Pickard-added in-class function to figure out whether the fieldnote should be appended or a new file
    # [?] Codestral is chastising me from not using an initial underscore in the function name; what's that about?
    # bracketing this out from the `write_fieldnote` method for cleanliness, and because it might need adjusting
    def should_append(self, file_path): # [?] do we need a better name for the 'should' bit of this function?
        if not file_path:
            return False # first and foremost, if the directory is empty, it must create a new file
        file_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
        now = datetime.datetime.now()
        return (now - file_time).total_seconds() < 25 * 60 # this is the mythical 25 minutes

    # [!] Pickard-added in-class function for appending fieldnotes to an existing file
    # wasn't clear where the `write` function came from, but it's a built-in Python function
    def append(self, file_path, fieldnote, timestamp): # keep this name as is, because 'a' is already an append mode
        with open(file_path, 'a') as file:
            file.write(f"\n\n---\n**{timestamp}**\n{fieldnote}")

    # [!] Pickard-added in-class function for creating a new fieldnote file
    # the LLMs have encouraged me to include this for symmetry
    # ensures that the logic for creating a new file is encapsulated in its own method
    # avoids the need for exceptions to the (presumed) default behaviour of creating a new file
    # the new note is titled with the retrieved timestamp; the "w" grants write permission
    def create_new_file(self, fieldnote, timestamp):
        with open(f"{self.folder_name}/{timestamp}.md", "w") as file:
            file.write(f"**{timestamp}**\n---\n{fieldnote}")

jotter = Jotter(os.getlogin())
jotter.create_folder_structure()
jotter.write_fieldnote(sys.argv[2], get_current_timestamp())

# no idea what `sys.argv[2]` is doing, at first glance; not the foggiest
# [?] okay, we know its a function that comes from the imported `sys` library, is it also an argument?
# no, it's a list / specifically, a list of arguments
# which get "passed" to the script (here, I'm imagining a bucket chain or relay baton)
# an argument is any value that is passed to the script when it's run from the command line
# and by having `sys.argv` as a list, rather than anything more structured or complicated
# it makes life easier (or, rather, more direct) for the programme's end user
# while leaving much of the interpretation and error handling to the developer
# so `sys.argv[2]` gets the second argument passed to the script, which is the fieldnote to be written (saved)