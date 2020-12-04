import xml.etree.ElementTree as ET
from django.core.exceptions import PermissionDenied
import core
from django.db import connection, transaction

from django.conf import settings


@core.comparable
class CalculationRules(object):

    def __init__(self, calculation_rules):
        self.calculation_rules = calculation_rules
        pass

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def create(self, calculation_rules):
        pass

    def update(self, calculation_rules):
        pass

    def delete(self, calculation_rules):
        pass

    def replace_calculation_rules(self, calculation_rules):
        pass

    def remove_calculation_rules(self, calculation_rules):
        pass


@core.comparable
class CalculationRulesDetails(object):

    def __init__(self, calculation_rules_details):
        self.calculation_rules_details = calculation_rules_details
        pass

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def create(self, calculation_rules_details):
        pass

    def update(self, calculation_rules_details):
        pass

    def delete(self, calculation_rules_details):
        pass

    def remove_calculation_rules_details(self, calculation_rules_details):
        pass