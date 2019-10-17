import os
from time import sleep
from gpiozero import AngularServo

VglobalAngle = 10
HglobalAngle = -60
minangle = 10


def write_to(position, incline):
    f = open("Position.txt", 'w+')
    f.write(str(position) + "," + str(incline) +"\n")
    f.close()


def moveto(position,incline): # works for reset function add a varible input change zeros to input.
    position = int(position)
    incline = int(incline)
    global deltaAngle
    global HdeltaAngle

    try:
        if s.angle < incline:
            while s.angle != incline:
                s.angle += 10
                write_to(HglobalAngle, VglobalAngle)
                sleep(2)
                if s.angle > incline:
                    s.angle = incline
                    sleep(2)
                    write_to(HglobalAngle, VglobalAngle)

        if s.angle > incline:
            while s.angle != incline:
                s.angle -= 10
                write_to(HglobalAngle, VglobalAngle)
                sleep(2)
                if s.angle < incline:
                    s.angle = incline
                    sleep(2)
                    write_to(HglobalAngle, VglobalAngle)

        if s2.angle < position:
            while s2.angle != position:
                s2.angle += 10
                write_to(HglobalAngle, VglobalAngle)
                sleep(2)
                if s2.angle > position:
                    s2.angle = position
                    sleep(2)
                    write_to(HglobalAngle, VglobalAngle)

        if s2.angle > position:
            while s2.angle != position:
                s2.angle -= 10
                write_to(HglobalAngle, VglobalAngle)
                sleep(2)
                if s2.angle < position:
                    s2.angle = position
                    sleep(2)
                    write_to(HglobalAngle, VglobalAngle)

    except KeyboardInterrupt:
        print('emergency exit')

def incrementVerticalServo():
    count = 0
    global VglobalAngle
    global deltaAngle

    try:
        while count == 0:
            count += 1;
            previousv = VglobalAngle
            VglobalAngle += deltaAngle
            s.angle = VglobalAngle
            if VglobalAngle == previousv:
                print("MOVE_FAILURE")
            else:
                print("MOVE_SUCCESS")
    except KeyboardInterrupt:
        print('emergency exit')


def moveHorizontalServo():
    count = 0
    global HglobalAngle
    global HdeltaAngle
    try:
        while count == 0:
            count += 1;
            previoush = HglobalAngle
            HglobalAngle += HdeltaAngle
            s2.angle = HglobalAngle
            if HglobalAngle == previoush:
                print("MOVE_FAILED")
            else:
                print("MOVE_SUCCESS")
    except KeyboardInterrupt:
        print('emergency exit')


def worker(conn, increasepos, increaseinc):
    pid = os.getpid()
    conn.send(pid)
    global deltaAngle
    global HdeltaAngle
    global VglobalAngle
    global HglobalAngle
    global minangle
    global s
    global s2

    # move vertical angle by this much
    deltaAngle = -int(increaseinc)

    # move vertical angle by this much
    HdeltaAngle = int(increasepos)

    while True:
        # recv the command fromt the conctroller
        command = conn.recv()
        if command == 'Start':
            print('\ndeltaAngle =' + str(deltaAngle))
            print('HdeltaAngle = ' + str(HdeltaAngle))
            
            try:
                f = open("Position.txt", 'r+')
                coord = f.read().split(",")
                f.close()

                s = AngularServo(17, initial_angle=int(coord[1]), min_angle=-60, max_angle=60)
                sleep(2)
                s2 = AngularServo(21, initial_angle=int(coord[0]), min_angle=-60, max_angle=60)
                sleep(2)
            except FileNotFoundError:
                print("File not found. Setting angles to 0 in 5 seconds...")
                sleep(5)
                s = AngularServo(17, min_angle=-60, max_angle=60)
                sleep(2)
                s2 = AngularServo(21, min_angle=-60, max_angle=60)
                sleep(2)
                write_to(0,0)
                sleep(2)
                
                
            
            print("ANTENNA INITIALIZED")
            print("Waiting 5 seconds before continuing...")
            sleep(5)
            while s.angle != 10:
                s.angle += 10
                sleep(2)
                
            write_to(HglobalAngle, VglobalAngle)
            
            while s2.angle != -60:
                s2.angle -= 10
                sleep(2)
                
            write_to(HglobalAngle, VglobalAngle)
            
           # sends controller that it has finished moving
            conn.send([HglobalAngle,VglobalAngle])# checks to see if the next command is to move
            write_to(HglobalAngle, VglobalAngle)
        elif command == 'Next':
            sleep(1)
            # if the angle is greater than 50 it'll set the angle to 50 instead of going over
            if VglobalAngle == -20:
                if HglobalAngle + HdeltaAngle >= 60:
                    if VglobalAngle == -20 and HglobalAngle == 60:
                        conn.send("done")
                        while True:
                            if conn.recv() == 'movetostrongest':
                                conn.send('ready')
                                strongest = conn.recv()
                                print("moving to strongest signal at: " + str(strongest[0]) +"  " + str(strongest[1]))
                                sleep(3)
                                moveto(strongest[0], strongest[1])
                                write_to(strongest[0], strongest[1])
                                sleep(3)
                                break
                        conn.send("Done")
                    HglobalAngle = 60
                    s2.angle = 60
                    sleep(2)
                    VglobalAngle = minangle
                    moveto(HglobalAngle, VglobalAngle)
                    sleep(2)
                    conn.send([HglobalAngle, VglobalAngle])
                    write_to(HglobalAngle, VglobalAngle)
                    sleep(1)
                else:
                    moveHorizontalServo()  # increases the HglobalAngle
                    VglobalAngle = minangle
                    moveto(HglobalAngle,VglobalAngle)
                    sleep(2)
                    conn.send([HglobalAngle, VglobalAngle])
                    write_to(HglobalAngle, VglobalAngle)
                    sleep(1)
            if VglobalAngle + deltaAngle <= -20:
                VglobalAngle = -20
                s.angle = -20
                sleep(2) # for right now they are set to 1
                conn.send([HglobalAngle, VglobalAngle])
                write_to(HglobalAngle, VglobalAngle)
                sleep(1)
            #  increments the vertical servo if it won't go over 50
            else:
                incrementVerticalServo()
                sleep(3)
                conn.send([HglobalAngle, VglobalAngle])
                write_to(HglobalAngle, VglobalAngle)
                sleep(3)
        elif command == 'moveto':
            print("Moving Antenna vertical angle to:", str(increaseinc))
            print("Moving Antenna horizontal angle to:", str(increasepos))

            try:
                f = open("Position.txt", 'r+')
                coord = f.read().split(",")
                f.close()

                s = AngularServo(17, initial_angle=int(coord[1]), min_angle=-60, max_angle=60)
                sleep(2)
                s2 = AngularServo(21, initial_angle=int(coord[0]), min_angle=-60, max_angle=60)
                sleep(2)
            except FileNotFoundError:
                print("File not found. Setting angles to 0 in 5 seconds...")
                sleep(5)
                s = AngularServo(17, min_angle=-60, max_angle=60)
                sleep(2)
                s2 = AngularServo(21, min_angle=-60, max_angle=60)
                sleep(2)
                write_to(0,0)
                sleep(2)
                
            moveto(increasepos, increaseinc)
            write_to(increasepos, increaseinc)
            sleep(3)
            s.close()
            sleep(3)
            s2.close()
            conn.send("close")
            exit(0)
