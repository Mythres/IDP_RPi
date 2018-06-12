import sys
import time
import utils.communication as comm

# Init motor variables
max_speed = 160
max_speed_increase = 30

median_pos = 512


def update_speed(pos_difference, motor_speed, current_polarity):
    speed_updater = motor_speed

    # TODO use this variable to increase/decrease speed more fluently
    # Calculate change in speed
    speed_change = (max_speed_increase / median_pos) * abs(pos_difference)

    # Idle de-acceleration
    if -20 < pos_difference < 20:
        speed_updater -= max_speed_increase / 2
        if speed_updater < 0:
            speed_updater = 0

    # Forward throttle
    if pos_difference > 20 and current_polarity is True:

        # Normal throttle
        speed_updater += speed_change

        # Check to not exceed max speed
        if speed_updater > max_speed:
            speed_updater = max_speed

    # Back throttle
    if pos_difference < -20 and current_polarity is False:

        # Normal throttle
        speed_updater += speed_change

        # Check to not exceed max speed
        if speed_updater > max_speed:
            speed_updater = max_speed

            # Forward de-acceleration
        if pos_difference < -20 and current_polarity is True and motor_speed > 0:
            speed_updater -= speed_change
            if speed_updater < 0:
                speed_updater = 0

                # Backward de-acceleration
        if pos_difference > 20 and current_polarity is False and motor_speed > 0:
            speed_updater -= speed_change
            if speed_updater < 0:
                speed_updater = 0

    return speed_updater


def polarity_update(pos_difference, current_polarity, current_speed):
    # Keep polarity when polarity is forward and joystick is pressed forward
    if current_polarity is True and pos_difference > 10:
        return current_polarity

    # Keep polarity when polarity is backwards and joystick is pressed backwards
    if current_polarity is False and pos_difference < -10:
        return current_polarity

    # Switch polarity from forward to backward
    if current_polarity is True and pos_difference < -10 and current_speed < 10:
        return False

    # Switch polarity from backward to forward
    if current_polarity is False and pos_difference > 10 > current_speed:
        return True

    return current_polarity


class Motor:
    def __init__(self):
        self.name = "motor"
        self.conn = None
        self.left_speed = 0
        self.right_speed = 0
        self.left_motor_polarity = True
        self.right_motor_polarity = False
        self.left_joy_xpos = 0
        self.right_joy_xpos = 0
        self.left_pos_difference = 0
        self.right_pos_difference = 0

    def run(self, conn):
        self.conn = conn
        comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Started")

        while True:
            self.handleMessages()
            # TODO Grab from bluetooth
            self.left_joy_xpos
            self.right_joy_xpos

            self.left_pos_difference = self.left_joy_xpos - median_pos
            self.right_pos_difference = self.right_joy_xpos - median_pos

            self.left_speed = update_speed(self.left_pos_difference, self.left_speed, self.left_motor_polarity)
            self.right_speed = update_speed(self.right_pos_difference, self.right_speed, self.right_motor_polarity)

    def handleMessages(self):
        if self.conn.poll():
            received = comm.recv_msg(self.conn)

            if received == "Stop":
                self.is_stopped = True
                comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Stopped")
            elif received == "Unload":
                self.unload()
                comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Unloaded")
                sys.exit()

        while self.is_stopped:
            received = comm.recv_msg(self.conn)
            if received == "Start":
                self.is_stopped = False
                comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Started")
            elif received == "Unload":
                self.unload()
                comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Unloaded")
                sys.exit()

    def unload(self):
        {}


motor = None


def name():
    return motor.name


def load():
    global motor
    motor = motor()


def unload():
    i = 0


def start(conn):
    try:
        motor.run(conn)
    except KeyboardInterrupt:
        motor.unload()
        sys.exit(1)
