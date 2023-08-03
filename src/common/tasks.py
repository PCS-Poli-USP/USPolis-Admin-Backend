from datetime import datetime, timedelta


def update_events_activeness(events):
    try:
        today = datetime.now()
        print("--- starting update_events_activeness task ---")
        for event in list(events.find()):
            start_interval = datetime.strptime(
                event["start_period"], "%Y-%m-%d"
            ) - timedelta(days=14)

            end_interval = datetime.strptime(
                event["end_period"], "%Y-%m-%d"
            ) + timedelta(days=14)

            print(event)
            query = {
                "subject_code": event["subject_code"],
                "class_code": event["class_code"],
                "week_day": event["week_day"],
                "start_time": event["start_time"],
                "end_time": event["end_time"],
            }

            events.update_many(
                query,
                {
                    "$set": {
                        "is_active": today >= start_interval and today <= end_interval,
                        "updated_at": today.strftime("%d/%m/%Y %H:%M"),
                    }
                },
            )

        print("--- end update_events_activeness task ---")
        return
    except Exception as ex:
        print(ex)
        return
