def prettify_preferences(preferences):
    preferences["building_id"] = str(preferences["building_id"])
    return preferences