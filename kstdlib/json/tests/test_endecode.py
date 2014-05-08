import datetime
import decimal
import kstdlib.json as json
import unittest
from StringIO import StringIO

class JSONEncoderTests(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	# COMMON

	def test_jsonobject_fail1(self):
		self.assertRaises(AssertionError, json.JSONObject, '')

	def test_jsonobject_fail2(self):
		self.assertRaises(AssertionError, json.JSONObject, '____')

	def test_jsonobject(self):
		values = {
			'first_name': 'Isaak',
			'last_name': 'Knewton',
			'email': None,
		}
		obj = json.JSONObject('__user__', values)
		values['email'] = 'isaak@knewton.com'
		obj.update(values)
		assert 'first_name' in obj
		assert obj.get('first_name') == 'Isaak'
		assert not obj.has_key('missing')
		assert len(obj) == len(values) + 1
		assert len(repr(obj)) > 1
		for key in obj:
			if key != 'json_class':
				obj[key] = values[key].upper()
				assert obj[key] == values[key].upper()

		del obj['first_name']

	def test_json_object_wrap_null(self):
		assert json.json_object_wrap(None, 'foo') is None

	def test_json_object_wrap_list(self):
		expected = [
			{'json_class': 'user', 'first_name': 'Isaak', 'last_name': 'Knewton', 'email': None},
			{'json_class': 'user', 'first_name': 'Isaak2', 'last_name': 'Knewton2', 'email': None}
		]
		data = [
			{'first_name': 'Isaak', 'last_name': 'Knewton', 'email': None},
			{'first_name': 'Isaak2', 'last_name': 'Knewton2', 'email': None},
		]
		actual = json.json_object_wrap(data, 'user')
		assert expected == [element.__dict__ for element in actual]

	def test_json_object_wrap_jo(self):
		expected = {'json_class': 'user', 'first_name': 'Isaak',
				'last_name': 'Knewton', 'email': None}
		data = {'first_name': 'Isaak',
				'last_name': 'Knewton',
				'email': None}
		actual = json.json_object_wrap(data, 'user')
		assert expected == actual.__dict__

	# ENCODERS

	def test_dump(self):
		buffer = StringIO()
		json.dump('foobar', buffer)
		buffer.seek(0)
		expected = '"foobar"'
		actual = buffer.read()
		assert expected == actual

	def test_string_dumps(self):
		assert '"foobar"\n' == json.dumps("foobar")

	def test_datetime_dumps(self):
		expected = ('{"__datetime__": "2000-01-01T00:00:00"}\n')
		actual = json.dumps(datetime.datetime(2000, 1, 1))
		assert expected == actual

	def test_date_dumps(self):
		expected = ('{"__date__": "2000-01-01"}\n')
		actual = json.dumps(datetime.date(2000, 1, 1))
		assert expected == actual

	def test_decimal_dumps(self):
		expected = ('{"__decimal__": {"__string_repr__": "10001e-1", '
				'"__float_repr__": 1000.1}}\n')
		actual = json.dumps(decimal.Decimal('1000.1'))
		assert expected == actual

	def test_decimal_dumps_negative(self):
		expected = ('{"__decimal__": {"__string_repr__": "-10001e-1", '
				'"__float_repr__": -1000.1}}\n')
		actual = json.dumps(decimal.Decimal('-1000.1'))
		assert expected == actual

	def test_jsonobject_dumps(self):
		expected = '{"__user__": {"first_name": "Isaak", "last_name": "Knewton", "email": null}}\n'
		json_object = json.JSONObject('__user__', {
				'first_name': 'Isaak',
				'last_name': 'Knewton',
				'email': None})
		actual = json.dumps(json_object)
		assert expected == actual

	def test_unknown_dumps(self):
		error_text = '<object object at .*> is not JSON serializable'
		with self.assertRaisesRegexp(TypeError, error_text):
			json.dumps(object())

	# DECODERS

	def test_jsondecoder(self):
		def foo_decoder(obj):
			return obj

		decoder = json.JSONDecoder()
		assert len(decoder.decoders) == 3
		decoder.add_decoder('__foo__', foo_decoder)
		assert len(decoder.decoders) == 4

	def test_load(self):
		expected = 'foobar'
		data = StringIO('"foobar"\n')
		actual = json.load(data)
		assert expected == actual

	def test_string_loads(self):
		assert json.loads('"foobar"\n') == 'foobar'

	def test_datetime_loads_legacy(self):
		expected = datetime.datetime(2000, 1, 31)
		data = ('{"__datetime__": {"hour": 0, "month": 1, "second": 0, '
				'"microsecond": 0, "__string_repr__": "2000-01-31T00:00:00", '
				'"year": 2000, "tzinfo": null, "day": 31, "minute": 0}}\n')
		actual = json.loads(data)
		assert expected == actual

	def test_datetime_loads(self):
		expected = datetime.datetime(2000, 1, 31, 12, 34, 56)
		data = ('{"__datetime__": "2000-01-31T12:34:56"}\n')
		actual = json.loads(data)
		assert expected == actual

	def test_datetime_loads_with_microsecond(self):
		expected = datetime.datetime(2000, 1, 31, 12, 34, 56, 999999)
		data = ('{"__datetime__": "2000-01-31T12:34:56.999999"}\n')
		actual = json.loads(data)
		assert expected == actual

	def test_date_loads_legacy(self):
		expected = datetime.date(2000, 1, 31)
		data = ('{"__date__": {"month": 1, "__string_repr__": '
				'"2000-01-31", "day": 31, "year": 2000}}\n')
		actual = json.loads(data)
		assert expected == actual

	def test_date_loads(self):
		expected = datetime.date(2000, 1, 31)
		data = ('{"__date__": "2000-01-31"}\n')
		actual = json.loads(data)
		assert expected == actual

	def test_decimal_loads_tuple_legacy(self):
		expected = decimal.Decimal('1000.1')
		data = ('{"__decimal__": {"tuple": [0, [1, 0, 0, 0, 1], -1]}}')
		actual = json.loads(data)
		assert expected == actual

	def test_decimal_loads_digits_legacy(self):
		expected = decimal.Decimal('1000.1')
		data = ('{"__decimal__": {"coefficient": [1, 0, 0, 0, 1], '
				'"exponent": -1, "__float_repr__": 1000.1, "sign": 0}}\n')
		actual = json.loads(data)
		assert expected == actual

	def test_decimal_loads_coefficient_legacy(self):
		expected = decimal.Decimal('1000.1')
		data = ('{"__decimal__": {"coefficient": 10001, '
				'"exponent": -1, "__float_repr__": 1000.1, "sign": 0}}\n')
		actual = json.loads(data)
		assert expected == actual

	def test_decimal_loads(self):
		expected = decimal.Decimal('1000.1')
		data = '{"__decimal__": {"__string_repr__": "10001e-1"}}'
		actual = json.loads(data)
		assert expected == actual

	def test_decimal_loads_negative(self):
		expected = decimal.Decimal('-1000.1')
		data = '{"__decimal__": {"__string_repr__": "-10001e-1"}}'
		actual = json.loads(data)
		assert expected == actual

	def test_jsonobject_loads(self):
		expected = json.JSONObject('__user__', {
				'first_name': 'Isaak',
				'last_name': 'Knewton',
				'email': None})
		data = '{"__user__": {"first_name": "Isaak", "last_name": "Knewton", "email": null}}\n'
		actual = json.loads(data)
		assert expected.__dict__ == actual.__dict__

