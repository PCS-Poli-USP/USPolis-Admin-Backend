from datetime import datetime

def break_class_into_events(class_obj):
    event_list = []

    if isinstance(class_obj['start_time'], list):
        for i in range(len(class_obj['start_time'])):
            # allocator data
            # event = class_obj.copy()
            event = { }
            event['start_time'] = class_obj['start_time'][i]
            event['end_time'] = class_obj['end_time'][i]
            event['week_day'] = class_obj['week_days'][i]

            if len(class_obj['professors']) > i:
                event['professor'] = class_obj['professors'][i]

            # event['event_id'] = str(event['subject_code']) + '_' + str(event['class_code']) + '_' + str(i)
            # event['class_id'] = str(event['subject_code']) + '_' + str(event['class_code'])

            event['subscribers'] = class_obj['subscribers']

            # event data
            event['class_code'] = class_obj['class_code']
            event['subject_code'] = class_obj['subject_code']
            event['subject_name'] = class_obj['subject_name']
            event['start_period'] = datetime.strptime(class_obj['start_period'], '%d/%m/%Y').strftime('%Y-%m-%d')
            event['end_period'] = datetime.strptime(class_obj['end_period'], '%d/%m/%Y').strftime('%Y-%m-%d')
            event['class_type'] = class_obj['class_type']
            event['vacancies'] = class_obj['vacancies']
            event['pendings'] = class_obj['pendings']


            # set default preferences
            event['preferences'] = {
                'building' : 'Biênio',
                'air_conditioning' : False,
                'projector' : False,
                'accessibility' : False,
            }

            event['has_to_be_allocated'] = True

            event_list.append(event)

    return event_list