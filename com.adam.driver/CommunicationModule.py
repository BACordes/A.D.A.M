from socket import socket
from socket import timeout


class CommunicationModule:

    def __init__(self, addr, port):
        self.tcp_socket = socket()
        self.tcp_socket.settimeout(10)
        self.tcp_socket.connect((addr, int(port)))


    def get_signal_strength(self):
        try:
            self.tcp_socket.send(b"GET SIGNAL\n")
            return self.tcp_socket.recv(1024).decode()
        except ConnectionAbortedError as e:
            print(e)
        except ConnectionRefusedError as e:
            print("CONNECTION REFUSED")
            print(e)
        except timeout:
            print("CONNECTION TIMED OUT!")
            print("No Response from Android Software (10s)")
            print("Shutting Down...")
            return 'error'

    def abort(self):
        try:
            self.tcp_socket.send(b"STOP ANDROID\n")
            return self.tcp_socket.recv(1024).decode()
        except ConnectionAbortedError as e:
            print(e)
        except ConnectionRefusedError as e:
            print("CONNECTION REFUSED")
            print(e)
        except timeout:
            print("CONNECTION TIMED OUT!")
            print("No Response from Android Software (10s)")
            print("Shutting Down...")
            return 'error'

    def verify(self):
        try:
            self.tcp_socket.send(b"VERIFY READY\n")
            return self.tcp_socket.recv(1024).decode()
        except ConnectionAbortedError as e:
            print(e)
        except ConnectionRefusedError as e:
            print("CONNECTION REFUSED")
            print(e)
        except timeout:
            print("CONNECTION TIMED OUT!")
            print("No Response from Android Software (10s)")
            print("Shutting Down...")
            exit(0)

