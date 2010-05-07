# Meta-informations about Weka classifiers and datasets

import re, utils

ARFF_ATTRIBUTE = re.compile("@ATTRIBUTE\s+(:?[\"'](.*?)[\"']|(.*?))\s+(.*)", re.I)

# Extraction of meta-information from an ARFF dataset
class Dataset:

	def __init__ (self, arff_filename, class_index = -1):
		self.__class_type = None
		self.__attributes_types = []

		for line in utils.TextReader(arff_filename, False):
			m = ARFF_ATTRIBUTE.match(line)
			if (not m):
				continue

			attribute_name, attribute_type = m.group(1), m.group(4)

			# nominal attribute
			if (attribute_type[0] == '{'):
				attribute = ("nominal", attribute_name)

			# any other
			else:
				attribute = (attribute_type.lower(), attribute_name)
				assert (attribute[0] in ("numeric", "string", "date")), "Invalid attribute type : '%s'" % attribute[0]

			self.__attributes_types.append(attribute)

		# extraction of the class
		self.__class_type = self.__attributes_types[class_index]
		del self.__attributes_types[class_index]

	def get_class (self):
		return self.__class_type

	def get_attribute (self, index):
		return self.__attributes_types[index]

	def get_attributes (self):
		return self.__attributes_types

# Meta-informations about Weka classifiers (rely on 'classifiers.properties')
class Classifiers:

	def __init__ (self, properties_filename):

		# getting properties for supported attributes and classes types
		input_properties = (
		  (2, ("nominal", "nominal")),
		  (3, ("nominal", "numeric")),
		  (4, ("numeric", "nominal")),
		  (5, ("numeric", "numeric"))
		 )

		self.classifiers_properties = {}

		for data in utils.TextReader(properties_filename):
			classifier = data[0]

			for (index, t) in input_properties:
				if (not classifier in self.classifiers_properties):
					self.classifiers_properties[classifier] = {}
				
				if (data[index] == "1"):
					self.classifiers_properties[classifier][t] = True

	# get the list of the declared classifiers
	def declared_classifiers (self):
		return self.classifiers_properties.keys()

	# get the list of the classifiers compatible with given types
	def compatible_classifiers (self, class_type, attributes_types):

		classifiers = []
		for classifier, inputs in self.classifiers_properties.iteritems():
			compatible = True
			for attribute in attributes_types:
				if not (class_type[0], attribute[0]) in inputs:
					compatible = False
					break

			if compatible:
				classifiers.append(classifier)

		classifiers.sort()
		return classifiers
