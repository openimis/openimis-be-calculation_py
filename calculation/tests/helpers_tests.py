from functools import lru_cache
from unittest import TestCase

from calculation.models import CalculationRules, CalculationRulesDetails
from calculation.tests import create_test_calculation_rules, create_test_calculation_rules_details


class HelpersTest(TestCase):
    """
    Class to check whether the helper methods responsible for creating test data work correctly.
    """

    def test_create_calculations_rules(self):
        calculations_rules = self.__create_test_calculations_rules()
        db_calculations_rules = CalculationRules.objects.filter(id=calculations_rules.id).first()
        self.assertEqual(
            db_calculations_rules,
            calculations_rules,
            "Failed to create calculations rules in helper"
        )

    def test_create_calculations_rules_details(self):
        calculations_rules_details = self.__create_test_calculations_rules_details()
        db_calculations_rules_details = CalculationRulesDetails.objects.filter(id=calculations_rules_details.id).first()
        self.assertEqual(
            db_calculations_rules_details,
            calculations_rules_details,
            "Failed to create calculations details rules in helper"
        )

    def test_create_calculations_rules_custom_params(self):
        calculations_rules = self.__create_test_calculations_rules(custom=True)
        db_calculations_rules = CalculationRules.objects.filter(id=calculations_rules.id).first()

        self.assertEqual(
            db_calculations_rules.calculation_class_name,
            self.__custom_calculations_rules_params['calculation_class_name']
        )
        self.assertEqual(
            db_calculations_rules.priority,
            self.__custom_calculations_rules_params['priority']
        )
        self.assertEqual(
            db_calculations_rules.status,
            self.__custom_calculations_rules_params['status']
        )

    def test_create_calculations_rules_details_custom_params(self):
        calculations_rules_details = self.__create_test_calculations_rules_details(custom=True)
        db_calculations_rules_details = CalculationRulesDetails.objects.filter(id=calculations_rules_details.id).first()
        params = self.__custom_calculations_rules_details_params
        self.assertEqual(db_calculations_rules_details.calculation_rules, params['calculation_rules'])
        self.assertEqual(db_calculations_rules_details.version, 1)

    @property
    @lru_cache(maxsize=2)
    def __custom_calculations_rules_params(self):
        return {
            'calculation_class_name': 'CustomCode',
            'priority': 2,
            'status': 1,
            }

    @property
    @lru_cache(maxsize=2)
    def __custom_calculations_rules_details_params(self):
        return {
            'calculation_rules': self.__create_test_calculations_rules(custom=True),
        }

    def __create_test_instance(self, function, **kwargs):
        if kwargs:
            return function(**kwargs)
        else:
            return function()

    def __create_test_calculations_rules(self, custom=False):
        custom_params = self.__custom_calculations_rules_params if custom else {}
        return self.__create_test_instance(create_test_calculation_rules, custom_props=custom_params)

    def __create_test_calculations_rules_details(self, custom=False):
        custom_params = self.__custom_calculations_rules_details_params if custom else {}
        return self.__create_test_instance(create_test_calculation_rules_details, custom_props=custom_params)