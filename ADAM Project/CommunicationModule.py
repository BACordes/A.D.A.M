import json
import sys
import time
from json import JSONDecodeError
from socket import socket
from socket import timeout, herror, gaierror
from threading import Thread
from Drivers import ServoController


class CommunicationModule(Thread):

    def __init__(self, addr, port, connection_listener=None):
        super().__init__()
        self.signal_changed_listeners = []
        self.connection_changed_listeners = []
        self.thread_state_listeners = []
        self.feedback_display_handlers = []

        self.max = {
            "horizontal": 0,
            "strength": -999
        }

        # add the listener
        if connection_listener is not None:
            self.connection_changed_listeners.append(connection_listener)

        # transmit connection information to listeners
        for x in self.connection_changed_listeners:
            x("Connecting")  # indicate that we are establishing an connection
        self.tcp_socket = socket()
        self.tcp_socket.settimeout(3)  # 3 second timeout
        self.ip_address = addr
        self.port = port
        self.alive = True
        self.reset = False

        try:
            self.tcp_socket.connect((self.ip_address, int(self.port)))
            self.tcp_socket.sendall(b"")
            for x in self.connection_changed_listeners:
                x("Connected")  # indicate that we have successfully connected to a socket
        except Exception as e:
            for x in self.connection_changed_listeners:
                x("NotConnected")  # indicate something has gone wrong
                print(e)
                self.alive = False

    def run(self):
        try:
            servos = ServoController()
            # move the antenna to the beginning position
            time.sleep(1)
            print("min angles", servos.MIN_HORIZONTAL_ANGLE, 10)
            servos.move_to_position(servos.MIN_HORIZONTAL_ANGLE, self)
            try:
                while servos.get_horizontal_position() < servos.MAX_HORIZONTAL_ANGLE:

                    # check for the kill command
                    if not self.alive:
                        raise RuntimeError

                    # check for the reset command
                    if self.reset:
                        self.alive = False
                        servos.move_to_position(0, self)
                        self.reset = False

                    for y in self.thread_state_listeners:
                        y("Running")  # update thread state listeners
                    for x in self.signal_changed_listeners:
                        x(self.get_signal_txt())  # update signal state listeners

                    # move the antenna if we are not at the max angle yet
                    print("horizontal position: ", servos.get_horizontal_position())

                    if self.get_signal_strength()[1] > self.max["strength"]:
                        self.max["horizontal"] = servos.get_horizontal_position()
                        self.max["strength"] = int(self.get_signal_strength()[1])

                    for j in self.feedback_display_handlers:
                        j("Moved to position %d DEG. \tMax Signal: %d DEG -> %d" %
                          (servos.get_horizontal_position(),
                           self.max["horizontal"],
                           self.max["strength"]))

                    servos.increment_horizontal_position()

            except ValueError as v:
                print(v)

            try:
                # move to the strongest signal recorded
                servos.move_to_position(self.max["horizontal"], self)
                self.tcp_socket.sendall(b"")  # probe the connection to see if it is open
                self.tcp_socket.close()  # if its open, close it
            except Exception as e:
                pass  # connection was already closed
            finally:
                for x in self.connection_changed_listeners:
                    x("NotConnected")

                for y in self.thread_state_listeners:
                    y("Stopped")
        except RuntimeError:
            # execution was intentionally terminated
            pass
        finally:
            for x in self.connection_changed_listeners:
                x("NotConnected")

            for y in self.thread_state_listeners:
                y("Stopped")

    def get_alive_status(self):
        return self.alive

    def get_signal_strength(self):
        """
        Quality -> signal[0]
        Power -> signal[1]
        """
        try:

            self.tcp_socket.send(b"GET SIGNAL\n")
            signal = self.tcp_socket.recv(1024).decode()
            signal = json.loads(signal)
            return signal

        except TypeError as t:
            print("TypeError: ", t)
            for x in self.feedback_display_handlers:
                x("TypeError " + str(t))
            self.exit()

        except ConnectionResetError as c:
            print("Connection Reset: ", c)
            for x in self.feedback_display_handlers:
                x("Connection Reset: " + str(c))
            self.exit()

        except ConnectionAbortedError as a:
            print("Connection Aborted: ", a)
            for x in self.feedback_display_handlers:
                x("Connection Aborted: " + str(a))
            self.exit()

        except ConnectionRefusedError as r:
            print("Connection Refused: ", r)
            for x in self.feedback_display_handlers:
                x("Connection Refused: " + str(r))
            self.exit()

        except JSONDecodeError as j:
            print("Bytestream Error: Socket received invalid data. ", j)
            for x in self.feedback_display_handlers:
                x("Bytestream Error: Socket received invalid data: " + str(j))
            self.exit()

        except timeout as t:
            print("Timeout Error: Socket received no data. ", t)
            for x in self.feedback_display_handlers:
                x("Timeout Error: Socket received no data. " + str(t))
            self.exit()

    def get_signal_txt(self):
        try:
            signal = self.get_signal_strength()
            return "quality: " + str(signal[0]) + "\tpower: " + str(signal[1])
        except TypeError as t:
            pass

    def abort(self):
        try:
            self.tcp_socket.send(b"STOP ANDROID\n")
            return self.tcp_socket.recv(1024).decode()
        except ConnectionAbortedError as e:
            print(e)
        except ConnectionRefusedError as e:
            print("CONNECTION REFUSED")
            print(e)

    # methods (listeners) from other classes that get called at specific times
    def add_signal_changed_listener(self, method):
        self.signal_changed_listeners.append(method)

    def add_connection_changed_listener(self, method):
        self.signal_changed_listeners.append(method)

    def add_thread_state_listener(self, method):
        self.thread_state_listeners.append(method)

    def add_error_display_handler(self, method):
        self.feedback_display_handlers.append(method)

    def exit(self):
        for y in self.thread_state_listeners:
            y("Stopped")

        for x in self.connection_changed_listeners:
            x("NotConnected")

        self.alive = False  # kill this thread

