from unittest import TestCase
from transfire import ApiGatewayTransform
import json
from datetime import datetime, date


class MockChildObject:
    def __init__(self, name):
        self.name = name
        self._hidden_parameter = "cant see me!!!"

    def greeting(self):
        return "Woof Woof " + self.name

class MockTimeObject:
    def __init__(self):
        self.date = date.today()
        self.datetime = datetime.now()
        self.datetime = self.datetime.replace(microsecond=0)

class MockObject:
    def __init__(self):
        self.cats = 3
        self.dog = MockChildObject("Bojo")
        self.time = MockTimeObject()
        self.dogs = [MockChildObject("Baxter"), MockChildObject("Basil"), MockChildObject("Bob")]
        self.dict = {"key": "value"}


class TestApiGatewayTransform(TestCase):
    def setUp(self):
        self.transform = ApiGatewayTransform(MockObject())

    def test_get_paramaters(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/cats'
        })

        self.assertEqual({
            'statusCode': 200,
            'body': '3'
        }, response)

    def test_recursive_get(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/dog/name'
        })

        self.assertEqual({
            'statusCode': 200,
            'body': '"Bojo"'
        }, response)

    def test_get_object_with_hidden(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/dog'
        })

        self.assertEqual({
            'statusCode': 200,
            'body': '{"name": "Bojo"}'
        }, response)

    def test_get_method(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/dog/greeting'
        })

        self.assertEqual({
            'statusCode': 200,
            'body': '"Woof Woof Bojo"'
        }, response)

    def test_no_such_path(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/nosuchresource'
        })

        self.assertEqual({
            'statusCode': 400,
            'body': '"No such resource"'
        }, response)

    def test_dates(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/time'
        })

        self.assertEqual({
            'statusCode': 200,
            'body': '{{"date": "{}", "datetime": "{}"}}'.format(date.today().isoformat(), datetime.now().isoformat(timespec='seconds'))
        }, response)

    def test_arrays(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/dogs'
        })

        self.assertEqual({
            'statusCode': 200,
            'body': '[{"name": "Baxter"}, {"name": "Basil"}, {"name": "Bob"}]'
        }, response)


    def test_no_such_key(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/dogs/3'
        })

        self.assertEqual({
            'statusCode': 404,
            'body': '"index out of bounds"'
        }, response)

    def test_string_key(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/dogs/string'
        })

        self.assertEqual({
            'statusCode': 404,
            'body': '"index must be integer"'
        }, response)

    def test_get_dict_key(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/dict/key'
        })

        self.assertEqual({
            'statusCode': 200,
            'body': '"value"'
        }, response)

    def test_get_dict(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/dict'
        })

        self.assertEqual({
            'statusCode': 200,
            'body': '{"key": "value"}'
        }, response)
