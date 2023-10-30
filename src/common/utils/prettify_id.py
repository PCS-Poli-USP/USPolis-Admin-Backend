def prettify_id(obj):
    obj["id"] = str(obj["_id"])  # Convert _id to id
    del obj["_id"]
    return obj