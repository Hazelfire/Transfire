from unittest import TestCase
from transfire import ApiGatewayTransform
import json

class MockObject:
    def __init__(self):
        self.cats = 3

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
