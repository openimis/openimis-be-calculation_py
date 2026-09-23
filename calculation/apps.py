import importlib
import inspect

from django.apps import AppConfig
from core.abs_calculation_rule import AbsStrategy
from core.rights_declaration import RightsDeclaration

MODULE_NAME = "calculation"


# Rights, by entity then by action. A single entity, `calculationRule`: the calculation
# rule the other modules query to value a contribution, a benefit or a commission.
#
# `update` (153003) is a dormant declaration: the module exposes no mutation
# (`schema.py` has no `Mutation` class), so the identifier is declared and read nowhere.
# Kept rather than removed - it is in the catalogue (`permissions_map.json`), roles may
# already carry it, and it is the identifier that will have to be enforced the day the
# mutation exists.
DJANGO_PERMS = {
    "calculationRule": {
        "query": ("calculation.view_calculationrule", 153001),
        "update": ("calculation.change_calculationrule", 153003),
    },
}

_PERM_CFG = {
    "gql_query_calculation_rule_perms": ("calculationRule", "query"),
    "gql_mutation_update_calculation_rule_perms": ("calculationRule", "update"),
}

RIGHTS = RightsDeclaration(MODULE_NAME, DJANGO_PERMS, _PERM_CFG)

perms = RIGHTS.perms
django_perms = RIGHTS.django_perm_names
configured_perms = RIGHTS.configured
require = RIGHTS.require


# No `get_rights` on a model: `calculation/models.py` is empty. A calculation rule is a
# strategy class (`AbsStrategy`) discovered at import time, not a row in the database -
# so there is no model to entrust the access to, and no `scope_parent` to declare. The
# access point to the configured value is `configured_perms`, above. The django name
# stays purely declarative, as for `workflow`.


DEFAULT_CFG = {
}


CALCULATION_RULES = []


def read_all_calculation_rules(module_name, rule_list):
    calc_root = f"{module_name}.calculation_rule"
    """function to read all calculation rules from that module"""
    for name, cls in inspect.getmembers(importlib.import_module(calc_root), inspect.isclass):
        if issubclass(cls, AbsStrategy) and cls.__module__.startswith(calc_root):
            rule_list.append(cls)
            cls.ready()

class CalculationConfig(AppConfig):
    name = MODULE_NAME

    # Rights: constants, no longer overridable. They go neither through DEFAULT_CFG
    # nor through ready(): `ModuleConfiguration.get_or_default` now ignores any
    # `_perms` key stored in the database.
    gql_query_calculation_rule_perms = RIGHTS.perms("calculationRule", "query")
    gql_mutation_update_calculation_rule_perms = RIGHTS.perms("calculationRule", "update")

    def __load_config(self, cfg):
        for field in cfg:
            if hasattr(CalculationConfig, field):
                setattr(CalculationConfig, field, cfg[field])

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self.__load_config(cfg)
        read_all_calculation_rules(MODULE_NAME, CALCULATION_RULES)
