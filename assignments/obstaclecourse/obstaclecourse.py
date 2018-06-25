import sys
import time
import utils.communication as comm
import drivers.Motor.motor as motor
import serial
import abc
import numpy as np
from drivers.visioncore import CoreVision
import cv2
# import scipy
# from scipy import interpolate
from drivers.visioncore.MathHelper import MathHelper


class Obstaclecourse:
    def __init__(self):
        self.name = "obstaclecourse"
        self.conn = None
        self.is_stopped = False
        self.left_joy_xpos = 512
        self.right_joy_xpos = 512
        self.left_joy_ypos = 512
        self.right_joy_ypos = 512
        self.serial = serial.Serial("/dev/ttyACM0")
        self.vision = CupVisionHandler("CupVision", "Vision to detect cup")

    def run(self, conn):
        self.conn = conn
        comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Started")
        motor_driver = motor.Motor(250, 100)

        while True:
            self.handleMessages()

            # TODO  self.vision.imageHandler.loadFrameAsset(cv2.imread('../assets/images/rstip2.jpg', cv2.IMREAD_COLOR), True) # load camera asset
            # TODO  self.vision.do_Vision() # do vision here

            # Update motor
            left_speed, left_polarity, right_speed, right_polarity = motor_driver.update(self.left_joy_xpos, self.right_joy_xpos)

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
                controller_values = received_split[1].split(",")
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


obstaclecourse = None


def name():
    return obstaclecourse.name


def load():
    global obstaclecourse
    obstaclecourse = Obstaclecourse()


def unload():
    {}


def start(conn):
    try:
        obstaclecourse.run(conn)
    except KeyboardInterrupt:
        obstaclecourse.unload()
        sys.exit(1)


# ============== implementation ==============
class CupImageHandler(CoreVision.CoreImageHandler):
    """Handles cup image"""

    def __init__(self, displayName, functionDescription, verboseLogs=False):
        super(CupImageHandler, self).__init__(displayName, functionDescription, verboseLogs)
        self.__resize = (750, 1000)
        self.__blur_KernelSize = (5, 5)

    def updateFrameAssetBeforeLoad(self, input):
        pass

    def postUpdateWithVision(self):
        print("testpostupdate")

    def preUpdateWithVision(self):
        print("testpreupdate")

    def checkConstraints_Custom(self, visionHandler=NotImplemented):
        print("testconstraints")


class CupVisionHandler(CoreVision.CoreVisionHandler):
    def __init__(self, displayName="", functionDescription=""):
        super(CupVisionHandler, self).__init__(CupImageHandler(displayName, functionDescription, True), displayName,
                                               functionDescription)
        """"Settings"""
        # todo remove debug settings
        self.drawApprox = False
        self.drawCenterMoment = True
        self.showSteps = False
        self.showResult = True
        self.dynamicCenterMomentSize = True
        self.drawCenterRectangle = True
        self.printDebug = True
        self.centerRectangleRelSize = 0.2
        self.centerRectangleColor = (0, 255, 255)
        self.centerRectangleThickness = 4
        self.staticCenterMomentSize = 10
        self.resize = (750, 1000)
        self.approxLen = [8, 4]
        self.contourColor = (0, 255, 0)
        self.contourThickness = 4
        self.centerMomentColor = (0, 0, 255)

    def visionLogic(self):
        def prepareFrame():
            self.workingFrame = cv2.resize(self.workingFrame, self.resize)
            gray = cv2.cvtColor(self.workingFrame, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)

            if self.showSteps:
                cv2.imshow("Gray", blur)

            edged = cv2.Canny(blur, 10, 50)
            if self.showSteps:
                cv2.imshow("Edged", edged)
            # construct and apply a closing kernel to 'close' gaps between 'white' pixels
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
            self.closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
            if self.showSteps:
                cv2.imshow("Closed", self.closed)

        def getContours():
            # find contours (i.e. the 'outlines') in the image and initialize the
            # total number of books found
            _, cnts, _ = cv2.findContours(self.closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # for some reason this broke :(
            # todo needs scipy
            # makes outline better!

            # smoothened = []
            # for contour in cnts:
            #     x, y = contour.T
            #     # Convert from numpy arrays to normal arrays
            #     x = x.tolist()[0]
            #     y = y.tolist()[0]
            #     # https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.interpolate.splprep.html
            #     tck, u = interpolate.splprep([x, y], u=None, s=1, per=1)
            #     # https://docs.scipy.org/doc/numpy-1.10.1/reference/generated/numpy.linspace.html
            #     u_new = np.linspace(u.min(), u.max(), 25)
            #     # https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.interpolate.splev.html
            #     x_new, y_new = interpolate.splev(u_new, tck, der=0)
            #     # Convert it back to numpy format for opencv2 to be able to display it
            #     res_array = [[[int(i[0]), int(i[1])]] for i in zip(x_new, y_new)]
            #     smoothened.append(np.asarray(res_array, dtype=np.int32))

            self.contours = cnts

        def drawContours():
            self.cx = 0
            self.cy = 0
            self.ct = 0
            self.ca = 0

            # loop over the contours
            for c in self.contours:
                # approximate the contour
                epsilon = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * epsilon, True)

                # print(area)

                # approximate the points of the vertices
                # print(len(approx))
                # if len(approx) == 8 or len(approx) == 4:
                isLen = False
                if isinstance(self.approxLen, list):
                    for arrLen in self.approxLen:
                        if len(approx) == arrLen or len(approx) == arrLen - 1 or len(approx) == arrLen + 1:
                            isLen = True
                            break
                else:
                    # noinspection PyTypeChecker
                    isLen = len(approx) == self.approxLen or len(approx) == self.approxLen - 1 or len(
                        approx) == self.approxLen + 1

                if isLen:
                    subject = approx if self.drawApprox else c

                    area = cv2.contourArea(subject)
                    if area > 5000:
                        cv2.drawContours(self.workingFrame, [subject], -1, self.contourColor, self.contourThickness)

                        if self.drawCenterMoment:
                            self.ca += area * 0.00025
                            M = cv2.moments(c)
                            self.cx += int(M['m10'] / M['m00'])
                            self.cy += int(M['m01'] / M['m00'])
                            self.ct += 1

        def drawExtras():
            if self.drawCenterMoment and self.ct != 0:
                cx = int(self.cx / self.ct)
                cy = int(self.cy / self.ct)
                ca = int(self.ca / self.ct)
                cv2.circle(self.workingFrame, (cx, cy),
                           ca if self.dynamicCenterMomentSize else self.staticCenterMomentSize,
                           self.centerMomentColor, -1)

            middle = (int(self.resize[0] * 0.5), int(self.resize[1] * 0.5))
            rectSize = (
                int(self.resize[0] * self.centerRectangleRelSize), int(self.resize[1] * self.centerRectangleRelSize))
            rectOff = (int(rectSize[0] * 0.5), int(rectSize[1] * 0.5))
            rectTopLeft = (middle[0] - rectOff[0], middle[1] - rectOff[1])
            rectBottomRight = (middle[0] + rectOff[0], middle[1] + rectOff[1])

            # angleToCenterMoment = int(math.atan((middle[1] - cy) / (cx - middle[0])) * 180 / math.pi)

            angleToCenterMoment = int(MathHelper.clockwiseAngle(middle, (self.cx, self.cy)))

            if self.drawCenterRectangle:
                """Draw rect"""
                cv2.rectangle(self.workingFrame, rectTopLeft, rectBottomRight, self.centerRectangleColor,
                              thickness=self.centerRectangleThickness,
                              lineType=4, shift=0)
                """"Draw dot in rect"""
                cv2.circle(self.workingFrame, middle, self.centerRectangleThickness * 2, self.centerRectangleColor, -1)

                """Draw 0 deg line"""
                cv2.line(self.workingFrame, middle, (self.resize[0], middle[1]), (255, 0, 0), thickness=1, lineType=4,
                         shift=0)
                cv2.putText(self.workingFrame, '0deg',
                            (middle[0] + int((self.resize[0] - middle[0]) / 2), middle[1]),
                            cv2.FONT_HERSHEY_COMPLEX,
                            0.5,
                            (255, 255, 255),
                            1)
                """Draw line from dot to center moment"""
                cv2.line(self.workingFrame, middle, (self.cx, self.cy), (255, 0, 0), thickness=4, lineType=4, shift=0)
                cv2.putText(self.workingFrame, str(angleToCenterMoment) + 'deg',
                            (middle[0] + int((self.cx - middle[0]) / 2), middle[1] + int((self.cy - middle[1]) / 2)),
                            cv2.FONT_HERSHEY_COMPLEX,
                            0.5,
                            (255, 255, 255),
                            1)

            """"Get if the center moment is in the center rectangle"""
            self.centerMomentInRect = rectTopLeft[0] <= self.cx <= rectBottomRight[0] and rectTopLeft[1] <= self.cy <= \
                                                                                          rectBottomRight[
                                                                                              1]
            self.centerMomentOutSide = "None"
            if self.cx < rectTopLeft[0]:
                self.centerMomentOutSide = "Left"
            elif self.cx > rectBottomRight[0]:
                self.centerMomentOutSide = "Right"

            if self.printDebug:
                print("cx: " + str(self.cx) + " ; cy: " + str(self.cy))
                print("mx: " + str(middle[0]) + " ; my: " + str(middle[1]))
                print("inside rect: " + str(self.centerMomentInRect))
                print("side out of rect: " + self.centerMomentOutSide)
                # noinspection PyUnboundLocalVariable
                if angleToCenterMoment:
                    # noinspection PyUnboundLocalVariable
                    print("angle to center moment: " + str(angleToCenterMoment))

        prepareFrame()
        getContours()
        drawContours()
        drawExtras()

        if self.showResult:
            cv2.imshow("Output", self.workingFrame)

            while True:
                if cv2.waitKey(1) != -1:
                    break
            cv2.destroyAllWindows()

        self.visionFrame = np.copy(self.workingFrame)

        return True, self.visionFrame