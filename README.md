TwistChat
=========

IRC-style chatroom written in about 500 lines of Python.

##Install
```
git clone https://github.com/bedekelly/twistchat
cd twistchat
python3 setup.py install --user
cp ~/.twistchat/twistchat.yml{.example,}
emacs ~/.twistchat/twistchat.yml  # Edit your config file.
```

##Usage
```
screen twistchat  # Or tmux etc., or just another terminal window.
# Detatch screen/tmux, or open another window/switch device.
telnet localhost 8001  # Or the port you selected in your config file.
```

##Commands
####Open to all users
* `/me <action> ...`
* `/nick <newname> ...`
* `/msg <user> [msg ...]`
* `/quit [reason ...]`
* `/changepass [newpass]`

####OP required for these:
* `/kick <user> ...`
* `/op <user>` and `/deop <user>`
