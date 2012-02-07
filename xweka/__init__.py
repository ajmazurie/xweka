
__version_major__ = 1
__version_minor__ = 4
__revision__ = 8
__build__ = "A3A269D"

version = "%s.%s (revision %s, build %s)" % (
	__version_major__,
	__version_minor__,
	__revision__,
	__build__
)

from parser import parse_WEKA_scores, parse_WEKA_predictions
from finder import find_compatible_schemes
