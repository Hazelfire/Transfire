import json


class ApiGatewayTransform:
    def __init__(self, transform_object):
        self.transform_object = transform_object

    def call(self, event):
        path_steps = self.get_path_steps(event['path'])
        response = self.call_path(path_steps, event, self.transform_object)
        if response is not None:
            return self.format_output(response)
        else:
            return self.format_output('No such resource', status_code=400)

    def get_path_steps(self, event_path):
        path_steps = event_path.split("/")[1:]
        if path_steps[-1] == "":
            del path_steps[-1]
        return path_steps

    def call_path(self, path_steps, event, object_part):
        if len(path_steps) == 0:
            return self.run_method(event,  object_part)
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

    def run_method(self, event, object_part):
        if event['method'] == 'GET':
            if callable(object_part):
                return object_part()
            else:
                return object_part

    def format_output(self, response, status_code=200):
        return {
            'statusCode': status_code,
            'body': self.serialise(response)
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
                         for key, value in obj.__dict__.items()])
            return data
        else:
            return obj
