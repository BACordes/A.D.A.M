import sys
from threading import Thread
from CommunicationModule import CommunicationModule


class ConsoleModule(Thread):
    """DEPRECATED!!"""

    def __init__(self, group=None, target=None, name=None, daemon=None, *args, **kwargs):
        super().__init__(group=group, target=target, name=name, daemon=daemon, args=args, kwargs=kwargs)
        self.TERMINATE = "terminate"
        self.START = "start"
        self.PAUSE = "pause"
        self.STOP = "stop"
        self.HELP = "help"
        addr = input("Please enter the IP address displayed on the screen")
        port = input("Please enter the port number displayed on the screen")
        self.tcpManager = CommunicationModule(addr, port)

    def run(self):
        print(self.getName(), self.ident)

        while self.is_alive():

            command = input("Enter a command or 'help' for more options:")

            if command == self.START:
                print("STARTING SIGNAL SWEEP...")
                # new thread that sweeps for signal (with the ability to be paused)
                print("**starts signal sweep**")
                print(self.tcpManager.get_signal_strength())

            elif command == self.PAUSE:
                # pause the sweep
                print("PAUSING THE SIGNAL SWEEP")
                # if there is a signal sweep in progress, pause it
                # if not, tell the user that there is not currently a signal sweep in progress
                # contact the signal sweep thread and pause it
                print("**pauses signal sweep**")

            elif command == self.STOP:
                # abort the signal sweep if there is a sweep in progress
                # return the antenna array to resting position
                print("ABORTING SIGNAL SWEEP")
                print("**aborts signal sweep**")
                print(self.tcpManager.abort())

            elif command == self.HELP:
                print("Available Commands:")
                print("\tstart - start the signal sweep")
                print("\tpause - pause a currently running signal sweep")
                print("\tstop - abort a currently running signal sweep and return the array to the start position")
                print("\tterminate - end the program")
                print("\thelp - display this help dialog")

            elif command == self.TERMINATE:
                print("TERMINATING PROGRAM")
                # do cleanup tasks here
                sys.exit(0)
            else:
                print("Command Not Recognized. Please type 'help' for available commands")
