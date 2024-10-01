import datetime             # for timestamping
import logging              # for error logging
from logging.handlers import RotatingFileHandler    # like recording over old CCTV VHS tapes
from pathlib import Path    # for handling file paths
import os                   # for interacting with the operating system
import sys                  # popping the hood on variables used or maintained by the interpreter
import argparse             # for making the CLI a notch more flexible (versatile?)

# extra-class function definitions
def get_current_timestamp():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace(':', '-')
# tweaked this code to replace colons with dashes because Windows can't handle colons in file names, apparently

# [!] no idea what's going on here
def setup_logging():
    log_dir = os.path.join(os.path.expanduser('~'), '.xic', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'xic_errors.log')

    # might need to fiddle with the specific parameters here: timestamp, ERROR level, message
    # but also the calibration of the RotatingFileHandler
    # minimal approach to error logging means we might miss context that could be useful for debugging
    handler = RotatingFileHandler(log_file, maxBytes=1e6, backupCount=3)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger('xic')
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)

    return logger

logger = setup_logging()

# implementation of error logging
def log_error(e):
    logger.error(f"Error occurred: {str(e)}")

# fire-and-forget error handling, minimising interruptions and allowing devs to review files later
# silent error handling means users might not realise if/when something goes wrong
# [?] how do flag critical errors without breaking the user's flow?
def custom_error_handler(func):
    def wrapper(*args, **kwargs):   # [!] I've got a handle on *args, but don't know what a **kwarg is
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_error(e)            # log the error for later review
            return None             # return gracefully
    return wrapper

# not really sure what this is doing, beyond applying error-handling to the `jot` function
@custom_error_handler
def execute_jot(jotter, content):
    timestamp = get_current_timestamp()
    jotter.write_fieldnote(" ".join(content), timestamp)

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
    # removed the timestamp-fetch, and am now handling this when the `jot` argument is invoked
    # instead, takes the argument and makes a phonecall to someone who knows _where_ the fieldnote should be written
    def write_fieldnote(self, fieldnote, timestamp):
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
    # [?] the mythical 25 minutes is currently hard-coded; should it be configurable?
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

# parser setup
def setup_argparse(): # [?] don't need to point it at itself?
    parser = argparse.ArgumentParser(description="Xic: Tiny tools for thick description")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Jotter subcommands
    # [?] `jotter` vs. `jot` as a name for this subparser?
    # [?] what does `nargs="+"` do? glues the different words together despite spaces?
    # [!] risk of this losing multiple spaces between words, but when would that be salient in this use case
    jotter_parser = subparsers.add_parser("jot", help="Create a new jotting")
    jotter_parser.add_argument("content", nargs="+", help="The content of the jotting")

    # future subcommands
    prompt_parser = subparsers.add_parser("prompt", help="Future: Event-triggered structured elicitation prompts")
    # placeholder arguments for future development
    prompt_parser.add_argument("--event", help="Specify the triggering event (placeholder)")

    parse_parser = subparsers.add_parser("parse", help="Future: Parse pseudo-ethnographic in-line code comments")
    # placeholder arguments for future development
    parse_parser.add_argument("--file", help="Specify the file to parse (placeholder)")

    return parser

def jot_command(args):
    jotter = Jotter(os.getlogin())
    jotter.create_folder_structure()
    execute_jot(jotter, args.content)
    # [?] how does this instruction differ from passing the second argument in the list, as before?
    # it's been encapsulatedddddddddd
    # currently no visible confirmation when a jotting has been successfully jotted, which might be an issue

def prompt_command(args):
    print("Prompter in development. Future versions of Xic will provide structured elicitation cues.")

def parse_command(args):
    print("Parser not yet available. This tool will pull code comments for ethnographic insights.")

# main execution
# first line ensures the code only runs when the script is executed directly, not when imported as a module
if __name__ == "__main__":
    try:
        parser = setup_argparse()
        args = parser.parse_args()
        jotter = None

        # added lazy jotter initialisation, such that the function is only summoned if needed
        # which won't always be the case in future
        # a step towards a more modular, symmetrical design for Xic
        if args.command == "jot":
            jot_command(args)
        elif args.command == "prompt":
            prompt_command(args)
        elif args.command == "parse": 
            parse_command(args)
        else:
            parser.print_help()
    except Exception as e:
        log_error(e)
        print(f"An error occurred: {str(e)}") # provide feedback to the user (it's only polite)
        # [!?] have we implemented a global error-handling function?
        # we have, but it's selectively applied