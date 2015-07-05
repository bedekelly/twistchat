"""
Check whether the config file exists before running the program.
"""
import os.path
from pkg_resources import Requirement, resource_filename

# TODO: Look into making this dependent on the package attributes.
from .misc import CONFIG_PATH

if not os.path.exists(CONFIG_PATH):
    print("""
          Doesn't look like you've set up your config file yet!
          There's an example config file here:
              ~/.twistchat/twistchat.yml.example .\n"
          Go ahead and copy it over to ~/.twistchat/twistchat.yml when you're
          done.
          """)
    exit(1)
