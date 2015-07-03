#!/usr/bin/env python3
"""
A mini chatroom server written in Twisted.
"""

import re
import pickle
from os.path import expanduser as abs_path
from twisted.internet import reactor, protocol
from twisted.protocols.basic import LineReceiver

PORT = 8001
USERS_FILE = abs_path("~/.chatroom_users.dat")

class states:
    """
    Enumerate all states that an IOStream protocol instance can be in.
    """
    REGISTERED = 0
    REQUESTING_NAME = 1
    REQUESTING_PASSWORD = 2
    REQUESTING_NEW_PASSWORD = 3
    CHANGING_USERNAME = 4


class UserSession(LineReceiver):
    """
    Represent a single user-session. Handles registering, logins, sending messages etc.
    """

    def __init__(self, factory, addr):
        self.factory = factory
        self.addr = addr
        self.reason_for_quit = ""
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
        When we lose a connection, let the other users know.
        """
        msg = "{} lost connection.".format(self.longname)
        if self.reason_for_quit:
            msg += ' ("{}")'.format(self.reason_for_quit)
        print(msg)
        self.broadcast_noti(msg)
        self.factory.remove_connection(self)

    def sendLine(self, line):
        """
        Wrap the LineReceiver's sendLine method to use strings instead of bytes.
        """
        super().sendLine(bytes(line, encoding="utf-8"))

    def msg_format(self, line):
        """
        When we're sending a message, prepend a nicely-formatted version of our username
        and hostname.
        """
        return "[{}] {}".format(self.name, line.strip())

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

    def command_or_msg(self, line):
        """
        Check if a line sent from a registered user is a command or a message.
        If it's a command, do what they say.
        If it's a message, broadcast it to the other users.
        """
        is_command = lambda l: l.startswith("/")
        if is_command(line):
            self.handle_command(line)
        else:
            self.broadcast_msg(line)

    def handle_command(self, text):
        """
        Process a command like /quit or /leave.
        """
        cmd, *params = text.split()
        print("Command from {}: {}".format(self.longname, cmd))
        if cmd in ("/quit", "/leave"):
            reason = ' '.join(params)
            self.reason_for_quit = reason
            self.transport.loseConnection()
        elif cmd in ("/nick", "/user", "/username"):
            if params:
                self.got_username('_'.join(params))
            else:
                self.sendLine("Usage: {} <new nick>"
                              "".format(cmd))
        elif cmd == "/me":
            if params:
                msg = "* {} {}".format(self.name,' '.join(params))
                self.factory.broadcast_message(msg)

            
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
            self.command_or_msg(line)
        elif self.state == states.REQUESTING_PASSWORD:
            self.check_password(line)
        elif self.state == states.REQUESTING_NEW_PASSWORD:
            self.create_account(line)

    def welcome(self):
        """
        Welcome the user to the chatroom.
        Show how many users there are, and let the others know.
        """
        print("Anonymous({}) logged in as {}"
              "".format(self.addr.host, self.name))

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
        # Output some debug info.
        print("Anonymous({}) registered as {}"
              "".format(self.addr.host, self.name))
        # Save our changes.
        save_users(self.factory.users)

    def check_username(self, uname):
        """
        Check if the given username is valid.
        If so, proceed with login or registration.
        If not, stay in the same state and ask for a repeat.
        """
        valid = re.compile("^[A-Za-z0-9_]+$")
        is_valid = lambda attempt: bool(valid.fullmatch(attempt))

        if is_valid(uname):
            # If the line we got is a valid username, proceed to register or login.
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


class UserSessionFactory(protocol.Factory):
    """
    Store state across sessions (currently, just the number of players).
    """
    def __init__(self):
        self.connections = set()
        self.users = load_users()

    @property
    def num_users(self):
        return len(self.connections)

    def remove_connection(self, conn):
        """
        Remove a connection from our mapping.
        """
        self.connections.remove(conn)

    def broadcast_message(self, message, exception=None):
        """
        Broadcast `message` to every connected user except `exception`.
        """
        for conn in self.connections:
            if conn is not exception:
                conn.sendLine(message)

    def buildProtocol(self, addr):
        """
        Create and return a new connection instance, adding it to a dict of users.
        """
        sess = UserSession(self, addr)
        self.connections.add(sess)
        return sess


def save_users(users):
    """
    Save the user-password mapping to the local folder.
    """
    with open(USERS_FILE, "wb") as users_file:
        pickle.dump(users, users_file)
        

def load_users():
    """
    Attempt to load users from the data file.
    If one doesn't exist, just return a new mapping.
    """
    try:
        with open(USERS_FILE, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}

        
reactor.listenTCP(PORT, UserSessionFactory())
print("Server running at localhost:{p}. Connect using `telnet localhost {p}`."
      "".format(p=PORT))
reactor.run()
