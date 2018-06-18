class Motor:

    def __init__(self):
        # Init motor variables
        self.max_speed = 160
        self.max_speed_increase = 30
        self.median_pos = 512
        self.left_speed = 0
        self.right_speed = 0
        self.left_motor_polarity = True
        self.right_motor_polarity = False
        self.left_joy_xpos = 0
        self.right_joy_xpos = 0

    def update(self, left, right):
        left_pos_difference = left - median_pos
        right_pos_difference = right - median_pos

        self.left_speed = update_speed(left_pos_difference, self.left_speed, self.left_motor_polarity)
        self.right_speed = update_speed(right_pos_difference, self.right_speed, self.right_motor_polarity)

        self.left_motor_polarity = polarity_update(left_pos_difference, self.left_motor_polarity, self.left_speed);
        self.right_motor_polarity = polarity_update(right_pos_difference, self.right_motor_polarity, self.right_speed);

        # Easier to send 1/0 to arduino compared to true/false
        if self.left_motor_polarity:
            polarity_sender_left = 1
        else:
            polarity_sender_left = 0

        if self.right_motor_polarity:
            polarity_sender_right = 1
        else:
            polarity_sender_right = 0

        return self.left_speed, polarity_sender_left, self.right_speed, polarity_sender_right

    def update_speed(self, pos_difference, motor_speed, current_polarity):
        speed_updater = motor_speed

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

