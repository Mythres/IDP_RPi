import abc
import numpy as np
from drivers.visioncore import CoreVision
import cv2
# import scipy
# from scipy import interpolate
from drivers.visioncore.MathHelper import MathHelper
import utils.communication as comm


class Ass6:
	def __init__(self):
		self.name = "ass6"
		self.conn = None
		self.vision = DotVision.DotVisionHandler("RedDotVision", "Vision to find center of red dot")

	def run(self, conn):
		self.conn = conn
		comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Started")

		while True:
			pass  # todo code runs here ???
		# TODO  self.vision.imageHandler.loadFrameAsset(cv2.imread('../assets/images/cup5.jpg', cv2.IMREAD_COLOR), True) # load camera asset
		# TODO  self.vision.do_Vision() # do vision here


assignment = None


# todo needs commenting...
# todo needs abstraction?
def name():
	return assignment.name


def load():
	global assignment
	assignment = Ass6()


def start(conn):
	try:
		assignment.run(conn)
	except KeyboardInterrupt:
		assignment.unload()
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
