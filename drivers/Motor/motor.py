from drivers.Motor import MotorDirections


class Motor:

    def __init__(self, max_speed, max_speed_increase):
        # Init motor variables
        self.max_speed = max_speed
        self.max_speed_increase = max_speed_increase
        self.median_pos = 512
        self.left_speed = 0
        self.right_speed = 0
        self.left_motor_polarity = True
        self.right_motor_polarity = True
        self.left_joy_xpos = 0
        self.right_joy_xpos = 0
        self.pos_range = 20

    def update_max_speed(self, max_speed=255, max_speed_increase=125):
        self.max_speed = max_speed
        self.max_speed_increase = max_speed_increase

    def update(self, left, right):
        left_pos_difference = left - self.median_pos
        right_pos_difference = right - self.median_pos

        # self.left_speed = 512 - left * 0.48
        # self.right_speed = right - 512 * 0.48

        self.left_speed = self.update_speed(left_pos_difference, self.left_speed, self.left_motor_polarity)
        self.right_speed = self.update_speed(right_pos_difference, self.right_speed, self.right_motor_polarity)

        # self.left_motor_polarity = True if self.left_speed > 0 else False
        # self.right_motor_polarity = True if self.left_speed > 0 else False

        self.left_motor_polarity = self.polarity_update(left_pos_difference, self.left_motor_polarity, self.left_speed)
        self.right_motor_polarity = self.polarity_update(right_pos_difference, self.right_motor_polarity,
                                                         self.right_speed)

        # Easier to send 1/0 to arduino compared to true/false
        if self.left_motor_polarity:
            polarity_sender_left = 0
        else:
            polarity_sender_left = 1

        if self.right_motor_polarity:
            polarity_sender_right = 0
        else:
            polarity_sender_right = 1

        return abs(self.left_speed), polarity_sender_left, abs(self.right_speed), polarity_sender_right

    def update_speed(self, pos_difference, motor_speed, current_polarity):
        speed_updater = motor_speed

        # Calculate change in speed
        speed_change = (self.max_speed_increase / self.median_pos) * abs(pos_difference)

        # Idle de-acceleration
        if -self.pos_range < pos_difference < self.pos_range:
            speed_updater -= self.max_speed_increase
            if speed_updater < 0:
                speed_updater = 0

        # Forward throttle
        if pos_difference > self.pos_range and current_polarity is True:

            # Normal throttle
            speed_updater += speed_change

            # Check to not exceed max speed
            if speed_updater > self.max_speed:
                speed_updater = self.max_speed

        # Back throttle
        if pos_difference < -self.pos_range and current_polarity is False:

            # Normal throttle
            speed_updater += speed_change

            # Check to not exceed max speed
            if speed_updater > self.max_speed:
                speed_updater = self.max_speed

        # Forward de-acceleration
        if pos_difference < -self.pos_range and current_polarity is True and motor_speed > 0:
            speed_updater -= speed_change * 2
            if speed_updater < 0:
                speed_updater = 0

        # Backward de-acceleration
        if pos_difference > self.pos_range and current_polarity is False and motor_speed > 0:
            speed_updater -= speed_change * 2
            if speed_updater < 0:
                speed_updater = 0

        return speed_updater

    def polarity_update(self, pos_difference, current_polarity, current_speed):
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

    def get_motor_values_string(self, left_speed, left_polarity, right_speed, right_polarity):
        return str(int(round(left_speed))) + "," + str(left_polarity) + "," + str(int(round(right_speed))) + "," + str(
            right_polarity)

    # returns the appropriate motor power. accepts an input between 0-512.
    # the value is automatically increased if based on forward movement
    def get_motor_power(self, power, np_direction=MotorDirections.FORWARD):
        self.__backward_power_check(power)
        return power + self.median_pos \
            if np_direction is MotorDirections.FORWARD \
            else self.median_pos - power

    # raises an exception if the power exceeds the bounds of forward movement (512-1024)
    def __forward_power_check(self, power):
        if power < self.median_pos:
            raise Exception("Power can not be lower than 512")
        elif power > self.median_pos * 2:
            raise Exception("Power can not be higher than 1024")
        return True

    # raises an exception if the power exceeds the bounds of backward movement (0-512)
    def __backward_power_check(self, power):
        if power < 0:
            raise Exception("Power can not be lower than 0")
        elif power > self.median_pos:
            raise Exception("Power can not be higher than 512")
        return True

    # power must be between 0-512
    # 0 would be no power, 512 would be full power
    # example: motor.move_forward(motor.get_motor_power(512, forward=True))
    # or:      motor.move_forward(512, True)
    # or:      motor.move_forward(1024)
    # all are full power examples
    def move_forward(self, power, autoTransform=False):
        if autoTransform:
            power = self.get_motor_power(power, MotorDirections.FORWARD)
        self.__forward_power_check(power)
        return self.update(power, power)

    # power must be between 0-512
    # 0 would be no power, 512 would be full power
    # example: motor.move_backward(motor.get_motor_power(512, forward=False))
    # or:      motor.move_backward(512, True)
    # or:      motor.move_backward(1024)
    # all are full power examples
    def move_backward(self, power, autoTransform=False):
        if autoTransform:
            power = self.get_motor_power(power, MotorDirections.BACKWARD)
        self.__backward_power_check(power)
        return self.update(power, power)

    # power must be between 0-512
    # 0 would be no power, 512 would be full power
    # all examples are full power, forward and to the right
    # example: motor.rotate_around_axis(motor.get_motor_power(512))
    # or:      motor.rotate_around_axis(512, autoTransform=True)
    # or:      motor.rotate_around_axis(1024)
    def rotate_around_axis(self, power, rp_direction=MotorDirections.RIGHT, autoTransform=False):
        oldPower = power
        forwPower = power
        backPower = power
        if autoTransform:
            forwPower = self.get_motor_power(oldPower, MotorDirections.FORWARD)
            backPower = self.get_motor_power(oldPower, MotorDirections.BACKWARD)
        self.__forward_power_check(forwPower)
        self.__backward_power_check(backPower)

        if rp_direction is MotorDirections.RIGHT:
            power_left = forwPower
            power_right = backPower
        else:
            power_left = backPower
            power_right = forwPower

        return self.update(power_left, power_right)
