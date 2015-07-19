#!/usr/bin/env python3

import os
from setuptools import setup
from os.path import expanduser as path_to

if os.geteuid() == 0:
    raise PermissionError("Don't install as root!\n\n"
                          "This script installs example configuration"
                          " files in your home directory.\n"
                          "To install, use the `--user` option:\n"
                          "\tpip3 install --user twistchat\nOr:\n"
                          "\tpython3 setup.py install --user")

setup(name='TwistChat',
      version='0.1.0',
      description='Chatroom server written using Twisted',
      license='The Unlicense',
      author='Bede Kelly',
      author_email='admin@bede.club',
      maintainer='Bede Kelly',
      maintainer_email='admin@bede.club',
      entry_points={'console_scripts': "twistchat = twistchat.server:main"},
      keywords=['irc', 'chatroom', 'server', 'webchat'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Communications',
          'Topic :: Communications :: Chat :: Internet Relay Chat',
          ],
      data_files=[(path_to("~/.twistchat"), ("etc/twistchat.yml.example",))],
      install_requires=["twisted", "pyyaml"],
      url='https://bede.club/tag/chatroom',
      packages=['twistchat'],
     )

print("*"*80)
print("\n\nGreat, you've got TwistChat installed! Your config file should go\n"
      "in ~/.twistchat/twistchat.yml. An example config file is provided for\n"
      "you at ~/.twistchat/twistchat.yml.example.")
print("*"*80)
