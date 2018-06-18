import numpy as np
import abc


class CoreImageHandler:
	__metaclass__ = abc.ABCMeta

	def __init__(self, displayName, functionDescription, verboseLogs=False):
		""""Initializes the image handler"""
		self.displayName = displayName
		self.functionDescription = functionDescription
		self.frameAsset = None
		self.verboseLogs = verboseLogs
		self.visionHandler = None

	# super(abc.ABC, self).__init__()

	@abc.abstractmethod
	def updateFrameAssetBeforeLoad(self, input):
		"""Allows updating the frame asset before it is loaded into the core vision
		Examples of usage are resizing"""
		pass

	def loadFrameAsset(self, input, forceLoad=False):
		"""Expects  a numpy array and loads it into frameAsset"""
		if self.frameAsset is None or forceLoad:
			self.updateFrameAssetBeforeLoad(input)
			self.frameAsset = input
		elif self.verboseLogs:
			print("Could not set frame asset (is not None). To force overwrite specify forceLoad")

	@abc.abstractmethod
	def postUpdateWithVision(self):
		"""Allows to do something after vision code"""
		pass

	@abc.abstractmethod
	def preUpdateWithVision(self):
		"""Allows to do something before vision code"""
		pass

	@abc.abstractmethod
	def checkConstraints_Custom(self, visionHandler=NotImplemented):
		"""Allows custom constraints checks, happens after default constraints"""
		pass

	def checkConstraints(self, visionHandler=NotImplemented):
		"""Checks constraints"""
		if self.frameAsset is None or not isinstance(self.frameAsset, np.ndarray):
			if self.verboseLogs:
				print("Frame asset was None or not numpy array when trying to apply vision")
			return False

		if visionHandler is not NotImplemented:
			if not isinstance(visionHandler, CoreVisionHandler):
				if self.verboseLogs:
					print("Given vision handler was not type of VisionHandler")
				return False

		self.checkConstraints(visionHandler)
		return True

	def updateFrameAsset_WithVisionHandler(self, visionHandler):
		"""Updates loaded asset with given vision handler"""

		ret = self.checkConstraints(visionHandler)

		if not ret:
			return False

		self.preUpdateWithVision()

		ret, retimg = visionHandler.__do_Vision(np.copy(self.frameAsset))
		if ret:
			self.frameAsset = retimg

		self.postUpdateWithVision()

		return True

	def updateVisionHandler(self, visionHandler):
		"""Updates the internal vision handler"""
		if not isinstance(visionHandler, CoreVisionHandler):
			if self.verboseLogs:
				print("Given vision handler was not type of VisionHandler")
			return False

		self.visionHandler = visionHandler
		return True

	def updateFrameAsset_AsSelf(self):
		"""Updates loaded asset using internal vision handler"""
		self.preUpdateWithVision()

		if self.frameAsset is None:
			if self.verboseLogs:
				print("Frame asset was None when trying to apply vision")
			return False

		if self.visionHandler is None:
			if self.verboseLogs:
				print("Given vision handler was not type of VisionHandler or is None")
			return False

		ret, retimg = self.visionHandler.__do_Vision(np.copy(self.frameAsset))
		if ret:
			self.frameAsset = retimg

		self.postUpdateWithVision()

		return True


class CoreVisionHandler:
	__metaclass__ = abc.ABCMeta

	def __init__(self, imageHandler, displayName="", functionDescription=""):
		"""Sets up the vision handler, has an embedded image handler"""
		self.displayName = displayName
		self.functionDescription = functionDescription
		if not isinstance(imageHandler, CoreImageHandler):
			raise TypeError("Given image handler is not of type ImageHandler")
		self.imageHandler = imageHandler
		self.visionFrame = None
		self.workingFrame = None

	# super(abc.ABC, self).__init__()

	def GetFrameAsset(self):
		"""Gets the frame asset by the embedded image handler"""
		return self.imageHandler.frameAsset

	def pre_Vision(self):
		"""Runs right before vision, will update the frames"""
		self.visionFrame = None  # the frame that vision should set as result
		self.workingFrame = np.copy(self.GetFrameAsset())  # the frame vision should use to perform vision on

	def do_Vision(self):
		"""Runs vision"""
		self.pre_Vision()
		return self.visionLogic()

	@abc.abstractmethod
	def visionLogic(self):
		"""Performs the custom vision on the self.workingFrame asset. Should return ret, retimg"""
		raise NotImplementedError("doVision remains unimplemented for " + __name__)

	def do_Vision_Local(self):
		"""Performs the vision on the local frame asset, and sets self.visionFrame if there is a result
		Returns success"""
		if self.GetFrameAsset() is None or self.GetFrameAsset() is not np.array:
			return False

		ret, retimg = self.do_Vision()
		if ret:
			self.visionFrame = retimg
		return ret
