TwistChat
=========

IRC-style chatroom written in about 500 lines of Python.

Check out some basic usage below, along with the new Inline Messaging feature:

[![asciicast](https://asciinema.org/a/23003.png)](https://asciinema.org/a/23003)

Here's a full list of the commands available. Some of them are likely familiar from IRC and the like.

##Install
```
$ git clone https://github.com/bedekelly/twistchat
$ cd twistchat
$ python3 setup.py install --user
$ cp ~/.twistchat/twistchat.yml{.example,}
$ emacs ~/.twistchat/twistchat.yml  # Edit your config file if needed.
```

##Usage
```
$ screen twistchat  # Or tmux etc., or just another terminal window.
$ # Detatch screen/tmux, or open another window/switch device.
$ telnet localhost 8001  # Or the port you selected in your config file.
```


