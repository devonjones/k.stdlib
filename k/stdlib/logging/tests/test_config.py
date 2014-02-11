import unittest
import sys
from optparse import OptionParser
from mock import Mock, patch
from k.stdlib.logging.config import *

class LoggingConfigTests(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_parsing_default_logging_options(self):
		parser = OptionParser()
		get_logging_options(parser)
		(options, args) = parser.parse_args([])
		assert options.logfile == 'stderr'
		assert options.loglevel == 'error'

	def test_parsing_logging_options_custom_loglevel(self):
		parser = OptionParser()
		get_logging_options(parser, loglevel='critical')
		(options, args) = parser.parse_args([])
		assert options.logfile == 'stderr'
		assert options.loglevel == 'critical'

	def test_parsing_altered_logging_options(self):
		parser = OptionParser()
		get_logging_options(parser)
		(options, args) = parser.parse_args([
			"--loglevel", "info", "--logfile", "stdout"])
		assert options.logfile == 'stdout'
		assert options.loglevel == 'info'

	def test_default_manual_logging_options(self):
		options = LoggingOptions()
		assert options.logfile == 'stderr'
		assert options.loglevel == 'error'

	def test_altered_manual_logging_options(self):
		options = LoggingOptions('stdout', 'info')
		assert options.logfile == 'stdout'
		assert options.loglevel == 'info'
		options = LoggingOptions(loglevel='warning', logfile='stdout')
		assert options.logfile == 'stdout'
		assert options.loglevel == 'warning'

	def test_configure_logging_defaults(self):
		with patch('logging.basicConfig') as mock_function:
			options = LoggingOptions()
			configure_logging(options)
			mock_function.assert_called_with(level=40, stream=sys.stderr)

	def test_configure_logging_stdout(self):
		with patch('logging.basicConfig') as mock_function:
			options = LoggingOptions(logfile='STDOUT')
			configure_logging(options)
			mock_function.assert_called_with(level=40, stream=sys.stdout)

	def test_configure_logging_warning(self):
		with patch('logging.basicConfig') as mock_function:
			options = LoggingOptions(loglevel='warning')
			configure_logging(options)
			mock_function.assert_called_with(level=30, stream=sys.stderr)

	def test_configure_logging_file(self):
		with patch('logging.basicConfig') as mock_function:
			options = LoggingOptions(logfile='somefile')
			configure_logging(options)
			mock_function.assert_called_with(level=40, filename='somefile')

	def test_false_log_level(self):
		with patch('logging.basicConfig') as mock_function:
			options = LoggingOptions(loglevel='falselevel')
			self.assertRaises(ValueError, configure_logging, options)

