import multiprocessing, Driver, signalposition, os, psutil


def main(conn, inputposition, inputincline, command, conpid, tcp_manager):
    if command == 'START':
        # Sends back to pid to the parent process
        conn.send(os.getpid())

        # creates signal objects
        strongest = signalposition.Signalposition(0, 0, 0)
        signal_obj = signalposition.Signalposition(0, 0, 0)

        # creates the pipes for sending information
        conn1, conn2 = multiprocessing.Pipe()
        # Starts the driver process with the argument the first comm mod end of the pipe
        driver_process = multiprocessing.Process(
            target=Driver.worker, args=[conn2, inputposition, inputincline])
        driver_process.start()
        driver_pid = conn1.recv()
        conn.send(driver_pid)
        conn1.send('Start')
        p = psutil.Process(conpid)
        p1 = psutil.Process(driver_pid)
        # if the driver is done moving the servos then grab signal
        starting_position = conn1.recv()
        strongest.position = starting_position[0]
        strongest.incline = starting_position[1]
        strongest.signal = tcp_manager.get_signal_strength()
        if strongest.signal == 'error':
            tcp_manager.abort()
            p1.terminate()
            p.terminate()
            exit(0)
        # puts information from drivers into a signal obj
        print("Antenna Horizontal Angle: " + str(strongest.position))
        print("Antenna Vertical Angle: " + str(strongest.incline))
        print("Signal Strength = " + str(strongest.signal))
        print('Please enter a command: ')
        while True:
            conn1.send('Next')   # moves the antenna to the next position
            position = conn1.recv()  # recieves information from position

            if position == 'done':  # if the moving is complete then break out of loop
                break

            signal_strength = tcp_manager.get_signal_strength() # receives signal
            if signal_strength == 'error':
                tcp_manager.abort()
                p1.terminate()
                p.terminate()
                exit(0)
            # signal object below
            signal_obj.position = int(position[0])
            signal_obj.incline = int(position[1])
            signal_obj.signal = signal_strength

            print("Antenna Horizontal Angle: " + str(signal_obj.position))
            print("Antenna Vertical Angle: " + str(signal_obj.incline))
            print("Signal Strength = " + str(signal_obj.signal))
            print('Please enter a command: ')

            # compares the signal strength to see which object is better
            if int(signal_obj.signal) >= int(strongest.signal):

                # Replaces teh strongest object with the new object.
                strongest.signal = signal_obj.signal
                strongest.incline = signal_obj.incline
                strongest.position = signal_obj.position

        # prints out the stronges object
        print("\nStrongest signal is at position: " + str(strongest.position))
        print("Strongest signal is at incline: " + str(strongest.incline))
        print("Strongest signal is: " + str(strongest.signal))
        conn1.send('movetostrongest')
        if conn1.recv() == 'ready':
            conn1.send([strongest.position, strongest.incline])
        if conn1.recv() == 'Done':
            print("Exiting...")
            # Exits the child process and kills the parent
            tcp_manager.abort()
            p1.terminate()
            p.terminate()
            exit(0)
    elif command == 'MOVETO' or 'RESET':
        # Sends back to pid to the parent process
        conn.send(os.getpid())

        # creates the pipes for sending information
        conn1, conn2 = multiprocessing.Pipe()

        # Starts the driver process with the argument the first comm mod end of the pipe
        driver_Process = multiprocessing.Process(
            target=Driver.worker, args=[conn2, inputposition, inputincline])
        driver_Process.start()
        driver_pid = conn1.recv()
        conn.send(driver_pid)
        conn1.send('moveto')
        if conn1.recv() == "close":
            print("Exiting...")
            # Exits the child process and kills the parent
            p = psutil.Process(conpid)
            p1 = psutil.Process(driver_pid)
            if p1.is_running():
                p1.terminate
            p.terminate()
            exit(0)


