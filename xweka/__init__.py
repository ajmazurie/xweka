
__version_major__ = 0
__version_minor__ = 2
__revision__ = 1
__build__ = "211DCEC"

version = "%s.%s (revision %s, build %s)" % (
	__version_major__,
	__version_minor__,
	__revision__,
	__build__
)

from parser import parse_WEKA_results
from finder import find_compatible_schemes
