Chatroom
=========

Miniature IRC-style chatroom written in about 200 lines of Python. Only stores state in RAM, so if the server dies, the accounts are gone too. 

Todo:

* Add a /quit or /leave command with "reason" parameter.
* Store accounts more permanently
* Improve username formatting
* ~~Broadcast messages when users join and leave~~
* Take another look at the `users` and `connections` dicts - probably some redundancy there
* ~~Don't send messages to yourself~~
