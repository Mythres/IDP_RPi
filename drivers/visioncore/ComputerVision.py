import sys
import cv2

from visioncore import CupVision, DotVision


# from picamera.array import PiRGBArray
# from picamera import PiCamera
# import time

# todo remove this when no longer needed


class ComputerVision:
	"""The 'main' class, holds all custom vision classes"""

	def __init__(self):
		self.cupVision = CupVision.CupVisionHandler("CupVision", "Vision to detect cup")
		self.dotVision = DotVision.DotVisionHandler("RedDotVision", "Vision to find center of red dot")


if __name__ == "__main__":
	# todo missing assets
	# todo camera frame
	vision = ComputerVision()
	vision.cupVision.imageHandler.loadFrameAsset(cv2.imread('../assets/images/cup5.jpg', 1), True)
	# print(vision.cupVision.displayName)
	# print(vision.cupVision.functionDescription)
	# print(vision.cupVision.do_Vision())
	vision.dotVision.imageHandler.loadFrameAsset(cv2.imread('../assets/images/rstip2.jpg', cv2.IMREAD_COLOR), True)
	vision.dotVision.do_Vision()

# initialize the camera and grab a reference to the raw camera capture
# camera = PiCamera()
# camera.resolution = (1280, 720)
# camera.framerate = 24
# rawCapture = PiRGBArray(camera, size=(1280, 720))
#
# # allow the camera to warmup
# time.sleep(0.1)
#
# # capture frames from the camera
# for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
# 	# grab the raw NumPy array representing the image, then initialize the timestamp
# 	# and occupied/unoccupied text
# 	image = frame.array
#
# 	# show the frame
# 	cv2.imshow("Frame", image)
# 	key = cv2.waitKey(1) & 0xFF
#
# 	# clear the stream in preparation for the next frame
# 	rawCapture.truncate(0)
#
# 	# if the `q` key was pressed, break from the loop
# 	if key == ord("q"):
# 		break

# print(vision.cupVision.imageHandler.updateFrameAsset_WithVisionHandler(vision.cupVision))
#
# cv2.imshow("Output", vision.cupVision.GetFrameAsset())
#
# while True:
#     if cv2.waitKey(1) != -1:
#         break
# cv2.destroyAllWindows()
# print("bye")
