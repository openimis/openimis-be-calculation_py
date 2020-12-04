import json
from functools import lru_cache
from calculation.models import CalculationRules, CalculationRulesDetails
from datetime import date
from core.models import InteractiveUser, User


def create_test_calculation_rules(custom_props={}):
    user = __get_or_create_simple_calculation_user()

    object_data = {
        'calculation_class_name': "Calculation class name",
        'description': "Calculation rule descriptiom",
        'priority': 1,
        "status": 1,
        'json_ext': json.dumps("{}"),
        **custom_props
    }

    calculation_rules = CalculationRules(**object_data)
    calculation_rules.save(username=user.username)

    return calculation_rules


def create_test_calculation_rules_details(calculation_rules=None, custom_props={}):
    if not calculation_rules:
        calculation_rules = create_test_calculation_rules()

    user = __get_or_create_simple_calculation_user()

    object_data = {
        'calculation_rules': calculation_rules,
        'status': 1,
        'main': True,
        'params': '{\"param1\": \"0.45\", \"param2\": \"55\"}',
        'class_params': '{\"Type\": \"test type\", \"Rights\": \"test right\", \"Relevance\": \"test relevance\", \"Conditions\": \"test conditions\"}',
        'json_ext': json.dumps("{}"),
        **custom_props
    }

    calculation_rules_details = CalculationRulesDetails(**object_data)
    calculation_rules_details.save(username=user.username)

    return calculation_rules_details


def __get_or_create_simple_calculation_user():
    user = User.objects.get(username="admin")
    return user