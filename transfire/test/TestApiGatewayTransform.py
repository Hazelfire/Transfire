from unittest import TestCase
from transfire import ApiGatewayTransform
import json
from datetime import datetime, date


class MockChildObject:
    def __init__(self, name):
        self.name = name

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

    def test_get_object(self):
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
