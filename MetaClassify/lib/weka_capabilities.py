
from __init__ import TextReader, PATH
import os, sys

class Classifiers:

	def __init__ (self, classifiers_filename = os.path.join(PATH, "weka_classifiers")):

		self.__classifiers = {}

		for data in TextReader(classifiers_filename):
			classifier = data[0]

			if (len(data) > 1):
				parameters = data[1]
			else:
				parameters = None

			self.__classifiers[classifier] = parameters

	def declared_classifiers (self):
		return sorted(self.__classifiers.keys())

	def compatible_classifiers (self, dataset_filename):

		classifiers = self.declared_classifiers()

		cmd = "java -cp %s:%s weka_capabilities %s %s" % (
		  PATH, os.environ.get("CLASSPATH", ''),
		  dataset_filename,
		  ','.join(classifiers)
		 )

		try:
			stream = os.popen(cmd, 'r')

			output = stream.readline().strip()
			status = stream.close()

			if (status != None):
				raise Exception("Child Java process returned an error code")

		except Exception, msg:
			print >>sys.stderr, " ERROR: Error while listing compatible classifiers.\n %s" % msg
			sys.exit(1)

		selected_classifiers = []

		for i, classifier in enumerate(classifiers):
			if (output[i] == '1'):
				selected_classifiers.append(classifier)

		return selected_classifiers

	def get_parameters (self, classifier):
		return self.__classifiers[classifier]
