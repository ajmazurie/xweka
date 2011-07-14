
import sys, subprocess
import os

def error (msg):
	print >>sys.stderr, "ERROR: " + msg
	sys.exit(1)

def find_compatible_schemes (fn, java_cmd = "java"):
	cmd = ' '.join((
		"%s weka.core.FindWithCapabilities" % java_cmd,
		"-superclass weka.classifiers.Classifier",
		"-generic",
		"-misses",
		"-t %s" % fn
	))

	try:
		process = subprocess.Popen(
			cmd, shell = True,
			bufsize = 1,
			stdin = None,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			close_fds = True
		)

		stdout = process.stdout.readlines()
		stderr = process.stderr.readlines()

	except Exception as msg:
		error("Unable to execute WEKA: %s" % msg)

	if (stderr[0].startswith("java.io.IOException")):
		error("Invalid input: %s" % stderr[0][21:].strip())

	compatible_list = []
	start_compatible_list = False

	uncompatible_list = []
	start_uncompatible_list = False

	for line in stdout:
		line = line.strip()
		if (line == ''):
			continue

		if (line.endswith("that matched the criteria:")):
			start_compatible_list = True
			start_uncompatible_list = False
			continue

		if (line.endswith("that didn't match the criteria:")):
			start_compatible_list = False
			start_uncompatible_list = True
			continue

		if (start_compatible_list):
			assert line.startswith("weka.classifiers"), line ###
			if (not ".meta." in line):
				compatible_list.append(line)
			continue

		if (start_uncompatible_list):
			assert line.startswith("weka.classifiers"), line ###
			if (not ".meta." in line):
				uncompatible_list.append(line)
			continue

	return sorted(compatible_list), sorted(uncompatible_list)

""" in Jython:

import java
import weka

finder = weka.core.FindWithCapabilities()
finder.setOptions(["-superclass", "weka.classifiers.Classifier", "-generic"])
finder.setClassIndex("last")

try:
	finder.setFilename(p.i_fn)

except java.io.IOException, msg:
	error("Invalid format: %s" % msg)

finder.find()

print finder.getMatches()
print finder.getMisses()
"""