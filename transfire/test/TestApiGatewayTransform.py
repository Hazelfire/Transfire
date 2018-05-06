from unittest import TestCase
from transfire import ApiGatewayTransform
import json


class MockChildObject:
    def __init__(self, name):
        self.name = name


class MockObject:
    def __init__(self):
        self.cats = 3
        self.dog = MockChildObject("Bojo")


class TestApiGatewayTransform(TestCase):
    def setUp(self):
        self.transform = ApiGatewayTransform(MockObject())

    def test_get_paramaters(self):
        response = self.transform.call({
            'method': 'GET',
            'path': '/cats'
        })

        self.assertEqual({
            'statusCode': 200,
            'body': '3'
        }, response)

    def test_recursive_get(self):
        response = self.transform.call({
            'method': 'GET',
            'path': '/dog/name'
        })

        self.assertEqual({
            'statusCode': 200,
            'body': '"Bojo"'
        }, response)

    def test_get_object(self):
        response = self.transform.call({
            'method': 'GET',
            'path': '/dog'
        })

        self.assertEqual({
            'statusCode': 200,
            'body': '{"name": "Bojo"}'
        }, response)

    def test_get_root(self):
        response = self.transform.call({
            'method': 'GET',
            'path': '/'
        })

        self.assertEqual({
            'statusCode': 200,
            'body': '{"cats": 3, "dog": {"name": "Bojo"}}'
        }, response)
