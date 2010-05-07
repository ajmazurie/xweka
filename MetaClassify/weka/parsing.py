# Parsing of Weka output

from pyparsing import *

REAL = Combine(Word("+-" + nums, nums) + Optional('.' + Optional(Word(nums))))

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::: Classification report

TRAINING_PERFORMANCES_SECTION = \
  Literal("=== Error on training data ===")

TEST_PERFORMANCES_SECTION = \
  Literal("=== Stratified cross-validation ===") ^ \
  Literal("=== Cross-validation ===") ^ \
  Literal("=== Error on test data ===")

PERFORMANCE_ITEM = \
  Word(alphas + ' ') + OneOrMore(REAL) + Suppress(Optional('%'))

ACCURACY_PER_CLASS_SECTION = Literal("=== Detailed Accuracy By Class ===") + Suppress(
  Literal("TP Rate") + \
  Literal("FP Rate") + \
  Literal("Precision") + \
  Literal("Recall") + \
  Literal("F-Measure") + \
  Literal("ROC Area") + \
  Literal("Class"))

ACCURACY_ITEM = \
  REAL + \
  REAL + \
  REAL + \
  REAL + \
  REAL + \
  (REAL ^ '?') + \
  Word(printables)

CONFUSION_MATRIX_SECTION = Literal("=== Confusion Matrix ===") + \
  Suppress(OneOrMore(Word(alphanums)) + "<-- classified as")

CONFUSION_MATRIX_ITEM = \
  OneOrMore(Word(nums)) + Suppress('|' + Word(alphanums) + '=') + Word(printables)

CLASSIFICATION_REPORT = \
  Suppress(SkipTo(TRAINING_PERFORMANCES_SECTION | TEST_PERFORMANCES_SECTION)) + \
  Optional(
    TRAINING_PERFORMANCES_SECTION + \
    Group(OneOrMore(Group(PERFORMANCE_ITEM))) + \
    Optional(
      ACCURACY_PER_CLASS_SECTION + \
      Group(OneOrMore(Group(ACCURACY_ITEM))) + \
      CONFUSION_MATRIX_SECTION + \
      Group(OneOrMore(Group(CONFUSION_MATRIX_ITEM)))
     )
   ) + \
  TEST_PERFORMANCES_SECTION + \
  Group(OneOrMore(Group(PERFORMANCE_ITEM))) + \
  Optional(
    ACCURACY_PER_CLASS_SECTION + \
    Group(OneOrMore(Group(ACCURACY_ITEM))) + \
    CONFUSION_MATRIX_SECTION + \
    Group(OneOrMore(Group(CONFUSION_MATRIX_ITEM)))
   )

CLASSIFICATION_PERFORMANCE_KEYWORDS = (
  # classification results
  "Correctly classified instances",
  "Incorrectly classified instances",
  "Kappa statistic",

  # regression results
  "Correlation coefficient",

  # both
  "Mean absolute error",
  "Root mean squared error",
  "Relative absolute error",
  "Root relative squared error",
 )

CLASSIFICATION_ACCURACY_KEYWORDS = (
  "TP Rate",
  "FP Rate",
  "Precision",
  "Recall",
  "F-Measure",
  "ROC Area",
 )

CLASSIFICATION_MODEL = 0
REGRESSION_MODEL = 1

def extract_classification_results (stream, extract_training_errors):

	def __extract_performances (block):
		m, performances = {}, []

		for item in block:
			key, value = item[0].strip().capitalize(), item[-1]
			m[key] = value

		for keyword in CLASSIFICATION_PERFORMANCE_KEYWORDS:
			if keyword in m:
				performances.append(m[keyword])
			else:
				performances.append('-')

		return performances

	def __extract_accuracy_per_class (block):
		accuracy = []

		for item in block:
			clazz, scores = item[-1].strip("'").strip('"'), item[:-1]
			accuracy.append((clazz, scores))

		return accuracy

	def __extract_confusion_matrix (block):
		matrix = {}

		for item in block:
			clazz, scores = item[-1].strip("'").strip('"'), item[:-1]
			matrix[clazz] = scores

		return matrix

	stream = ''.join(stream)
	stream = stream.strip()

	assert (stream != ''), "Empty WEKA output"

	try:
		data = CLASSIFICATION_REPORT.parseString(stream)

		# Is there a section describing the performance on a training set ?
		is_training_set = (data[0] == "=== Error on training data ===")

		# Did we have a classification or a regression model ?
		n = len(data)

		if (is_training_set):
			assert (n == 4) or (n == 12)
			is_classification = (n == 12)
		else:
			assert (n == 2) or (n == 6)
			is_classification = (n == 6)

		model_type = {
		  True : CLASSIFICATION_MODEL,
		  False : REGRESSION_MODEL
		 }[is_classification]

		# Extraction of the scores
		if (extract_training_errors):
			assert is_training_set, "No report found for errors on training set"
			offset = 0

		elif (not is_training_set):
			offset = 0

		else:
			if (is_classification):
				offset = 6
			else:
				offset = 2

		performances = __extract_performances(data[1 + offset])

		if (is_classification):
			accuracy = __extract_accuracy_per_class(data[3 + offset])
			matrix = __extract_confusion_matrix(data[5 + offset])
		else:
			accuracy, matrix = None, None

		return model_type, performances, accuracy, matrix

	except ParseException, err:
		raise Exception(
		  "Invalid WEKA output.\n" +
		  "%s\n" % err.line +
		  ' ' * (err.column - 1) + "^\n%s" % err
		 )
