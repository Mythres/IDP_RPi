import sys
import time
import utils.communication as comm
import drivers.Motor.motor as motor
import serial
from drivers.visioncore import CoreVision
import cv2
# import scipy
# from scipy import interpolate
from drivers.visioncore.MathHelper import MathHelper
import utils.communication as comm


class Knabenwunderhorn:
    def __init__(self):
        self.name = "knabenwunderhorn"
        self.conn = None
        self.is_stopped = False
        self.left_joy_xpos = 512
        self.right_joy_xpos = 512
        self.left_joy_ypos = 512
        self.right_joy_ypos = 512
        self.serial = serial.Serial("/dev/ttyACM0")
        self.vision = DotVision.DotVisionHandler("RedDotVision", "Vision to find center of red dot")

    def run(self, conn):
        self.conn = conn
        comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Started")
        motor_driver = motor.Motor(100, 80)


        while True:
            self.handleMessages()

            # TODO: Vision to recognise red circle for mandatory stop?
            # TODO  self.vision.imageHandler.loadFrameAsset(cv2.imread('../assets/images/cup5.jpg', cv2.IMREAD_COLOR), True) # load camera asset
            # TODO  self.vision.do_Vision() # do vision here

            # Update motor
            left_speed, left_polarity, right_speed, right_polarity = motor_driver.update(self.left_joy_ypos, self.right_joy_ypos)

            motor_values = str(int(round(left_speed))) + "," + str(left_polarity) + "," + str(int(round(right_speed))) + "," + str(right_polarity)

            comm.send_msg(self.conn, comm.MsgTypes.STATUS, motor_values)

            # Write to serial
            self.serial.write(bytes(motor_values + ";", "utf-8"))

            time.sleep(0.1)

    def handleMessages(self):
        if self.conn.poll():
            received = comm.recv_msg(self.conn)
            received_split = received.split(" ")
            if received_split[0] == "controller":
                controller_values = received_split[1].split("-")
                print(received_split)

                print(controller_values)

                # Grab positions
                self.left_joy_ypos = int(controller_values[0].split(":")[1].split(",")[0])
                self.right_joy_ypos = int(controller_values[1].split(":")[1].split(",")[0])
                self.left_joy_xpos = int(controller_values[0].split(":")[1].split(",")[1])
                self.right_joy_xpos = int(controller_values[1].split(":")[1].split(",")[1])

                comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Received")
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


knabenwunderhorn = None


def name():
    return knabenwunderhorn.name


def load():
    global knabenwunderhorn
    knabenwunderhorn = Knabenwunderhorn()


def unload():
    {}


def start(conn):
    try:
        knabenwunderhorn.run(conn)
    except KeyboardInterrupt:
        knabenwunderhorn.unload()
        sys.exit(1)


class DotImageHandler(CoreVision.CoreImageHandler):
    """Handles cup image"""

    def __init__(self, displayName, functionDescription, verboseLogs=False):
        super(DotImageHandler, self).__init__(displayName, functionDescription, verboseLogs)
        self.__resize = (750, 1000)

    def updateFrameAssetBeforeLoad(self, input):
        pass

    def postUpdateWithVision(self):
        print("testpostupdate")

    def preUpdateWithVision(self):
        print("testpreupdate")

    def checkConstraints_Custom(self, visionHandler=NotImplemented):
        print("testconstraints")


class DotVisionHandler(CoreVision.CoreVisionHandler):
    def __init__(self, displayName="", functionDescription=""):
        super(DotVisionHandler, self).__init__(DotImageHandler(displayName, functionDescription, True), displayName,
                                               functionDescription)

    def visionLogic(self):

        def houghTransformApproach():
            self.workingFrame = cv2.resize(self.workingFrame, (750, 1000))
            gray = cv2.cvtColor(self.workingFrame, cv2.COLOR_BGR2GRAY)
            gray = cv2.medianBlur(gray, 5)

            rows = gray.shape[0]
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8,
                                       param1=10, param2=60,
                                       minRadius=50, maxRadius=450)

            if circles is not None:
                circles = np.uint16(np.around(circles))
                for i in circles[0, :]:
                    print("a circle!")
                    center = (i[0], i[1])
                    # circle center
                    cv2.circle(self.workingFrame, center, 1, (0, 100, 100), 3)
                    # circle outline
                    radius = i[2]
                    cv2.circle(self.workingFrame, center, radius, (255, 0, 255), 3)

            cv2.imshow("detected circles", self.workingFrame)

        def contourAreaApproach():
            self.workingFrame = cv2.resize(self.workingFrame, (750, 1000))
            gray = cv2.cvtColor(self.workingFrame, cv2.COLOR_BGR2GRAY)
            # cv2.imshow("gray", gray)
            ret, th = cv2.threshold(gray, 127, 255, 0)
            _, cnts, hier = cv2.findContours(th, 2, 1)
            cnt = cnts
            # big_contour = []
            # max = 0
            for c in cnt:
                area = cv2.contourArea(c)  # --- find the contour having biggest area ---
                if area > 100:  # --- filter noise ---
                    epsilon = cv2.arcLength(c, True)
                    approx = cv2.approxPolyDP(c, 0.02 * epsilon, True)
                    # -- get approx --
                    if len(approx) == 8:
                        cv2.drawContours(self.workingFrame, [c], -1, (0, 255, 0), 3)
                        M = cv2.moments(c)
                        cx = int(M['m10'] / M['m00'])
                        cy = int(M['m01'] / M['m00'])
                        cv2.circle(self.workingFrame, (cx, cy), 10, (255, 255, 255), -1)
            # if (area > max):
            # 	max = area
            # 	big_contour = i

            # final = cv2.drawContours(self.workingFrame, big_contour, -1, (0, 255, 0), 3)
            cv2.imshow("detected circles", self.workingFrame)

        contourAreaApproach()
        # houghTransformApproach()

        while True:
            if cv2.waitKey(1) != -1:
                break
        cv2.destroyAllWindows()

        self.visionFrame = np.copy(self.workingFrame)
        return True, self.visionFrame