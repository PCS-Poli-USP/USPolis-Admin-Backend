def prettify_id(bson_doc):
    bson_doc["id"] = str(bson_doc["_id"])
    del bson_doc["_id"]

    return bson_doc