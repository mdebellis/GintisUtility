from franz.openrdf.connect import ag_connect
from franz.openrdf.vocabulary import RDF
from functools import reduce
from ag_api import *
import random


or_state_class = conn.createURI("http://www.semanticweb.org/mdebe/ontologies/2024/7/util/Lottery")
state_class = conn.createURI("http://www.semanticweb.org/mdebe/ontologies/2024/7/util/State")
sub_state_property = conn.createURI("http://www.semanticweb.org/mdebe/ontologies/2024/7/util/hasSubState")
utility_property = conn.createURI("http://www.semanticweb.org/mdebe/ontologies/2024/7/util/utility")
preferred_state_property = conn.createURI("http://www.semanticweb.org/mdebe/ontologies/2024/7/util/preferredState")
expected_value_property = conn.createURI("http://www.semanticweb.org/mdebe/ontologies/2024/7/util/expectedValue")
probability_property = conn.createURI("http://www.semanticweb.org/mdebe/ontologies/2024/7/util/probability")

example_list =[find_instance_from_iri("SlotMachinePaysOff"),find_instance_from_iri("SlotMachineReturnsNothing")]

def higher_utility(or_instance1, or_instance2):
    if get_utility(or_instance1) > get_utility(or_instance2):
        return or_instance1
    else:
        return or_instance2

# Convert to string strips off all the data type crud and just leaves the number as a literal
def get_utility(proposition_object):
    utility = float(convert_to_string(get_value(proposition_object, utility_property)))
    return utility

def max_utility(obj_list):
    return max(obj_list, key=get_utility)

def find_max_utility_state(or_state):
    alternative_states= get_values(or_state, sub_state_property)
    return max_utility(alternative_states)

def set_preferred_state(or_state):
    preferred_state = find_max_utility_state(or_state)
    put_value(or_state, preferred_state_property, preferred_state)

def set_preferred_states():
    or_instances = find_instances_of_class(or_state_class)
    for or_instance in or_instances:
        set_preferred_state(or_instance)

def set_expected_values():
    state_instances = find_instances_of_class(state_class)
    for state_instance in state_instances:
        set_expected_value(state_instance)

def set_expected_value(state_instance):
    sub_states = get_values(state_instance, sub_state_property)
    expected_value = 0.0
    sub_states_exist = False
    for sub_state in sub_states:
        expected_value = expected_value + get_utility(sub_state)
        sub_states_exist = True
    if sub_states_exist:
        put_value(state_instance, expected_value_property, expected_value)

def get_probability_list(lottery_instance):
    outcomes = get_values(lottery_instance, sub_state_property)
    probability_list = []
    for outcome in outcomes:
        utility = get_utility(outcome)
        probability = get_value(outcome, probability_property)
        probability_list.append([probability, utility])
    return probability_list

def weighted_choice(prob_outcome_list):
    probabilities = [item[0] for item in prob_outcome_list]
    outcomes = [item[1] for item in prob_outcome_list]
    return random.choices(outcomes, probabilities)[0]

    # Example usage



slot_pays = find_instance_from_iri("SlotMachinePaysOff")
slot_loses = find_instance_from_iri("SlotMachineReturnsNothing")
slot_choices = find_instance_from_iri("SlotMachineResult")
#set_preferred_states()
set_expected_values()
print(get_value(slot_choices, preferred_state_property))
prob_outcome_list = [(0.7, 1), (0.3, 2)]
result = weighted_choice(prob_outcome_list)
print(result)
