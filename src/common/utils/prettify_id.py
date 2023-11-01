def prettify_id(obj):
    if "_id" in obj:
        obj["id"] = str(obj["_id"])  # Convert _id to id
        del obj["_id"]
    return obj

def recursive_prettify_id(x):
    if isinstance(x, list):
        for item in x:
            recursive_prettify_id(item)
    elif isinstance(x, dict):
        prettify_id(x)
        for key, value in x.items():
            recursive_prettify_id(value)
    else:
        return x
    return x