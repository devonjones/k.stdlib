import unittest
from kstdlib.collections import defaultnamedtuple

class DefaultnamedtupleTests(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_unknown_property(self):
		error_text = "Encountered default not listed in field_names: age"
		with self.assertRaisesRegexp(ValueError, error_text):
			defaultnamedtuple('Person', [], age=10)

	def test_all_required(self):
		Person = defaultnamedtuple('Person', ['name'])
		bob = Person('Bob')
		assert bob.name == 'Bob'

	def test_some_optional_all_defaults(self):
		Person = defaultnamedtuple('Person', ['name', 'age', 'height'], age=10, height=80)
		bob = Person('Bob')
		assert bob.name == 'Bob'
		assert bob.age == 10
		assert bob.height == 80

	def test_some_optional(self):
		Person = defaultnamedtuple('Person', ['name', 'age', 'height'], age=10, height=80)
		bob = Person('Bob', 35, 60)
		assert bob.name == 'Bob'
		assert bob.age == 35
		assert bob.height == 60

	def test_some_optional_2(self):
		Person = defaultnamedtuple('Person', ['name', 'age', 'height'], age=10, height=80)
		bob = Person('Bob', 35)
		assert bob.name == 'Bob'
		assert bob.age == 35
		assert bob.height == 80

	def test_some_optional_3(self):
		Person = defaultnamedtuple('Person', ['name', 'age', 'height'], age=10, height=80)
		bob = Person('Bob', height=60)
		assert bob.name == 'Bob'
		assert bob.age == 10
		assert bob.height == 60

	def test_some_optional_fail(self):
		Person = defaultnamedtuple('Person', ['name', 'age', 'height'], height=80)
		error_text = "__new__\(\) takes exactly 4 arguments \(3 given\)"
		with self.assertRaisesRegexp(TypeError, error_text):
			bob = Person('Bob', height=60)

	def test_all_optional_all_defaults(self):
		Person = defaultnamedtuple('Person', ['name', 'age', 'height'], name=None, age=10, height=80)
		bob = Person()
		assert bob.name is None
		assert bob.age == 10
		assert bob.height == 80

	def test_all_optional(self):
		Person = defaultnamedtuple('Person', ['name', 'age', 'height'], name=None, age=10, height=80)
		bob = Person('Bob', 35, 60)
		assert bob.name == 'Bob'
		assert bob.age == 35
		assert bob.height == 60

	def test_all_optional_2(self):
		Person = defaultnamedtuple('Person', ['name', 'age', 'height'], name=None, age=10, height=80)
		bob = Person('Bob', 35)
		assert bob.name == 'Bob'
		assert bob.age == 35
		assert bob.height == 80

	def test_all_optional_3(self):
		Person = defaultnamedtuple('Person', ['name', 'age', 'height'], name=None, age=10, height=80)
		bob = Person(height=60)
		assert bob.name == None
		assert bob.age == 10
		assert bob.height == 60

	def test_eq(self):
		Person = defaultnamedtuple('Person', 'name age', age=10)
		bob1 = Person('Bob')
		bob2 = Person('Bob')
		assert bob1 == bob2

	def test_ne(self):
		Person = defaultnamedtuple('Person', 'name age', age=10)
		bob = Person('Bob')
		mary = Person('Mary')
		assert bob != mary

	def test_ne_2(self):
		Person = defaultnamedtuple('Person', 'name age', age=10)
		bob1 = Person('Bob')
		Person2 = defaultnamedtuple('Person2', 'name age', age=10)
		bob2 = Person2('Bob')
		assert bob1 != bob2

