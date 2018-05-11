import json
from datetime import date, datetime
from typing import get_type_hints, List
from inspect import signature


class NoSuchMethodError(Exception):
    def __init__(self, method, path):
        super(NoSuchMethodError, self).__init__(
            "No such method {} for resource {}".format(method, path)
        )


class NoSuchResourceError(Exception):
    def __init__(self, path):
        super(NoSuchResourceError, self).__init__(
            "No such resource at {}".format(path)
        )


class CannotSetResourceError(Exception):
    def __init__(self, path):
        super(CannotSetResourceError, self).__init__(
            '"{}" cannot be set'.format(path)
        )


class IncorrectConstructorParametersError(Exception):
    def __init__(self):
        super(IncorrectConstructorParametersError, self).__init__(
            "Could not create object with given parameters"
        )


class InvalidTypeError(Exception):
    def __init__(self, value, resource, resource_type):
        super(InvalidTypeError, self).__init__(
               'Cannot assign {} of type {} to {} of type {}'.format(json.dumps(value), type(value).__name__, resource, resource_type.__name__)
        )


class ApiGatewayTransform:
    def __init__(self, transform_object):
        self.transform_object = transform_object

    def call(self, event):
        try:
            return self.get_response(event)
        except NoSuchMethodError as e:
            return self.format_output(str(e), status_code=400)
        except NoSuchResourceError as e:
            return self.format_output(str(e), status_code=404)
        except IncorrectConstructorParametersError as e:
            return self.format_output(str(e), status_code=400)
        except InvalidTypeError as e:
            return self.format_output(str(e), status_code=400)

    def get_response(self, event):
        path_steps = self.get_path_steps(event['path'])
        root_resource = Resource.create_resource(self.transform_object)
        response = self.call_method(path_steps, event, root_resource)
        return self.format_output(response)


    def get_path_steps(self, event_path):
        path_steps = event_path.split("/")[1:]
        if path_steps[-1] == "":
            del path_steps[-1]
        return path_steps

    def call_method(self, path_steps, event, resource):
        if len(path_steps) == 0:
            return resource.call_method(event)
        else:
            child = resource.child(path_steps[0])
            return self.call_method(path_steps[1:], event, child)

    def format_output(self, response, status_code=200):
        if response:
            return {
                'statusCode': status_code,
                'body': self.serialise(response)
            }
        else:
            return {
                'statusCode': 204
            }

    def serialise(self, data):
        return json.dumps(self.todict(data))

    def todict(self, obj):
        if isinstance(obj, dict):
            data = {}
            for (k, v) in obj.items():
                data[k] = self.todict(v)
            return data
        elif hasattr(obj, "__dict__"):
            data = dict([(key, self.todict(value))
                         for key, value in obj.__dict__.items()
                         if not key.startswith("_")])
            return data
        elif isinstance(obj, list):
            return [self.todict(value) for value in obj]
        elif isinstance(obj, date) or isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj

class Resource:
    def __init__(self, obj, parent=None, key=""):
        self.obj = obj
        self.parent = parent
        self.key = key
        if self.parent is not None:
            self.path = self.parent.path + "/" + str(self.key)
        else:
            self.path = ""

    @staticmethod
    def create_resource(obj, parent=None, key=None):
        if isinstance(obj, list):
            return ListResource(obj, parent, key)
        elif isinstance(obj, dict):
            return DictResource(obj, parent, key)
        elif callable(obj):
            return FunctionResource(obj, parent, key)
        elif isinstance(key, str) and key in dir(parent.obj.__class__) and isinstance(getattr(parent.obj.__class__, key), property):
            return PropertyResource(obj, parent, key)
        else:
            return ObjectResource(obj, parent, key)

    def call_method(self, event):
        method = event['httpMethod']
        if method == 'GET':
            return self.get()
        elif method == 'PUT':
            self.put(json.loads(event['body']))
        elif method == 'POST':
            self.post(json.loads(event['body'])) # Assumes valid JSON. Bug
        elif method == 'DELETE':
            self.delete()
        else:
            raise NoSuchMethodError(method, self.path)

    def get(self):
        raise NoSuchMethodError('GET', self.path)

    def put(self, value):
        raise NoSuchMethodError('PUT', self.path)

    def post(self, value):
        raise NoSuchMethodError('POST', self.path)

    def delete(self):
        if isinstance(self.parent, ListResource) and not self.parent.immutable():
            self.parent.remove(self.key)
        else:
            raise NoSuchMethodError('DELETE', self.path)


class ListResource(Resource):
    def __init__(self, obj, parent=None, key=""):
        super(ListResource, self).__init__(obj, parent, key)

        # Bug, assumes root is not list
        annotations = get_type_hints(self.parent.obj)
        has_annotation = key in annotations
        if has_annotation:
            annotation = annotations[key]
            if issubclass(annotation, list):
                self.type = annotation.__args__[0]
                print("Not Immutable")
                self.post = self._post


    def child(self, name):
        try:
            return Resource.create_resource(self.obj[int(name)], self, int(name))
        except ValueError:
            raise NoSuchResourceError(name)
        except IndexError:
            raise NoSuchResourceError(name)

    def get(self):
        return self.obj

    def put(self, value):
        self.parent.set(int(self.key), value)

    def set(self, key, value):
        self.obj[key] = value

    def call_constructor(self, args):
        try:
            return self.type(**args)
        except TypeError as e:
            print(e)
            raise IncorrectConstructorParametersError()

    def _post(self, value):
        if isinstance(value, self.type):
            self.obj.append(value)
        elif isinstance(value, dict):
            item = self.call_constructor(value)
            self.obj.append(item)

    def immutable(self):
        return 'type' not in dir(self)

    def remove(self, key):
        del self.obj[key]
        


class DictResource(Resource):
    def child(self, name):
        if name in self.obj:
            return Resource.create_resource(self.obj[name], self, name)
        else:
            raise NoSuchResourceError(name)

    def get(self):
        return self.obj

class FunctionResource(Resource):
    def child(self, name):
        return NoSuchResourceError(name)
    
    def get(self):
        return self.obj()

class ObjectResource(Resource):
    def child(self, name):
        if name in dir(self.obj):
            return Resource.create_resource(getattr(self.obj, name), self, name)
        else:
            raise NoSuchResourceError(name)

    def get(self):
        return self.obj

    def put(self, value):
        if isinstance(value, type(self.obj)):
            self.parent.set(self.key, value)
        else:
            raise InvalidTypeError(value, self.path, type(self.obj))


    def set(self, key, value):
        setattr(self.obj, key, value)

class PropertyResource(Resource):
    def __init__(self, obj, parent=None, key=""):
        super(PropertyResource, self).__init__(obj, parent, key)

        if getattr(self.parent.obj.__class__, self.key).fset is not None:
            self.put = self._put


    def child(self, name):
        return NoSuchResourceError(name)

    def get(self):
        return self.obj

    def _put(self, value):
        return self.parent.set(self.key, value)
