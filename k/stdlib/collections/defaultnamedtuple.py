"""
Adapted from:
  http://blog.thomnichols.org/2010/12/lightweight-data-types-in-python

This solves the problem of namedtuples not having default values.
"""

import copy
import collections
import sys
from types import MethodType

def defaultnamedtuple(_cls_name, _field_names, **defaults):
	"""
	Similar to `collections.namedtuple` except default properties may be
	specified. For example:

	>>> Person = defaultnamedtuple('Person', 'name', 'address', age=10)
	>>> bob = Person(name='bob', address='123 someplace')

	A mix of positional and keyword args is supported.
	"""

	# Since namedtuple supports space separated strings, or lists of
	# strings, so do we.
	if isinstance(_field_names, basestring):
		_field_names = _field_names.replace(',', ' ').split()

	for key in defaults:
		if key not in _field_names:
			raise ValueError("Encountered default not listed in"
					" field_names: {0}".format(key))

	# We're starting off with a 'stock' namedtuple and modifying it slightly.
	cls = collections.namedtuple(_cls_name, _field_names)

	# Here we are intercepting the normal __new__ call in order to assign
	# defaults before all properties are passed to the namedtuple
	# constructor.
	# If extra properties are given, or any are missing, the old_new will
	# make that determination and throw the proper exception.

	old_new = cls.__new__
	def _new(cls, _ignore, *args, **kwargs):
		"""Overriding namedtuple's __new__ method."""
		# Construct a dict to pass into the __new__ method
		# of namedtuple.
		data = copy.deepcopy(defaults)
		for index, value in enumerate(args):
			data[_field_names[index]] = value

		data.update(kwargs)
		return old_new(cls, **(data))

	cls.__new__ = MethodType(_new, cls)

	def _eq(self, other):
		"""Overridding namedtuple's __eq__ method.

		Equality should depend on type as well as values.
		"""
		return tuple.__eq__(self, other) and self.__class__ == other.__class__

	cls.__eq__ = _eq

	def _ne(self, other):
		"""Overridding namedtuple's __ne__ method."""
		return not self.__eq__(other)

	cls.__ne__ = _ne

	# Since this is wrapped, the proper module name is up another level.
	if hasattr(sys, '_getframe'):
		#pylint: disable-msg=W0212
		cls.__module__ = sys._getframe(1).f_globals.get('__name__', '__main__')

	return cls

