Chatroom
=========

Miniature IRC-style chatroom written in about 300 lines of Python. Stores users and their passwords persistently.

Todo:

* Implement a `/nick` command to change the current connection's username
* Look into writing a client program to smooth out the experience and get rid of the usability problems with Telnet
* Store some statistics about users, like total number of messages sent
* Make the users file an absolute filepath
* Implement a `/help` command
* Implement a `/me` command - linked to this, look into bolding and other terminal control features over Telnet. Think about compatability with a client program.
* ~~Add a /quit or /leave command with "reason" parameter.~~
* ~~Store accounts more permanently~~
* ~~Improve username formatting~~
* ~~Broadcast messages when users join and leave~~
* ~~Take another look at the `users` and `connections` dicts - probably some redundancy there~~
* ~~Don't send messages to yourself~~
