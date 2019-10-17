from time import sleep

from gpiozero import AngularServo


class ServoController:

    def __init__(self, min_h_angle=-90, max_h_angle=90, delta_horizontal=10):

        self.HORIZONTAL_PIN = 17
        self.delta_horizontal_angle = delta_horizontal
        self.MIN_HORIZONTAL_ANGLE = min_h_angle
        self.MAX_HORIZONTAL_ANGLE = max_h_angle
        CORRECTION_VALUE = 0.7
        maxPW = (2.0 + CORRECTION_VALUE) / 1000
        minPW = (1.0 - CORRECTION_VALUE) / 1000

        self.horizontal_servo = AngularServo(self.HORIZONTAL_PIN, min_angle=self.MIN_HORIZONTAL_ANGLE,
                                             max_angle=self.MAX_HORIZONTAL_ANGLE,
                                             min_pulse_width=minPW,
                                             max_pulse_width=maxPW)


    def increment_horizontal_position(self):
        print("Incrementing Horizontal Position")
        # check to make sure that the current angle won't go out of bounds if the delta angle is added
        if self.horizontal_servo.angle + self.delta_horizontal_angle <= self.MAX_HORIZONTAL_ANGLE:
            # increment the angle
            self.horizontal_servo.angle += self.delta_horizontal_angle
            print("Horizontal Angle Set To " + self.horizontal_servo.angle.__str__())
        else:
            # set the angle at the maximum
            self.horizontal_servo.angle = self.MAX_HORIZONTAL_ANGLE

        sleep(2)
        return self.horizontal_servo.angle

    def move_to_position(self, horizontal, comm):
        delta = 5
        slp = 1

        print("Moving to %d DEG" % (horizontal))

        if horizontal > self.MAX_HORIZONTAL_ANGLE:
            raise ValueError("Horizontal position out of bounds! " + horizontal.__str__() + " > " +
                             self.MAX_HORIZONTAL_ANGLE.__str__())

        if horizontal >= self.horizontal_servo.angle:
            while horizontal != self.horizontal_servo.angle and comm.get_alive_status():
                if horizontal < self.horizontal_servo.angle + delta:
                    self.horizontal_servo.angle = horizontal
                else:
                    self.horizontal_servo.angle += delta
                sleep(slp)
        else:
            while horizontal != self.horizontal_servo.angle and comm.get_alive_status():
                if horizontal > self.horizontal_servo.angle - delta:
                    self.horizontal_servo.angle = horizontal
                else:
                    self.horizontal_servo.angle -= delta
                sleep(slp)

    def get_horizontal_position(self):
        return self.horizontal_servo.angle

