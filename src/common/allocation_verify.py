import pandas as pd
import numpy as np


def verify_allocation(allocation, classroom_list, event_list):
    """
    Returns whether an allocation (set of event-classroom pairs) is valid or not, for the given a set of validity conditions

    Parameters:
    allocation (list[dict]): list of event-classroom pairs, representing the allocation
    classroom_list (list[dict]): list of dictionaries representing each classroom available for allocation
    event_list (list[dict]): list of dictionaries representing each event to be allocated

    Returns:
    bool: whether the allocation is valid or not
    dict: dict of problems found in allocation
    """

    exceptions = {}
    is_valid = True

    aux_validity, exceptions['all_events_allocated'] = _all_events_allocated(allocation, event_list)
    is_valid = aux_validity and is_valid



    return is_valid, exceptions


# def _no_conflicts(allocation):

#     df_allocation = pd.DataFrame(allocation)

#     df_allocation.groupby('')

#     return

# def _has_conflicts(a_obj, a_p_obj):
#     """Returns wheter or not events a and a_p have conflitcts (i.e can't be allocated in the same classroom)"""

#     same_weekday = (a_obj['week_days'] == a_p_obj['week_days'])
#     if (a_obj['start_time'] <= a_p_obj['end_time']) and \
#         (a_obj['end_time'] >= a_p_obj['start_time']) :
#         hour_conflict = True
#     else:
#         hour_conflict = False

#     return same_weekday and hour_conflict

def _all_events_allocated(allocation, event_list):
    is_valid = True
    exception_list = []

    allocation_event_keys = [
        _get_event_key(a)
        for a in allocation
    ]
    event_keys = [
        _get_event_key(e)
        for e in event_list
    ]

    for event in event_keys:
        if event not in allocation_event_keys:
            is_valid = False
            exception_list.append(f'Event {event} not allocated')

    if len(exception_list) == 0: exception_list = None

    return is_valid, exception_list

def _get_event_key(event):
    """Returns the event key (subject code + class code + week day + start time)"""

    key_parameters = [
        'subject_code',
        'class_code',
        'week_day',
        'start_time',
    ]

    key = ''
    for p in key_parameters:
        key += str(event[p])

    return key
