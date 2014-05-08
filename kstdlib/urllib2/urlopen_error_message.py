#!/usr/bin/env python
"""Improvements to urllib2's urlopen method."""
import types
import urllib2 as _urllib2
import logging
from StringIO import StringIO

def _process_response(response):
	"""
	By default addbase's fp instance variable is of type socket._fileobject.
	You can't rewind that object. This method modified an addinfourl
	response object, so that you can read the response body multiple times.
	Adapted from addbase#__init__, in /usr/lib/python2.6/urllib.py.
	"""
	response.fp = StringIO(response.read())
	response.read = response.fp.read
	response.readline = response.fp.readline

	if hasattr(response.fp, "readlines"):
		response.readlines = response.fp.readlines
	else:
		def _not_implemented(*args, **kwargs):
			"""If the readlines method does not exist on
			StringIO, there's nothing to assign to the
			response, so we will raise and exception, instead.
			"""
			raise NotImplementedError

		response.readlines = _not_implemented

	if hasattr(response.fp, "fileno"):
		response.fileno = response.fp.fileno
	else:
		response.fileno = lambda: None

	if hasattr(response.fp, "__iter__"):
		response.__iter__ = response.fp.__iter__
		if hasattr(response.fp, "next"):
			response.next = response.fp.next

	# TODO: Add a method to response or response.fp, so that I don't have to
	#       explicitly refer to StringIO's seek method.

def _dump_response(response):
	"""
	Sample output:

		code = 200
		msg = OK
		url = https://my.staging.knewton.com/remote/api/authentication/
		typeheader = application/json
		maintype = application
		subtype = json
		encoding = None
		headers =
			Server: nginx/0.7.65
			Date: Mon, 20 Jun 2011 21:45:36 GMT
			Content-Type: application/json
			Connection: close
			Allow: GET, HEAD, POST
			Content-Length: 157
			Vary: Accept-Encoding
			P3P: policyref="/w3c/p3p.xml", CP="CAO DSP COR CURa ADMa DEVa OUR IND PHY ONL UNI COM NAV INT DEM PRE"
			Set-Cookie: uid=Cv6O/03/v4AtH3aCAwM3Ag==; expires=Fri, 19-Jun-15 21:45:36 GMT; domain=.staging.knewton.com; path=/
		date = Mon, 20 Jun 2011 21:45:36 GMT
		{
		  "auth_token": "0e5e3cfbcec8531dbacd6719bb4d3b2da55b2212", 
		  "user_id": 4234, 
		  "email": "jon@knewton.com", 
		  "last_authentication_type": "knewton"
		}
	"""
	logging.debug("code = {0}".format(response.code))
	logging.debug("msg = {0}".format(response.msg))
	logging.debug("url = {0}".format(response.url))
	logging.debug("typeheader = {0}".format(response.headers.typeheader))
	logging.debug("maintype = {0}".format(response.headers.maintype))
	logging.debug("subtype = {0}".format(response.headers.subtype))
	logging.debug("encoding = {0}".format(response.headers.encodingheader))
	logging.debug("headers =")
	for header in response.headers.headers:
		logging.debug("\t{0}".format(header.strip()))
	logging.debug("date = {0}".format(response.headers['date']))

	_process_response(response)

	#logging.debug(response.read())
	#response.fp.seek(0)
	logging.debug(response.fp.getvalue())

def urlopen(*args, **kwargs):
	"""
	Here are some examples used in identifying features of different categories of 404 responses:

	Proxy 404 (/fake):

		<html>
		<head><title>404 Not Found</title></head>
		<body bgcolor="white">
		<center><h1>404 Not Found</h1></center>
		<hr><center>nginx/0.7.65</center>
		</body>
		</html>

	CherryPy 404 (/krs/fake):
		{
		  "status": "404 Not Found",
		  "message": "The path '/krs/fake' was not found.",
		  "traceback": "",
		  "version": "3.1.2"
		}

	Resource 404 (/krs/assessments/quizzes/16289):
		{
		  "status": "404 Not Found",
		  "unfound": [
		    {
		      "type": "quiz",
		      "id": "16289"
		    }
		  ],
		  "message": "Resource not found.",
		  "version": "3.1.2"
		}
	"""
	try:
		handle = _urllib2.urlopen(*args, **kwargs)
	except _urllib2.HTTPError, err:
		_process_response(err)

		#body = err.read()
		#err.fp.seek(0)
		body = err.fp.getvalue()

		if type(args[0]) in types.StringTypes:
			url = args[0]
		else:
			url = args[0].get_full_url()

		if '<title>404 Not Found</title>' in body:
			msgfmt = "%s (%s) (Proxy couldn't match the route.)"
		elif '"status": "404 Not Found"' in body and '"unfound":' not in body:
			msgfmt = "%s (%s) (Application couldn't match the route.)"
		else:
			msgfmt = "%s (%s)"

		err.msg = msgfmt % (err.msg, url)
		raise
	except _urllib2.URLError, err:
		if type(args[0]) in types.StringTypes:
			err.args = err.args + (args[0],)
			err.reason = "%s (%s)" % (err.reason, args[0])
		else:
			err.args = err.args + (args[0].get_full_url(),)
			err.reason = "%s (%s)" % (err.reason, args[0].get_full_url())
		raise

	return handle

