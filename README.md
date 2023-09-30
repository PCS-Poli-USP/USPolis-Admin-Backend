# USPolis Admin Backend

This is the repo for the backend of the USPolis Admin application

## Running

```bash
pip install requirements.txt
python3 wsgi.py
```

## Stack

The API is built based on [```Flask```](https://flask.palletsprojects.com/en/2.3.x/) framework and also on the [```flasgger```](https://github.com/flasgger/flasgger) library.

## Architecture

The main code of the API is centered on **blueprints** and **schemas**. This topic will cover what you should encounter on each of this project's folders.

### Schemas

This folder is reserved for definition of ```flasgger schemas```, which are like "entities" for our system.

They are declared as subclasses of the **Schema** class, and defines schemas similar to "objects" or "dictionaries", containing a series of properties, each one with its name and field type.

```python
class SubjectSchema(Schema):
  subject_name = fields.Str()
  subject_code = fields.Str()
```

The most common use case of these schemas on this api is to **validate endpoints inputs**, using the ```.load()``` schema method. This method throws errors when the format of the request is not coherent with the schema.

Below is a demonstration of this use case in a POST request.

```python
def create_classroom():
    try:
        classroom_schema.load(request.json)
        dict_request_body = request.json

    ...

    except DuplicateKeyError as err:
        return {"message": err.details["errmsg"]}, 400

    except ValidationError as err:
        return {"message": err.messages}, 400
```

Beyong helping in validating, they are important for ```flasgger``` to generate the ```swagger``` API documentation.

### Blueprints

Here is where all the API business logic is centered. Each blueprint file is responsible for a determined section of the API, tipically an endpoint and its HTTP methods.

In each blueprint file, there are:
- **endpoints routing**: Flask's basic functionalities
- **request treatment**: Schema's ```load``` method 
- **database consulting**: ```mongodb``` python driver
- **error handling**

### Common

In this folder, we encounter some utilities for our server.

### Database

File inside Common folder, it contains the connection instantiation for ```mongodb``` database.