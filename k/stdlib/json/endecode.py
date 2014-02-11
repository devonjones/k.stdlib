import warnings
warnings.filterwarnings('ignore', 'Module _mysql was already imported from.*', UserWarning, 'simplejson')
import copy
import json as _json
from collections import OrderedDict
from decimal import Decimal
from datetime import datetime
from datetime import date

# COMMON

class JSONObject():

	def __init__(self, json_class, values=None):
		self.__dict__ = {}

		assert json_class.startswith('__')
		assert json_class.endswith('__')
		assert len(json_class) > 4
		self.json_class = json_class[2:-2]

		if values:
			self.__dict__.update(values)

	def __getitem__(self, key):
		return self.__dict__[key]

	def __setitem__(self, key, value):
		self.__dict__[key] = value

	def __delitem__(self, key):
		del self.__dict__[key]

	def __iter__(self):
		return self.__dict__.__iter__()

	def __len__(self):
		return self.__dict__.__len__()

	def __contains__(self, key):
		return self.__dict__.__contains__(key)

	def __repr__(self):
		return repr(self.__dict__)

	def update(self, values):
		self.__dict__.update(values)

	def has_key(self, key):
		return self.__dict__.has_key(key)

	def get(self, key, default=None):
		return self.__dict__.get(key, default)

def json_object_wrap(obj, name):
	if obj == None:
		return None

	if type(obj) in (list, tuple):
		retlist = []
		for element in obj:
			retlist.append(json_object_wrap(element, name))

		return retlist
	else:
		json_object = JSONObject('__{0}__'.format(name))
		json_object.update(obj)
		return json_object

# ENCODERS

def datetime_encoder(obj):
	return {'__datetime__' : obj.isoformat()}

def date_encoder(obj):
	return {'__date__' : obj.isoformat()}

def decimal_encoder(obj):
	values = {}
	payload = {'__decimal__' : values}
	(sign, coefficient, exponent) = obj.as_tuple()

	tmp = ''
	if sign == 1:
		tmp += '-'

	tmp += ''.join([str(digit) for digit in coefficient])
	tmp += 'e'
	tmp += str(exponent)

	values['__string_repr__'] = tmp
	values['__float_repr__'] = float(obj)
	return payload

def json_object_encoder(obj):
	key = '__{0}__'.format(obj.json_class)
	values = copy.deepcopy(obj.__dict__)
	del values['json_class']
	return {key: values}

class JSONEncoder(_json.JSONEncoder):

	def __init__(self, encoders=None, **kwargs):
		# We are using an OrderedDict because the order in which
		# classes are checked matters. For example, datetime must
		# be checked before date, as isinstance(datetime.datetime(),
		# datetime.date) evaluates to True.
		self.encoders = encoders
		if not self.encoders:
			self.encoders = OrderedDict()

		# NOTE: If using simplejson, instead of json, the following
		#       line is required:
		#kwargs['use_decimal'] = False

		self.encoders[datetime] = datetime_encoder
		self.encoders[date] = date_encoder
		self.encoders[Decimal] = decimal_encoder
		self.encoders[JSONObject] = json_object_encoder
		_json.JSONEncoder.__init__(self, **kwargs)

	def default(self, obj):
		for cls in self.encoders:
			if isinstance(obj, cls):
				return self.encoders[cls](obj)
		return _json.JSONEncoder.default(self, obj)

def dumps(obj, cls=JSONEncoder, **kwargs):
	return _json.dumps(obj, cls=cls, **kwargs) + "\n"

def dump(obj, fp, cls=JSONEncoder, **kwargs):
	return _json.dump(obj, fp, cls=cls, **kwargs)

# DECODERS

def _legacy_datetime_decoder(obj):
	return datetime(obj['year'], obj['month'], obj['day'], obj['hour'],
			obj['minute'], obj['second'], obj['microsecond'],
			obj['tzinfo'])

def datetime_decoder(obj):
	if not isinstance(obj, basestring):
		return _legacy_datetime_decoder(obj)

	if '.' in obj:
		return datetime.strptime(obj, '%Y-%m-%dT%H:%M:%S.%f')
	else:
		return datetime.strptime(obj, '%Y-%m-%dT%H:%M:%S')

def _legacy_date_decoder(obj):
	return date(obj['year'], obj['month'], obj['day'])

def date_decoder(obj):
	if not isinstance(obj, basestring):
		return _legacy_date_decoder(obj)

	return datetime.strptime(obj, '%Y-%m-%d').date()

def _legacy_decimal_decoder(obj):
	if 'tuple' in obj:
		return Decimal(obj['tuple'])

	sign = obj['sign']
	coefficient = obj['coefficient']
	exponent = obj['exponent']
	digits = []
	if type(coefficient) == list:
		digits = coefficient
	else:
		while coefficient > 0:
			digits.insert(0, coefficient % 10)
			coefficient /= 10

	return Decimal((sign, digits, exponent))

def decimal_decoder(obj):
	if '__string_repr__' not in obj:
		return _legacy_decimal_decoder(obj)

	return Decimal(obj['__string_repr__'])

def json_object_decoder(name, obj):
	json_obj = JSONObject(name)
	json_obj.update(obj)
	return json_obj

class JSONDecoder(object):

	def __init__(self):
		self.decoders = {}
		self.decoders['__datetime__'] = datetime_decoder
		self.decoders['__date__'] = date_decoder
		self.decoders['__decimal__'] = decimal_decoder

	def add_decoder(self, name, decoder):
		self.decoders[name] = decoder

	def object_decoder(self, d):
		for name in self.decoders:
			if name in d:
				obj = d[name]
				decoder = self.decoders[name]
				return decoder(obj)

		for name in d:
			if name.startswith('__') and name.endswith('__') and not name.endswith('repr__'):
				return json_object_decoder(name, d[name])

		return d

	def loads(self, obj, **kwargs):
		return _json.loads(obj, object_hook=self.object_decoder, **kwargs)

	def load(self, obj, **kwargs):
		return _json.load(obj, object_hook=self.object_decoder, **kwargs)

def loads(obj, **kwargs):
	return JSONDecoder().loads(obj, **kwargs)

def load(obj, **kwargs):
	return JSONDecoder().load(obj, **kwargs)

