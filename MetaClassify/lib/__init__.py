
# Miscellaneous methods

import os, sys

class TextReader:

	def __init__ (self, file, split = True):
		if (not os.path.exists(file)):
			print >>sys.stderr, " Error: file '%s' not found." % file
			sys.exit(1)

		self.source = open(file, 'r')
		self.split = split

	def __iter__ (self):
		return self

	def next (self):
		while True:
			line = self.source.readline()

			if (line == ''):
				self.source.close()
				raise StopIteration

			line = line.strip()

			if (line == '') or (line[0] == '#'):
				continue

			if self.split:
				return line.split('	')
			else:
				return line

PATH = os.path.dirname(__file__)

import weka_capabilities, weka_output
