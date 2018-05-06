import json

class ApiGatewayTransform:
    def __init__(self, transform_object):
        self.transform_object = transform_object

    def call(self, event):
        path_steps = event['path'].split("/")[1:]
        response = self.call_path(path_steps, event, self.transform_object)
        return self.format_output(response)

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

    def format_output(self, response):
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
