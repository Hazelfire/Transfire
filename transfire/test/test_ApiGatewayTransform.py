from transfire import ApiGatewayTransform
from datetime import datetime, date
from typing import List


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
    dogs: List[MockChildObject] = []

    def __init__(self):
        self.cats = 3
        self.dog = MockChildObject("Bojo")
        self.time = MockTimeObject()
        self.dogs = [MockChildObject("Baxter"), MockChildObject("Basil"), MockChildObject("Bob")]
        self.integers = [1, 2, 3]
        self.dict = {"key": "value"}
        self.write_prop_value = 3

    def method(self):
        return "return"

    def null(self):
        pass

    @property
    def readproperty(self):
        return self.cats + 1
    
    @property
    def readwriteproperty(self):
        return self.write_prop_value + 1

    @readwriteproperty.setter
    def readwriteproperty(self, value):
        self.write_prop_value = value - 1



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
            'statusCode': 404,
            'body': '"No such resource at nosuchresource"'
        } == response

    def test_no_such_path_multiple(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/nosource1/nosource2'
        })

        assert response == {
            'statusCode': 404,
            'body': '"No such resource at nosource1"'
        }

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
            'body': '"No such resource at 3"'
        } == response

    def test_string_key(self):
        response = self.transform.call({
            'httpMethod': 'GET',
            'path': '/dogs/string'
        })

        assert {
            'statusCode': 404,
            'body': '"No such resource at string"'
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
    
    def test_put_array(self):
        response = self.transform.call({
            'httpMethod': 'PUT',
            'path': '/integers/2',
            'body': '2'
        })

        assert response == {
            'statusCode': 204
        }

        assert self.mock.integers == [1, 2, 2]

    def test_put_method_invalid(self):
        response = self.transform.call({
            'httpMethod': 'PUT',
            'path': '/method',
            'body': '"value"'
        })

        assert response == {
            'statusCode': 400,
            'body': '"No such method PUT for resource /method"'
        }

        assert callable(self.mock.method)

    def test_put_property_invalid(self):
        response = self.transform.call({
            'httpMethod': 'PUT',
            'path': '/readproperty',
            'body': '5'
        })

        assert response == {
            'statusCode': 400,
            'body': '"No such method PUT for resource /readproperty"'
        }

    def test_calls_setter_on_put(self):
        response = self.transform.call({
            'httpMethod': 'PUT',
            'path': '/readwriteproperty',
            'body': '4'
        })

        assert response == {
            'statusCode': 204
        }

        assert self.mock.write_prop_value == 3

    def test_invalid_type(self):
        response = self.transform.call({
            'httpMethod': 'PUT',
            'path': '/cats',
            'body': '"2"'
        })

        assert response == {
            'statusCode': 400,
            'body': '"Cannot assign \\"2\\" of type str to /cats of type int"'
        }

        assert self.mock.cats == 3  # Default


class TestPostApiGatewayTransform:
    def setup_method(self):
        self.mock = MockObject()
        self.transform = ApiGatewayTransform(self.mock)

    def test_post_object(self):
        response = self.transform.call({
            'httpMethod': 'POST',
            'path': '/dogs',
            'body': '{"name": "Barney"}'
        })

        assert response == {
            'statusCode': 204
        }

        assert len(self.mock.dogs) == 4
        assert self.mock.dogs[3].name == "Barney"

    def test_post_object_missing_param(self):
        response = self.transform.call({
            'httpMethod': 'POST',
            'path': '/dogs',
            'body': '{}'
        })

        assert response == {
            'statusCode': 400,
            'body': '"Could not create object with given parameters"'
        }


    def test_post_object_extra_params(self):
        response = self.transform.call({
            'httpMethod': 'POST',
            'path': '/dogs',
            'body': '{"name": "Barney", "feet": 4}'
        })


        assert response == {
            'statusCode': 400,
            'body': '"Could not create object with given parameters"'
        }

    def test_post_object_no_annotations(self):
        response = self.transform.call({
            'httpMethod': 'POST',
            'path': '/integers',
            'body': '4'
        })

        assert response == {
            'statusCode': 400,
            'body': '"No such method POST for resource /integers"'
        }
