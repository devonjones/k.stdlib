import httplib
import kstdlib.urllib2.urlopen_error_message
import logging
import mock
import socket
import unittest
import urllib2
from StringIO import StringIO
from kstdlib.urllib2 import urlopen

class UrlopenTests(unittest.TestCase):

	def setUp(self):
		self.response_text = """<!doctype html>
<html>
<head><title>404 Not Found</title></head>
<body bgcolor="white">
<center><h1>404 Not Found</h1></center>
<hr><center>nginx/0.7.65</center>
</body>
</html>
"""
		self.url = "http://www.a.com/"
		self.fp = StringIO("<!doctype html>\n<html>\n</html>\n")
		self.headers = httplib.HTTPMessage(StringIO("""Date: Fri, 12 Apr 2013 14:43:25 GMT
Server: Apache/2.2.3 (CentOS)
Last-Modified: Fri, 04 Jan 2013 01:17:22 GMT
Vary: Accept-Encoding
Connection: close
Transfer-Encoding: chunked
Content-Type: text/html; charset=UTF-8
"""))

	def tearDown(self):
		pass

	def test_urlopen_success(self):
		response = urllib2.addinfourl(self.fp, self.headers, self.url)
		response.code = 200
		response.msg = "OK"
		with mock.patch('urllib2.urlopen') as mock_urlopen:
			mock_urlopen.return_value = response
			urlopen(self.url)

	def test_urlopen_httperror(self):
		url = self.url
		error = urllib2.HTTPError(self.url, 404, "Not Found", self.headers, self.fp)
		#print error.msg # Not Found
		with mock.patch('urllib2.urlopen') as mock_urlopen:
			mock_urlopen.side_effect = error
			try:
				urlopen(url)
			except urllib2.HTTPError as err:
				#print err.msg # Not Found (http://www.a.com/)
				assert err.msg.endswith("({0})".format(self.url))
			else:
				self.fail()

	def test_urlopen_httperror_2(self):
		url = urllib2.Request(self.url)
		error = urllib2.HTTPError(self.url, 404, "Not Found", self.headers, self.fp)
		#print error.msg # Not Found
		with mock.patch('urllib2.urlopen') as mock_urlopen:
			mock_urlopen.side_effect = error
			try:
				urlopen(url)
			except urllib2.HTTPError as err:
				#print err.msg # Not Found (http://www.a.com/)
				assert err.msg.endswith("({0})".format(self.url))
			else:
				self.fail()

	def test_urlopen_httperror_3(self):
		url = self.url
		fp = StringIO("<!doctype html>\n<html>\n<title>404 Not Found</title>\n</html>\n")
		error = urllib2.HTTPError(self.url, 404, "Not Found", self.headers, fp)
		#print error.msg # Not Found
		with mock.patch('urllib2.urlopen') as mock_urlopen:
			mock_urlopen.side_effect = error
			try:
				urlopen(url)
			except urllib2.HTTPError as err:
				#print err.msg # Not Found (http://www.a.com/) (Proxy couldn't match the route.)
				assert err.msg.endswith("({0}) (Proxy couldn't match the route.)".format(self.url))
			else:
				self.fail()

	def test_urlopen_httperror_4(self):
		url = self.url
		fp = StringIO('{"status": "404 Not Found"}')
		error = urllib2.HTTPError(self.url, 404, "Not Found", self.headers, fp)
		#print error.msg # Not Found
		with mock.patch('urllib2.urlopen') as mock_urlopen:
			mock_urlopen.side_effect = error
			try:
				urlopen(url)
			except urllib2.HTTPError as err:
				print err.msg # Not Found (http://www.a.com/) (Application couldn't match the route.)
				assert err.msg.endswith("({0}) (Application couldn't match the route.)".format(self.url))
			else:
				self.fail()

	def test_urlopen_urlerror(self):
		url = self.url
		error = urllib2.URLError(socket.gaierror(-2, 'Name or service not known'),)
		#print error.args # (gaierror(-2, 'Name or service not known'),)
		#print error.reason # [Errno -2] Name or service not known
		with mock.patch('urllib2.urlopen') as mock_urlopen:
			mock_urlopen.side_effect = error
			try:
				urlopen(url)
			except urllib2.URLError as err:
				#print err.args # (gaierror(-2, 'Name or service not known'), 'http://www.a.com/')
				#print err.reason # [Errno -2] Name or service not known (http://www.a.com/)
				assert err.args[1] == self.url
				assert err.reason.endswith("({0})".format(self.url))
			else:
				self.fail()

	def test_urlopen_urlerror_2(self):
		url = urllib2.Request(self.url)
		error = urllib2.URLError(socket.gaierror(-2, 'Name or service not known'),)
		#print error.args # (gaierror(-2, 'Name or service not known'),)
		#print error.reason # [Errno -2] Name or service not known
		with mock.patch('urllib2.urlopen') as mock_urlopen:
			mock_urlopen.side_effect = error
			try:
				urlopen(url)
			except urllib2.URLError as err:
				#print err.args # (gaierror(-2, 'Name or service not known'), 'http://www.a.com/')
				#print err.reason # [Errno -2] Name or service not known (http://www.a.com/)
				assert err.args[1] == self.url
				assert err.reason.endswith("({0})".format(self.url))
			else:
				self.fail()

	def test__dump_response(self):
		response = urllib2.addinfourl(self.fp, self.headers, self.url)
		response.code = 200
		response.msg = "OK"
		with mock.patch('logging.debug') as mock_debug:
			kstdlib.urllib2.urlopen_error_message._dump_response(response)

	def test__process_response(self):
		response = mock.Mock()
		response.read.return_value = self.response_text

		assert "__iter__" not in dir(response)
		assert "fileno" not in dir(response)
		assert "fp" not in dir(response)
		assert "next" not in dir(response)
		assert "readline" not in dir(response)
		assert "readlines" not in dir(response)

		kstdlib.urllib2.urlopen_error_message._process_response(response)

		assert "__iter__" in dir(response)
		assert "fileno" in dir(response)
		assert "fp" in dir(response)
		assert "next" in dir(response)
		assert "readline" in dir(response)
		assert "readlines" in dir(response)

		assert response.fileno() is None

		expected = [
			'<!doctype html>\n',
			'<html>\n',
			'<head><title>404 Not Found</title></head>\n',
			'<body bgcolor="white">\n',
			'<center><h1>404 Not Found</h1></center>\n',
			'<hr><center>nginx/0.7.65</center>\n',
			'</body>\n',
			'</html>\n',
		]
		actual = response.readlines()
		assert expected == actual

		assert response.fileno() is None

	def test__process_response_2(self):
		response = mock.Mock()
		response.read.return_value = self.response_text

		assert "__iter__" not in dir(response)
		assert "fileno" not in dir(response)
		assert "fp" not in dir(response)
		assert "next" not in dir(response)
		assert "readline" not in dir(response)
		assert "readlines" not in dir(response)

		with mock.patch('kstdlib.urllib2.urlopen_error_message.StringIO') as mock_stringio:
			fp = mock.Mock(spec=['read', 'readline', 'fileno'])
			fp.read = lambda: None
			fp.readline = lambda: None
			fp.fileno = lambda: 0
			mock_stringio.return_value = fp
			kstdlib.urllib2.urlopen_error_message._process_response(response)

		assert "__iter__" not in dir(response)
		assert "fileno" in dir(response)
		assert "fp" in dir(response)
		assert "next" not in dir(response)
		assert "readline" in dir(response)
		assert "readlines" in dir(response)

		try:
			response.readlines()
		except NotImplementedError:
			pass
		else:
			self.fail()

		assert response.fileno() == 0

