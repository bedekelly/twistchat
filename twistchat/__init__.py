"""
Check whether the config file exists before running the program.
"""

if not os.path.exists("~/.twistchat/twistchat.yml"):
    print("""
          Doesn't look like you've set up your config file yet!
          There's an example config file here:
              ~/.twistchat/twistchat.yml.example .\n"
          Go ahead and copy it over to ~/.twistchat/twistchat.yml when you're
          done.
          """)
    exit(1)
