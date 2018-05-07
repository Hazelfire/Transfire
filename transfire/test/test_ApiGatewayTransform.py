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

    def method(self):
        return "return"

    def null(self):
        pass


class TestGetApiGatewayTransform:
    def setup_method(self):
        self.transform = ApiGatewayTransform(MockObject())

    def test_get_paramaters(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/cats'
        })

        expected = {
            'statusCode': 200,
            'body': '3'
        }

        assert expected == response

    def test_recursive_get(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/dog/name'
        })

        assert {
            'statusCode': 200,
            'body': '"Bojo"'
        } == response

    def test_get_object_with_hidden(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/dog'
        })

        assert {
            'statusCode': 200,
            'body': '{"name": "Bojo"}'
        } == response

    def test_get_method(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/dog/greeting'
        })

        assert {
            'statusCode': 200,
            'body': '"Woof Woof Bojo"'
        } == response

    def test_no_such_path(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/nosuchresource'
        })

        assert {
            'statusCode': 400,
            'body': '"No such resource at nosuchresource"'
        } == response

    def test_dates(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/time'
        })

        assert {
            'statusCode': 200,
            'body': '{{"date": "{}", "datetime": "{}"}}'.format(date.today().isoformat(), datetime.now().isoformat(timespec='seconds'))
        } == response

    def test_arrays(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/dogs'
        })

        assert {
            'statusCode': 200,
            'body': '[{"name": "Baxter"}, {"name": "Basil"}, {"name": "Bob"}]'
        } == response


    def test_no_such_key(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/dogs/3'
        })

        assert {
            'statusCode': 404,
            'body': '"index out of bounds"'
        } == response

    def test_string_key(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/dogs/string'
        })

        assert {
            'statusCode': 404,
            'body': '"index must be integer"'
        } == response

    def test_get_dict_key(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/dict/key'
        })

        assert {
            'statusCode': 200,
            'body': '"value"'
        } == response

    def test_get_dict(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/dict'
        })

        assert {
            'statusCode': 200,
            'body': '{"key": "value"}'
        } == response

    def test_method(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/method'
        })

        assert response == {
            'statusCode': 200,
            'body': '"return"'
        }

    def test_no_return(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/null'
        })

        assert response == {
            'statusCode': 204
        }


class TestApiGatewayTransform:
    def setup_method(self):
        self.mock = MockObject()
        self.transform = ApiGatewayTransform(self.mock)

    def test_invalid_method(self):
        response = self.transform.call({
            'httpMethod': 'BREW',
            'path': '/cats'
        })

        assert response == {
            'statusCode': 400,
            'body': '"No such method BREW for resource /cats"'
        }


class TestPutApiGatewayTransform:
    def setup_method(self):
        self.mock = MockObject()
        self.transform = ApiGatewayTransform(self.mock)

    def test_put_value(self):
        response = self.transform.call({
            'httpMethod': 'PUT',
            'path': '/cats',
            'body': '2'
        })

        assert response == {
            'statusCode': 204
        }

        assert self.mock.cats == 2
        
