from pulp import *
import numpy as np
from collections import Counter
from itertools import combinations, permutations

def _can_alocate(s_obj, a_obj):
    """Returns wheter or not classroom s has the resources required by event a"""

    a_prefs = a_obj['preferences']
    is_same_building = s_obj['building'] and a_prefs['building']

    if a_obj['subscribers'] <= s_obj['capacity']:
        has_enough_room = True
    else:
        has_enough_room = False

    if a_prefs['air_conditioning'] == True:
        satisfies_air_conditioning = s_obj['air_conditioning']
    else:
        satisfies_air_conditioning = True

    if a_prefs['projector'] == True:
        satisfies_projector = s_obj['projector']
    else:
        satisfies_projector = True

    if a_prefs['accessibility'] == True:
        satisfies_accessibility = s_obj['accessibility']
    else:
        satisfies_accessibility = True

    return is_same_building and \
        has_enough_room and \
        satisfies_air_conditioning and \
        satisfies_projector and \
        satisfies_accessibility


def _has_conflicts(a_obj, a_p_obj):
    """Returns wheter or not events a and a_p have conflitcts (i.e can't be allocated in the same classroom)"""

    same_weekday = (a_obj['week_day'] == a_p_obj['week_day'])
    if (a_obj['start_time'] <= a_p_obj['end_time']) and \
        (a_obj['end_time'] >= a_p_obj['start_time']) :
        hour_conflict = True
    else:
        hour_conflict = False

    return same_weekday and hour_conflict


def _process_solution(x, y, classroom_list, event_list):
    """Takes the optimization problem variables and processes them to a database-ready format"""

    allocation_list = []
    for c in classroom_list:
        for e in event_list:
            if x[c['classroom_name']][e['event_id']].value() == 1:
                entry = {
                    'subject_code' : e['subject_code'],
                    'class_code' : e['class_code'],
                    'week_day' : e['week_day'],
                    'start_time' : e['start_time'].strftime('%H:%M'),
                    'end_time' : e['end_time'].strftime('%H:%M'),
                    'classroom' : c['classroom_name'],
                    'building' : c['building'],
                }
                allocation_list.append(entry)

    return allocation_list


def allocate_classrooms(classroom_list, event_list):
    """
    Runs the allocation algorithm

    Parameters:
    classroom_list (list[dict]): list of dictionaries representing each classroom available for allocation
    event_list (list[dict]): list of dictionaries representing each event to be allocated

    Returns:
    list[dict] : list of allocations (event-classroom pairs) found

    """
    # Creating set S of classrooms
    S = [s['classroom_name'] for s in classroom_list]

    # Creating set A of events
    A = [a['event_id'] for a in event_list]

    # Creating set T of classes
    T = list(Counter([a['class_id'] for a in event_list]).keys()) # gets unique values of class_code

    # Creating set A_optional of events that don't have to necessarily be allocated
    A_optional = [a['event_id'] for a in event_list if a['has_to_be_allocated'] == False]

    # Creating USO (cost of allocation) and eta (possibility of allocation) matrices
    USO = {}
    eta = {}
    for s_obj in classroom_list:
        s = s_obj['classroom_name']
        USO[s] = {}
        eta[s] = {}
        for a_obj in event_list:
            a = a_obj['event_id']
            USO[s][a] = 1 - a_obj['subscribers']/s_obj['capacity']
            if _can_alocate(s_obj, a_obj):
                eta[s][a] = 1
            else:
                eta[s][a] = 0

    # Creating theta (time conflict of events) matrix
    theta = {}
    for a_obj in event_list:
        a = a_obj['event_id']
        theta[a] = {}
        for a_p_obj in event_list:
            a_p = a_p_obj['event_id']
            if a == a_p:
                continue

            if _has_conflicts(a_obj, a_p_obj):
                theta[a][a_p] = 1
            else:
                theta[a][a_p] = 0

    # Creating set A_t (subset of events a (in A) for a given class T)
    A_ = {}
    for t in T:
        A_[t] = []
    for a_obj in event_list:
        a = a_obj['event_id']
        t = a_obj['class_id']
        A_[t].append(a)

    # a_s_tuples = [(s,a) for s in S for a in A]
    ao_s_tuples = [(s,ao) for s in S for ao in A_optional]

    x = LpVariable.dicts("alloc_", (S,A), 0, 1, cat='Integer')
    y = LpVariable.dicts("classroom_changes_", (T), 0, None, cat='Integer')

    ############################ Problem formulation ############################

    prob = LpProblem("Classroom_allocation_problem", LpMinimize)

    # Objective function
    prob += (
        lpSum([y[t] for t in T]),
        "Total_classroom_changes"
    )
    prob += (
        100*lpSum([1 - x[s][ao] for (s, ao) in ao_s_tuples ]),
        "Events_not_allocated"
    )

    # One and only one classroom per mandatory event constraint
    for a in A:
        if a not in A_optional:
            prob += (
                lpSum([x[s][a] for s in S]) == 1,
                f"Number_of_allocated_classrooms_for_mandatory_event_{a}"
            )

    # One or zero classrooms per optional event constraint
    for a in A:
        if a in A_optional:
            prob += (
                lpSum([x[s][a] for s in S]) <= 1,
                f"Number_of_allocated_classrooms_for_optional_event_{a}"
            )

    # One classroom per event constraint
    # for a in A:
    #     prob += (
    #         lpSum([x[s][a] for s in S]) == 1,
    #         f"Number_of_allocated_classrooms_for_event_{a}"
    #     )

    # Resources/Preferences constraint
    for s in S:
        for a in A:
            prob += (
                x[s][a] <= eta[s][a],
                f'Classroom_{s}_can_contain_event{a}'
            )

    # Time conflict constraint
    for s in S:
        for a in A:
            for a_p in A:
                if a == a_p:
                    continue
                if theta[a][a_p] == 1:
                    prob += (
                        x[s][a] + x[s][a_p] <= 1,
                        f'Events_{a}_and_{a_p}_cant_both_be_in_classroom_{s}'
                    )

    # Bound the changement of classrooms per class constraint
    for t in T:
        for s_combination in combinations(S, len(A_[t])):
            for s_tuple in permutations(s_combination):
                prob += (
                    lpSum([x[s_tuple[i]][A_[t][i]] for i in range(len(A_[t]))]) <= 1 + y[t],
                    f'Classroom_change_bounding_for_class_{t}_with_pattern_{s_tuple}'
                )


    ############################## Problem solution ##############################

    # The problem data is written to an .lp file
    prob.writeLP("src/common/allocation/ClassroomAllocationProblem.lp")

    # The problem is solved using PuLP's choice of Solver
    solver = get_solver('GUROBI')
    prob.solve(solver)

    # The status of the solution is printed to the screen
    print("Solution status:", LpStatus[prob.status])

    if(prob.status < 0):
        raise Exception(f"Solution status: {LpStatus[prob.status]}")

    # Each of the variables is printed with it's resolved optimum value
    # for var in prob.variables():
    #     print(var.name, "=", var.varValue)

    # The optimised objective function value is printed to the screen
    print("Total classroom changes = ", value(prob.objective))

    allocation_list = _process_solution(x, y, classroom_list, event_list)

    return allocation_list
