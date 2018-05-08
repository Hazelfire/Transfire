import json
from datetime import date, datetime


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


class ApiGatewayTransform:
    def __init__(self, transform_object):
        self.transform_object = transform_object

    def call(self, event):
        path_steps = self.get_path_steps(event['path'])
        try:
            response = self.call_path(path_steps, event, self.transform_object)
            return self.format_output(response)
        except IndexError:
            return self.format_output('index out of bounds', status_code=404)
        except ValueError as e:
            return self.format_output(str(e), status_code=404)
        except NoSuchMethodError as e:
            return self.format_output(str(e), status_code=400)
        except NoSuchResourceError as e:
            return self.format_output(str(e), status_code=400)
        except CannotSetResourceError as e:
            return self.format_output(str(e), status_code=400)

    def get_path_steps(self, event_path):
        path_steps = event_path.split("/")[1:]
        if path_steps[-1] == "":
            del path_steps[-1]
        return path_steps

    def call_path(self, path_steps, event, object_part):
        if len(path_steps) <= 1:
            return self.run_method(event, object_part, path_steps[0])
        else:
            attribute = self.find_attribute(object_part, path_steps[0])
            return self.call_path(path_steps[1:], event, attribute)

    def find_attribute(self, object_part, attribute):
        if type(object_part) is list:
            return object_part[int(attribute)]
        elif type(object_part) is dict:
            return object_part[attribute]
        elif attribute in dir(object_part):
            return getattr(object_part, attribute)
        else:
            raise NoSuchResourceError(attribute)

    def run_method(self, event, object_part, attribute):
        if event['httpMethod'] == 'GET':
            resource = self.find_attribute(object_part, attribute)
            if callable(resource):
                return resource()
            else:
                return resource
        elif event['httpMethod'] == 'PUT':
            try:
                self.set_attribute(object_part, attribute, json.loads(event['body']))
            except CannotSetResourceError:
                raise NoSuchMethodError(event['httpMethod'], event['path'])
        else:
            raise NoSuchMethodError(event['httpMethod'], event['path'])
    
    def set_attribute(self, object_part, key, value):
        if type(object_part) is list:
            object_part[int(key)] = value
        elif key in dir(object_part):
            if not callable(getattr(object_part, key)):
                setattr(object_part, key, value)
                print("or here")
            else:
                print("got here")
                raise CannotSetResourceError(key)

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
