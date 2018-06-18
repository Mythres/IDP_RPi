import math


class MathHelper:
	@staticmethod
	def rotatePoint(point, radians):
		x = math.cos(radians) * point[0] - math.sin(radians) * point[1]
		y = math.sin(radians) * point[0] + math.cos(radians) * point[1]
		return x, y

	@staticmethod
	def rotateAroundPoint(point, center, radians):
		trans = (point[0] - center[0], point[1] - center[1])
		rot = MathHelper.rotatePoint(trans, radians)
		return rot[0] + center[0], rot[1] + center[1]

	@staticmethod
	def clockwiseAngle(center, b):
		angle = math.atan2(b[1] - center[1], b[0] - center[0]) * 180 / math.pi
		if angle < 0:
			angle = 360 - -angle
		return angle
