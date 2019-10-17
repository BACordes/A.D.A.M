import socket
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from CommunicationModule import CommunicationModule


class ADAMGraphicalInterface(QApplication):

    def __init__(self):
        super().__init__([])

        # set up the IP and Port collection window
        self.collection_window = CollectionWindow(gui=self)
        self.collection_window.setWindowTitle("ADAM Desktop Client")

        # set up the main window
        self.main_window = MainWindow(gui=self)
        self.main_window.setWindowTitle("ADAM Desktop Client")
        self.main_window.move(50, 50)
        # show the collection window
        self.collection_window.show()
        self.exec_()

    def show_main_window(self, ip="", port="", inclination="", position=""):
        # set the labels in the main window to the IP and Port number
        self.main_window.set_connection_information(ip, port)
        self.main_window.set_deltas(inclination, position)
        self.collection_window.hide()
        self.main_window.show()
        self.main_window.start()

    def show_collection_window(self):
        """ executed when there is an error with the IP or port """
        self.main_window.hide()
        self.collection_window.error_text.setText("Please enter a valid IP and Port")
        self.collection_window.show()


class MainWindow(QWidget):

    def __init__(self, gui):
        super().__init__()

        # reference to main thread
        self.env = gui

        # set window dimensions
        # self.resize(720, 480)

        # connection information
        self.ip_address = None
        self.port_number = None

        # driver deltas
        self.delta_incline = 0
        self.delta_position = 0

        # reference to the TCP manager (like console module)
        self.tcp_manager = None

        # main layout
        self.main_layout = QGridLayout(self)

        # welcome message
        self.welcome = QLabel(text="ADAM Project")
        self.welcome.setAlignment(Qt.AlignCenter)
        self.welcome_section = QHBoxLayout()
        self.welcome_section.addWidget(self.welcome)
        self.welcome_section.setAlignment(Qt.AlignCenter)
        self.welcome_section.setContentsMargins(20, 20, 20, 20)
        self.welcome.setStyleSheet("QWidget{color: darkblue}")
        self.welcome.setFont(QFont("Arial", pointSize=16))
        self.main_layout.addLayout(self.welcome_section, 0, 0)

        # connection label information
        self.connection_label = QLabel("Connection Information")
        self.ip_label = QLabel("Phone IP Address:")
        self.port_label = QLabel("Phone Port Number:")
        self.ip_text = QLabel("")
        self.port_text = QLabel("")

        # create the connection information section
        self.connection_section = QVBoxLayout()
        self.ip_section = QHBoxLayout()
        self.ip_section.addWidget(self.ip_label)
        self.ip_section.addWidget(self.ip_text)
        self.port_section = QHBoxLayout()
        self.port_section.addWidget(self.port_label)
        self.port_section.addWidget(self.port_text)
        self.connection_section.addLayout(self.ip_section)
        self.connection_section.addLayout(self.port_section)

        self.status_label = QLabel("Signal Status:")
        self.status_text = QLabel("")
        self.status_section = QHBoxLayout()
        self.status_section.addWidget(self.status_label)
        self.status_section.addWidget(self.status_text)

        self.connection_section.addLayout(self.status_section)
        # set the vertical margin
        self.connection_section.setContentsMargins(5, 5, 5, 5)
        self.main_layout.addLayout(self.connection_section, 1, 0)

        # create the socket connection indicator
        self.connection_indicator_section = QVBoxLayout()
        self.indicator_label = QLabel("TCP Socket")
        self.indicator_label.setAlignment(Qt.AlignCenter)
        self.connection_indicator = QLabel("Not Connected")
        self.connection_indicator.setAlignment(Qt.AlignCenter)

        # self.connection_indicator.setMaximumSize(150, 25)
        self.connection_indicator.setMargin(5)
        self.connection_indicator.setStyleSheet("QWidget{background-color: red; color: white}")
        self.connection_indicator_section.addWidget(self.indicator_label)
        self.connection_indicator_section.addWidget(self.connection_indicator)
        self.connection_indicator_section.setAlignment(Qt.AlignCenter)
        self.connection_indicator_section.setContentsMargins(10, 10, 10, 10)
        self.main_layout.addLayout(self.connection_indicator_section, 0, 1)

        # create the progress bar

        # create the feedback section (text on the screen)
        self.feedback_text = QLabel()
        self.main_layout.addWidget(self.feedback_text, 3, 0, 3, 1)

        # create the buttons for the actions
        self.button_section = QHBoxLayout()
        self.start_button = QPushButton("START")
        self.button_section.addWidget(self.start_button)
        self.start_button.clicked.connect(self.start)
        self.pause_button = QPushButton("PAUSE")
        self.button_section.addWidget(self.pause_button)
        self.pause_button.clicked.connect(self.pause)
        self.resume_button = QPushButton("RESUME")
        self.button_section.addWidget(self.resume_button)
        self.reset_button = QPushButton("RESET")
        self.reset_button.clicked.connect(self.reset)
        self.button_section.addWidget(self.reset_button)
        self.resume_button.clicked.connect(self.resume)
        self.stop_button = QPushButton("STOP")
        self.button_section.addWidget(self.stop_button)
        self.stop_button.clicked.connect(self.stop)
        self.main_layout.addLayout(self.button_section, 2, 0)

        # create runtime status indicator
        self.runtime_status_indicator = QLabel("Stopped")
        self.runtime_status_indicator.setMargin(5)
        self.runtime_status_indicator.setAlignment(Qt.AlignCenter)
        self.runtime_status_indicator.setStyleSheet("QWidget{color: white; background-color: red}")
        self.runtime_status_label = QLabel("Runtime Status")
        self.runtime_status_section = QVBoxLayout()
        self.runtime_status_section.addWidget(self.runtime_status_label)
        self.runtime_status_section.addWidget(self.runtime_status_indicator)
        self.runtime_status_section.setAlignment(Qt.AlignCenter)
        self.runtime_status_section.setContentsMargins(10, 10, 10, 10)
        self.main_layout.addLayout(self.runtime_status_section, 0, 2)

    def reset(self):
        self.tcp_manager.reset = True

    def pause(self):
        self.stop()

    def resume(self):
        pass

    def stop(self):
        if self.tcp_manager:
            self.set_feedback_txt("Stopping ADAM System")
            self.tcp_manager.alive = False
            self.tcp_manager = None  # disengage the reference to this tcp_manager so that we can make a new one
            self.update_status("")
            self.set_feedback_txt("Stopped")
            self.reset_button.setDisabled(True)


    def set_feedback_txt(self, msg):
        self.feedback_text.setText(msg)
        print("feedback message changed: " + msg)

    def set_runtime_indicator(self, status):
        color = ""
        txt = status
        if status == "Stopped":
            color = "red"
        elif status == "Paused":
            color = "#f4aa42"
        elif status == "Running":
            color = "green"
        else:
            raise ValueError("Invalid status code for runtime indicator")

        self.runtime_status_indicator.setText(txt)
        self.runtime_status_indicator.setStyleSheet("QWidget{background-color: %s; color: white}" % color)

    def set_indicator(self, status):
        color = "#f4aa42"
        txt = ""
        if status == "NotConnected":
            color = "red"
            txt = "Not Connected"
            print("not connected")
        elif status == "Connecting":
            color = "#f4aa42"
            txt = "Establishing Connection"
            print("establishing connection")
        elif status == "Connected":
            color = "green"
            txt = "Connected"
            print("connected")
        else:
            raise ValueError("Invalid status code for connection indicator")

        self.connection_indicator.setText(txt)
        self.connection_indicator.setStyleSheet("QWidget{background-color: %s; color: white}" % color)

    def validate_ip(self, s):
        a = s.split('.')
        if len(a) != 4:
            raise ValueError("Please enter an IP address with 4 octets.")
        for x in a:
            if not x.isdigit():
                raise ValueError("Please enter a valid IP Address.")
            i = int(x)
            if i < 0 or i > 255:
                raise ValueError("Please enter a valid IP Address.")

    def validate_port(self, p):
        if not p.isdigit():
            raise ValueError("Please enter a valid port number 1 <= port <= 65535.")
        if int(p) < 1 or int(p) > 65535:
            raise ValueError("Please enter a valid port number 1 <= port <= 65535.")

    def set_deltas(self, inclination, position):

        inclination = int(inclination)
        position = int(position)
        if 10 <= inclination <= 20:
            self.delta_incline = inclination
        else:
            raise ValueError("Please enter a delta inclination between 10 and 20")

        if 10 <= position <= 30:
            self.delta_position = position
        else:
            raise ValueError("Please enter a delta position between 10 and 30")

    def set_connection_information(self, ip, port):
        self.validate_ip(ip)
        self.validate_port(port)

        self.ip_text.setText(ip)
        self.port_text.setText(port)

        self.ip_address = ip
        self.port_number = int(port)

    def start(self):
        print("Starting Comm Module in separate thread!")
        try:
            if not self.tcp_manager:
                self.tcp_manager = CommunicationModule(self.ip_address, self.port_number, self.set_indicator)
                self.tcp_manager.add_signal_changed_listener(self.update_status)
                self.tcp_manager.add_thread_state_listener(self.set_runtime_indicator)
                self.tcp_manager.add_error_display_handler(self.set_feedback_txt)
                self.tcp_manager.start()
                self.reset_button.setDisabled(False)
                self.setFocus()
        except socket.timeout:
            print("TIMEOUT!")
            self.env.show_collection_window()

    def update_status(self, status):
        self.status_text.setText(status)
        self.status_text.update()
        # print("in update status method: ", status)

    def closeEvent(self, event):
        if self.tcp_manager:
            self.tcp_manager.alive = False  # kill the tcp socket thread
        super().closeEvent(event)


class CollectionWindow(QWidget):

    def __init__(self, gui):
        super().__init__()

        # reference to main thread
        self.env = gui

        # define window size and position
        self.resize(380, 220)
        self.move(100, 100)

        # get the layouts
        v_layout = QVBoxLayout()
        ip_layout = QHBoxLayout()
        port_layout = QHBoxLayout()

        # set the welcome message
        msg = QLabel("ADAM Project")
        sub_msg = QLabel("Please Enter Android Info")

        msg.setFont(QFont("Arial", pointSize=16))
        msg_layout = QVBoxLayout()
        msg_layout.addWidget(msg)
        msg_layout.addWidget(sub_msg)
        msg_layout.setAlignment(Qt.AlignCenter)
        v_layout.addLayout(msg_layout)

        # get the text fields
        ip_label = QLabel(text="IP Address of Phone:")
        ip_layout.addWidget(ip_label)
        self.ip_txt_field = QLineEdit()
        ip_layout.addWidget(self.ip_txt_field)

        port_label = QLabel(text="Port Number:")
        port_layout.addWidget(port_label)
        self.port_txt_field = QLineEdit()
        port_layout.addWidget(self.port_txt_field)

        # add fields for the delta inclination and declinations
        self.incline_field = QLineEdit()
        self.incline_label = QLabel("Delta Incline")
        self.incline_field.setPlaceholderText("Enter # to increment incline by")
        self.position_field = QLineEdit()
        self.position_label = QLabel("Delta Position")
        self.position_field.setPlaceholderText("Enter # to increment position by")

        # populate fields if data exists
        try:
            with open("network.conf", "r+") as conf:
                ip, port = conf.readline().split(",")
                self.ip_txt_field.setText(ip)
                self.port_txt_field.setText(port)
        except FileNotFoundError:
            pass  # file doesnt exist, do nothing

        # increment fields and labels
        self.incline_section = QHBoxLayout()
        self.incline_section.addWidget(self.incline_label)
        self.incline_section.addWidget(self.incline_field)
        self.position_section = QHBoxLayout()
        self.position_section.addWidget(self.position_label)
        self.position_section.addWidget(self.position_field)
        self.position_field.setText("10")
        self.incline_field.setText("10")

        # create submit button
        btn = QPushButton("Submit")
        btn.clicked.connect(self.submit)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn)
        btn_layout.setAlignment(Qt.AlignRight)

        # error label
        self.error_text = QLabel("")
        self.error_text.setFont(QFont("Arial", pointSize=12))
        self.error_text.setStyleSheet("QWidget{color: red}")

        # collect the layouts and add them to the window
        v_layout.addWidget(self.error_text)
        v_layout.addLayout(ip_layout)
        v_layout.addLayout(port_layout)
        v_layout.addLayout(self.incline_section)
        v_layout.addLayout(self.position_section)
        v_layout.addLayout(btn_layout)
        self.setLayout(v_layout)

    # bind action to enter button
    def keyPressEvent(self, event):
        # enter will submit the form
        if event.key() == Qt.Key_Enter or Qt.Key_Return:
            self.submit()
        super().keyPressEvent(event)

    def submit(self):
        # collect the values
        ip_address = self.ip_txt_field.text()
        port_number = self.port_txt_field.text()
        d_incline = self.incline_field.text()
        d_position = self.position_field.text()

        with open("network.conf", "w+") as conf:
            conf.write(ip_address + "," + port_number)  # record the ip and port so we don't have to keep typing it

        if ip_address and port_number and d_incline and d_position:
            print("IP & Port: ", ip_address, port_number)
            # switch to the main window and save the ip and port
            try:
                self.env.show_main_window(ip_address, port_number, d_incline, d_position)
            except ValueError as v:
                self.error_text.setText(v.__str__())
                print("Invalid Input", v)

