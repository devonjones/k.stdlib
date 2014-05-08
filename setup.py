#!/usr/bin/env python
import os.path
import re
from setuptools import Command, find_packages, setup

class PyTest(Command):
	user_options = []
	def initialize_options(self):
		pass
	def finalize_options(self):
		pass
	def run(self):
		import sys, subprocess
		errno = subprocess.call([sys.executable, "runtests.py"])
		raise SystemExit(errno)

def parse_requirements(file_name):
	"""Taken from http://cburgmer.posterous.com/pip-requirementstxt-and-setuppy"""
	requirements = []
	for line in open(os.path.join(os.path.dirname(__file__), "config", file_name), "r"):
		line = line.strip()
		# comments and blank lines
		if re.match(r"(^#)|(^$)", line):
			continue
		if line.startswith("git+"):
			parts = line.split('#')
			package = parts.pop().split('=').pop()
			parts = '#'.join(parts).split('@')
			if len(parts) == 3:
				version = parts.pop()
				if version.find('v') > -1:
					version = version.replace('v', '')
				line = "%s==%s" %(package, version)
			else:
				line = package
		requirements.append(line)
	return requirements

setup(
	name = "kstdlib",
	version = "0.2.0",
	url = "https://wiki.knewton.net/index.php/Tech",
	author = "Devon Jones",
	author_email = "devon.jones@gmail.com",
	license = "Proprietary",
	packages = find_packages(),
	cmdclass = {"test": PyTest},
	package_data = {"config": ["requirements.txt"]},
	install_requires = parse_requirements("requirements.txt"),
	tests_require = parse_requirements("requirements.txt"),
	description = "Knewton improvements to the python std library.",
	long_description = "\n" + open("README.md").read(),
)
