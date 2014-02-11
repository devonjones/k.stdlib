"""Improvements surrounding the options for
and configuration of logging.
"""
import logging
import sys
from k.stdlib.collections import defaultnamedtuple

_LoggingOptions = defaultnamedtuple( #pylint: disable-msg=C0103
		'LoggingOptions',
		['logfile', 'loglevel'],
		logfile="stderr", loglevel='error'
		)

class LoggingOptions(_LoggingOptions): #pylint: disable-msg=R0903,W0232
	"""
	Default named tuple that can be used to manually set logging options
	for use with get_logging_options

	:type logfile: String
	:param logfile: The file to log to, or "stdout" or "stderr"' to log to \
	those special file descriptors.  defaults to 'stderr'

	:type: loglevel: String
	:param loglevel: The level to log at. Valid levels are: debug, info, \
	warning, error, and critical. defaults to 'error'
	"""
	pass

def get_logging_options(parser, **kwargs):
	"""
	Provide default options for logging by adding them to a logging class

	:type parser: optparse.OptionParser
	:param parser: This OptionParser object will be used to add options to.
	"""
	default_loglevel = 'error'
	if 'loglevel' in kwargs:
		default_loglevel = kwargs['loglevel']

	parser.add_option(
		"--logfile", dest="logfile", default="stderr",
		type="str", help=" ".join(('The file to log to, or "stdout" or "stderr"',
			'to log to those special file descriptors.',)))
	parser.add_option(
		"--loglevel", dest="loglevel", default=default_loglevel,
		type="str", help=" ".join(('The level to log at.',
			'Valid levels are: debug, info, warning, error, and critical.',)))
	return parser

def configure_logging(options):
	"""Given an options object as returned by OptionParser,
	configure the logging module per the requested config.

	:type options: optparse.OptionParser or k.stdlib.logging.LoggingOptions
	:param options: The parsed command-line options per get_logging_options or LoggingOptions.
	"""
	#pylint: disable-msg=W0212
	if options.loglevel.upper() not in logging._levelNames.values():
		int_loglevels = [l for l in logging._levelNames.values()
				if isinstance(l, int)]
		int_loglevels.sort()
		raise ValueError, 'The loglevel option must be one of {0}'.format([
			logging._levelNames[l] for l in int_loglevels])
	else:
		log_level = logging._levelNames[options.loglevel.upper()]

	if options.logfile.upper() in ('STDOUT', 'STDERR'):
		log_stream = getattr(sys, options.logfile.lower())
		logging.basicConfig(level=log_level, stream=log_stream)
	else:
		logging.basicConfig(level=log_level, filename=options.logfile)
