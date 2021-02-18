import importlib
import inspect

from core.abs_calculation_rule import AbsCalculationRule
from django.apps import AppConfig


MODULE_NAME = "calculation"


DEFAULT_CFG = {}


CALCULATION_RULES = []


def read_all_calculation_rules():
    """function to read all calculation rules"""
    for name, cls in inspect.getmembers(importlib.import_module("calculation.calculation_rule"), inspect.isclass):
        if 'calculation' in cls.__module__.split('.')[0]:
            CALCULATION_RULES.append(cls)
            cls.ready()


class CalculationConfig(AppConfig):
    name = MODULE_NAME

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        read_all_calculation_rules()
