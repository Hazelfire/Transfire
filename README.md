# Transfire
Easilly turn your old python projects into microservices.

How easy?

```python
from transfire import ApiGatewayTransform
import your_amazing_project

def handler(event, context):
    transform = ApiGatewayTransform(your_amazing_project())
    transform.call(event)
```

That easy.

## Wait, what?
Transfire turns on object into a http interface, if an object that is passed
to it has a `name` attribute, calling `GET /name` will return the name.

This works recursively with arrays, dictionaries and objects.
