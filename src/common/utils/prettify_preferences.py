def prettify_preferences(preferences):
    if "building_id" in preferences:
        preferences["building_id"] = str(preferences["building_id"])
    return preferences