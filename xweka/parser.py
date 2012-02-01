
import sys
import pyparsing as pp

pp.ParserElement.setDefaultWhitespaceChars(" \t")

SOL = pp.Suppress(pp.LineStart()).setName("START_OF_LINE")
EOL = pp.Suppress(pp.LineEnd()).setName("END_OF_LINE")

EMPTY_LINES = pp.Suppress(pp.OneOrMore(pp.LineEnd())).setName("EMPTY_LINES")

def int_or_float (value):
	if (value == 0):
		value_ = value + 1
	else:
		value_ = value

	if ((int(value_) / value_) == 1):
		return int(value)
	else:
		return value

REAL = pp.Combine(
	pp.Optional(pp.oneOf("+ -")) +
	pp.Word(pp.nums) +
	pp.Optional(pp.Literal('.')) +
	pp.Optional(pp.Word(pp.nums))
)\
	.setParseAction(lambda tokens: int_or_float(float(tokens[0])))\
	.setName("REAL")

INTEGER = pp.Word(pp.nums)\
	.setParseAction(lambda tokens: int(tokens[0]))\
	.setName("INTEGER")

#:::::::::::::::::::::::::::::::::::::::::::::::::::::: Grammar for WEKA scores

# Training and test scores
SCORES_HEADER = \
	SOL + \
	(
		pp.Literal("=== Evaluation on training set ===") ^ \
		pp.Literal("=== Error on training data ===") ^ \
		pp.Literal("=== Evaluation on test set ===") ^ \
		pp.Literal("=== Error on test data ===") ^ \
		pp.Literal("=== Stratified cross-validation ===") ^ \
		pp.Literal("=== Cross-validation ===") ^ \
		pp.Literal("=== Evaluation on test split ===")
	).setParseAction(lambda tokens: tokens[0][4:-4].lower()) + \
	pp.Optional(EOL + SOL + pp.Suppress("=== Summary ===")) + \
	EOL

SCORES_ENTRY = \
	SOL + \
	pp.Group(
		pp.Regex("([A-Za-z0-9\.\(\)]+ ?)+").setParseAction(lambda tokens: tokens[0].strip().lower()) + \
		pp.delimitedList(pp.OneOrMore(REAL), delim = "  ")
	).setWhitespaceChars(" ") + \
	pp.Optional(pp.Suppress('%')) + \
	EOL

SCORES_BLOCK = \
	SCORES_HEADER + \
	EMPTY_LINES + \
	pp.Group(pp.OneOrMore(SCORES_ENTRY))

# Accuracy per class
ACCURACY_PER_CLASS_HEADER = \
	SOL + \
	pp.Literal("=== Detailed Accuracy By Class ===").setParseAction(lambda tokens: "accuracy by class") + \
	EMPTY_LINES + \
	pp.Suppress(
		pp.Literal("TP Rate") +
		pp.Literal("FP Rate") +
		pp.Literal("Precision") +
		pp.Literal("Recall") +
		pp.Literal("F-Measure") +
		pp.Optional(pp.Literal("ROC Area")) +
		pp.Literal("Class")
	) + \
	EOL

ACCURACY_PER_CLASS_ENTRY = \
	REAL + \
	REAL + \
	REAL + \
	REAL + \
	REAL + \
	pp.Optional(REAL ^ '?') + \
	pp.Word(pp.printables) + \
	EOL

ACCURACY_PER_CLASS_BLOCK = \
	ACCURACY_PER_CLASS_HEADER + \
	pp.Group(pp.OneOrMore(pp.Group(ACCURACY_PER_CLASS_ENTRY))) + \
	pp.Suppress(pp.Literal("Weighted Avg.") + pp.OneOrMore(REAL))

# Confusion matrix
CONFUSION_MATRIX_HEADER = \
	SOL + \
	pp.Literal("=== Confusion Matrix ===").setParseAction(lambda tokens: "confusion matrix") + \
	EMPTY_LINES + \
	pp.Suppress(pp.OneOrMore(pp.Word(pp.alphanums)) + "<-- classified as") + \
	EOL

CONFUSION_MATRIX_ENTRY = \
	pp.OneOrMore(INTEGER) + \
	pp.Suppress('|' + pp.Word(pp.alphanums) + '=') + \
	pp.Word(pp.printables) + \
	EOL

CONFUSION_MATRIX_BLOCK = \
	CONFUSION_MATRIX_HEADER + \
	pp.Group(pp.OneOrMore(pp.Group(CONFUSION_MATRIX_ENTRY)))

# Whole report
WEKA_SCORES = \
	pp.Suppress(pp.SkipTo(SCORES_HEADER)) + \
	pp.OneOrMore(
		SCORES_BLOCK + EMPTY_LINES + \
		pp.Optional(ACCURACY_PER_CLASS_BLOCK + EMPTY_LINES) + \
		pp.Optional(CONFUSION_MATRIX_BLOCK + EMPTY_LINES)
	)

#::::::::::::::::::::::::::::::::::::::::::::::::: Grammar for WEKA predictions

PREDICTIONS_HEADER = \
	EMPTY_LINES + \
	pp.Literal("=== Predictions on test data ===") + \
	EMPTY_LINES + \
	pp.Literal("inst#") + \
	pp.Literal("actual") + \
	pp.Literal("predicted") + \
	pp.restOfLine

WEKA_PREDICTIONS = \
	pp.Suppress(PREDICTIONS_HEADER)

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def error (msg):
	print >>sys.stderr, "ERROR: " + msg
	sys.exit(1)

def parse (grammar, text):
	if (text.strip() == ''):
		error("Empty WEKA output.")

	try:
		return grammar.parseString(text)

	except pp.ParseException as msg:
		error(
			"Invalid WEKA output.\n" + \
			"%s\n" % msg.line + \
			' ' * (msg.column - 1) + "^\n%s" % msg
		)

def parse_WEKA_scores (text):
	data = parse(WEKA_SCORES, text)

	if (len(data) % 2 != 0):
		error("Invalid WEKA output: blocks are missing.")

	performance_on = {
		"evaluation on training set": "training",
		"error on training data": "training",
		"evaluation on test set": "test",
		"error on test data": "test",
		"stratified cross-validation": "cross-validation",
		"cross-validation": "cross-validation",
		"evaluation on test split": "cross-validation"
	}

	accuracy_scores = ("TP rate", "FP rate", "precision", "recall", "F-measure", "ROC area")

	results = {}
	for i in range(0, len(data), 2):
		block_name, block_data = data[i:i+2]

		if (block_name in performance_on):
			performance_on_ = performance_on[block_name]
			assert (performance_on_ not in results) ###

			scores = {}
			for entry in block_data:
				score_name, value = entry[0], entry[-1]
				scores[score_name] = value

			results[performance_on_] = {"scores": scores}

		elif (block_name == "accuracy by class"):
			assert (performance_on_ != None) ###

			accuracies = {}
			for entry in block_data:
				scores, class_name = entry[:-1], entry[-1]
				assert (len(scores) in (5, 6)) ###

				scores = dict(zip(accuracy_scores, scores))

				assert (class_name not in accuracies) ###
				accuracies[class_name] = scores

			assert ("accuracy by class" not in results[performance_on_]) ###
			results[performance_on_]["accuracy by class"] = accuracies

		elif (block_name == "confusion matrix"):
			assert (performance_on_ != None) ###

			counts, known_classes = [], []
			for entry in block_data:
				counts.append(entry[:-1])
				known_classes.append(entry[-1])

			matrix = {}
			for i, known_class in enumerate(known_classes):
				for j, predicted_class in enumerate(known_classes):
					if (not known_class in matrix):
						matrix[known_class] = {}

					assert (not predicted_class in matrix[known_class]) ###
					matrix[known_class][predicted_class] = counts[i][j]

			assert ("confusion matrix" not in results[performance_on_]) ###
			results[performance_on_]["confusion matrix"] = matrix

		else:
			error(block_name)

	return results

def parse_WEKA_predictions (text):
	parse(WEKA_PREDICTIONS, text)
	data = [line.strip() for line in text.split('\n')]

	i = data.index("=== Predictions on test data ===") + 3

	results = []
	while True:
		if (data[i] == ''):
			break

		items = data[i].split()
		actual = items[1].split(':', 1)[1]
		predicted = items[2].split(':', 1)[1]

		results.append((actual, predicted))
		i += 1

	return results
