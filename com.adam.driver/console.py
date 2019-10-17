import multiprocessing, os,RaspMain, psutil,re
from CommunicationModule import CommunicationModule
conn1, conn2 = multiprocessing.Pipe()


def welcome_message():
    print("______          _           _      ___   ______  ___   ___  ___")
    print("| ___ \        (_)         | |    / _ \  |  _  \/ _ \  |  \/  |")
    print("| |_/ _ __ ___  _  ___  ___| |_  / /_\ \ | | | / /_\ \ | .  . |")
    print("|  __| '__/ _ \| |/ _ \/ __| __| |  _  | | | | |  _  | | |\/| |")
    print("| |  | | | (_) | |  __| (__| |_  | | | |_| |/ _| | | |_| |  | |")
    print("\_|  |_|  \___/| |\___|\___|\__| \_| |_(_|___(_\_| |_(_\_|  |_/")
    print("              _/ |                                             ")
    print("             |__/                                              ")
    print(" _____________________________________________________________")
    print("| COMMANDS:                                                   |")
    print("| start: Starts searching for signal.                         |")
    print("| stop: Exits the program.                                    |")
    print("| pause: Suspends the searching process.                      |")
    print("| resume: Resumes the searching.                              |")
    print("| reset: Reset the antenna position to zero.                  |")
    print("| moveto: Moves the antenna angles.                           |")
    print("\_____________________________________________________________/")


def help_message1():
    print("COMMANDS:")
    print("start: Starts searching for signal ")
    print("stop: Exits the program")
    print("reset: Reset the antenna position to zero.")
    print("moveto: Moves the antenna angles.")


def help_message2():
    print("COMMANDS:")
    print("stop: Exits the program")
    print("pause: Suspends the searching process")
    print("resume: Resumes the searching")


def starting():
    global p
    global p1
    global tcp_manager
    while True:
        command = input('Please enter a command: ').upper()
        con_pid = os.getpid()
        if command == 'START':
            while True:
                try:
                    input_incline = input('Please enter the Vertical Delta: ')
                    if 20 >= int(input_incline) >= 10:
                        break
                    else:
                        print('Please input a number equal or greater than 10')
                except ValueError:
                    print("Please input numbers only")
            while True:
                try:
                    input_position = input('Please enter the Horizontal Delta: ')
                    if 30 >= int(input_position) >= 10:
                        break
                    else:
                        print('Please input a number equal or greater than 10')
                except ValueError:
                    print("Please input numbers only")

            address_check = True
            while True:
                try:
                    while address_check:
                        address = input("Pleae enter IP Address: ")
                        if re.match("^(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})$", address):
                            address_check = False
                        elif address.upper() == 'STOP':
                            exit(0)
                        else:
                            print("Please enter a Valid IP Address!")
                    port = input('Please enter Port Number: ')
                    if port.upper() == 'STOP':
                        exit(0)
                    tcp_manager = CommunicationModule(address, port)  # receives signal

                    break
                except ConnectionRefusedError:
                    address_check = True
                    print("CONNECTION REFUSED!")
                    print("Please check your IP address or Port number")
                except TimeoutError:
                    address_check = True
                    print("CONNECTION TIMED OUT!")
                    print("Please check your IP address or Port number")
                except OSError:
                    address_check = True
                    print("Invalid IP and Port Number!")
                    print("Please check your IP address or Port number")
                except ValueError:
                    print("Please input a valid Port number")
            print("Android is " + tcp_manager.verify())
            communication_mod_process = multiprocessing.Process(
                target=RaspMain.main, args=[conn2, input_position, input_incline, command, con_pid, tcp_manager])
            communication_mod_process.start()
            comm_pid = conn1.recv()
            driver_pid = conn1.recv()
            p = psutil.Process(comm_pid)
            p1 = psutil.Process(driver_pid)

            break
        elif command == 'STOP':
            exit(0)
        elif command == 'HELP':
            help_message1()
        elif command == "MOVETO":
            correct_input = True
            while correct_input:
                try:
                    vertical = input('Please enter Vertical angle: ')
                    if 10 >= int(vertical) >= -20:
                        correct_input = False
                    elif vertical.upper() == 'STOP':
                        exit(0)
                    else:
                        print('Please input a number between 10 and -20')
                except ValueError:
                    print('Please input a number only')
            correct_input = True
            while correct_input:
                try:
                    horizontal = input('Please enter the Horizantal angle: ')
                    if -60 <= int(horizontal) <= 60:
                        correct_input = False
                    elif horizontal.upper() == 'STOP':
                        exit(0)
                    else:
                        print('Please input a number between -60 and 60')
                except ValueError:
                    print('Please input numbers only')
            communication_mod_process = multiprocessing.Process(
                target=RaspMain.main, args=[conn2, horizontal, vertical, command, con_pid, 0])
            communication_mod_process.start()
            comm_pid = conn1.recv()
            driver_pid = conn1.recv()
            p = psutil.Process(comm_pid)
            p1 = psutil.Process(driver_pid)
            break

        elif command == "RESET":
            communication_mod_process = multiprocessing.Process(
                target=RaspMain.main, args=[conn2, 0, 0, command, con_pid, 0])
            communication_mod_process.start()
            comm_pid = conn1.recv()
            driver_pid = conn1.recv()
            p = psutil.Process(comm_pid)
            p1 = psutil.Process(driver_pid)
            break
        else:
            print('Valid commands: start, stop, moveto')


def waiting():
    global p
    global p1
    global tcp_manager
    while True:
            command = input('\nPlease enter a command: \n').upper()
            if command == 'STOP':
                p.terminate()
                p1.terminate()
                try:
                    print(tcp_manager.abort())
                except AttributeError:
                    print("tcp_Manager wasn't started")
                except NameError:
                    print("tcp_Manager wasn't started")
                print("Exited")
                break
            elif command == 'PAUSE':
                print("Paused")
                p.suspend()
                p1.suspend()
            elif command == 'RESUME':
                print("Resumed")
                p.resume()
                p1.resume()
            elif command == 'HELP':
                help_message2()

            else:
                print('Please enter a correct command (pause, resume, stop)')

if __name__ == "__main__":
    welcome_message()
    starting()
    waiting()
    exit(0)
