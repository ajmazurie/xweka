
__version_major__ = 1
__version_minor__ = 4
__revision__ = 5
__build__ = "88DB8DA"

version = "%s.%s (revision %s, build %s)" % (
	__version_major__,
	__version_minor__,
	__revision__,
	__build__
)

from parser import parse_WEKA_results
from finder import find_compatible_schemes
