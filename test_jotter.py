import datetime
import os
import subprocess
import unittest

class JotterTest(unittest.TestCase):
    def test_jotter(self):
        username = os.getlogin()
        timestamp = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
        result = subprocess.run(["./bin/xic", "jot", "This is a test fieldnote"])
        assert result.returncode == 0
        with open(f".xic/{username}/{timestamp}.md") as file:
            result = file.read()
        assert "This is a test fieldnote" in result