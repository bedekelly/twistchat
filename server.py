#!/usr/bin/env python3
"""
A mini chatroom server written in Twisted.
"""

import re
from twisted.internet import reactor, protocol
from twisted.protocols.basic import LineReceiver


class states:
    """
    Enumerate all states that an IOStream protocol instance can be in.
    """
    REGISTERED = 0
    REQUESTING_NAME = 1
    REQUESTING_PASSWORD = 2
    REQUESTING_NEW_PASSWORD = 3


class IOStream(LineReceiver):
    """
    Define what happens when we get a new connection.
    """

    def __init__(self, factory, addr):
        self.factory = factory
        self.addr = addr
        self.gamesession = None
        self.name = "Anonymous"

    def connectionMade(self):
        """
        When we get a new connection, request the user's name.
        """
        print("{} connected.".format(self.longname))
        self.sendLine("What is your name? (Type below and press Return)")
        self.state = states.REQUESTING_NAME

    def connectionLost(self, reason):
        """
        When we lose a connection, stop the gamesession eval thread if we have one.
        """
        if self.gamesession is not None:
            self.gamesession.running = False
        msg = "{} lost connection.".format(self.longname)
        print(msg)
        self.broadcast_noti(msg)

    def sendLine(self, line):
        """
        Override the LineReceiver's sendLine method to use strings instead of bytes.
        """
        super().sendLine(bytes(line, encoding="utf-8"))

    def msg_format(self, line):
        """
        When we're sending a message, prepend a nicely-formatted version of
        our username and hostname.
        """
        return "[{}] {}".format(self.longname, line.strip())

    def broadcast_msg(self, line):
        """
        Send a formatted message to each connected user except this one.
        """
        self.factory.broadcast_message(self.msg_format(line), exception=self)

    def broadcast_noti(self, line):
        """
        Send a formatted server notification to each connected user except this one.
        """
        self.factory.broadcast_message(line, exception=self)

    def lineReceived(self, line):
        """
        When we get a new line, check what state we're in and act accordingly.
        """
        try:
            line = line.decode("utf-8").strip()
        except UnicodeDecodeError:
            # Just don't even try to handle it.
            return

        # If we're still requesting the name, then treat the line we just got as
        # the user's name.
        if self.state == states.REQUESTING_NAME:
            self.check_username(line)

        elif self.state == states.REGISTERED:
            self.broadcast_msg(line)

        elif self.state == states.REQUESTING_PASSWORD:
            self.check_password(line)

        elif self.state == states.REQUESTING_NEW_PASSWORD:
            self.create_account(line)

    def welcome(self):
        """
        Welcome the user to the chatroom.
        Show how many users there are, and let the others know.
        """
        self.sendLine("Welcome {}!".format(self.name))
        self.sendLine("{} people online currently."
                      "".format(self.factory.num_users))
        self.broadcast_noti("{} joined the chatroom."
                            "".format(self.longname))

    def create_account(self, pword):
        """
        Make an account using the requested username and password.
        Welcome the user and log their entrance.
        """
        self.factory.users[self.requested_uname] = pword
        self.name = self.requested_uname
        self.state = states.REGISTERED
        self.sendLine("Account created successfully.")
        # Display some personalised welcome information.
        self.welcome()
        # And output some debug info.
        print("Anonymous({}) registered as {}"
              "".format(self.addr.host, self.name))

    def check_username(self, uname):
        """
        Check if the given username is valid.
        If so, proceed with login or registration.
        If not, stay in the same state and ask for a repeat.
        """
        def valid_username(attempt):
            valid = re.compile("^[A-Za-z0-9 ]+$")
            return bool(valid.fullmatch(attempt))

        if valid_username(uname):
            # If the line we got is a valid username, try to register.
            self.got_username(uname)
        else:
            # If the line is empty or invalid, error and try again.
            self.sendLine("Please enter a valid username. (Type below and press Return)")

    def check_password(self, pword):
        """
        Checks the user's password against the value stored for that username.
        If it's right, allow them in. If not, just stay in the same state.
        """
        if self.factory.users[self.requested_uname] == pword:
            self.name = self.requested_uname
            self.state = states.REGISTERED
            self.welcome()
        else:
            self.sendLine("Password incorrect. Enter password:")

    def login(self, uname):
        """
        Called when the requested username is preexisting.
        """
        self.sendLine("Password:")
        self.requested_uname = uname
        self.state = states.REQUESTING_PASSWORD

    def register(self, uname):
        """
        Called when the requested username is new.
        """
        self.requested_uname = uname
        self.sendLine("Enter new password:")
        self.state = states.REQUESTING_NEW_PASSWORD

    def got_username(self, uname):
        """
        Called when the user has entered their username.
        """
        if uname in self.factory.users:
            self.login(uname)
        else:
            self.register(uname)

    @property
    def longname(self):
        """
        Formats the username and host address.
        """
        return "{}({}:{})".format(self.name, self.addr.host, self.addr.port)


class IOStreamFactory(protocol.Factory):
    """
    Store state across sessions (currently, just the number of players).
    """
    def __init__(self):
        self.connections = {}
        self.users = {}

    @property
    def num_users(self):
        return len(self.users)

    def broadcast_message(self, message, exception=None):
        """
        Broadcast `message` to every connected user except `exception`.
        """
        for conn in self.connections.values():
            if conn is not exception:
                conn.sendLine(message)

    def buildProtocol(self, addr):
        """
        Create and return a new connection instance, adding it to a dict of users.
        """
        self.connections[addr] = IOStream(self, addr)
        return self.connections[addr]


reactor.listenTCP(8001, IOStreamFactory())
print("Server running at localhost:8001. Connect using `telnet localhost 8001`.")
reactor.run()
