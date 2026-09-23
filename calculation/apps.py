import importlib
import inspect

from django.apps import AppConfig
from core.abs_calculation_rule import AbsStrategy
from core.rights_declaration import RightsDeclaration

MODULE_NAME = "calculation"


# Droits, par entite puis par action. Une seule entite, `calculationRule` : la regle de
# calcul, que les autres modules interrogent pour valoriser une cotisation, une prestation
# ou une commission.
#
# `update` (153003) est une declaration dormante : le module n'expose aucune mutation
# (`schema.py` n'a pas de classe `Mutation`), l'identifiant est donc declare et lu nulle
# part. Conserve plutot que supprime - il est au catalogue (`permissions_map.json`), des
# roles peuvent deja le porter, et c'est l'identifiant qui devra etre applique le jour ou
# la mutation existera.
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


# Pas de `get_rights` sur un modele : `calculation/models.py` est vide. Une regle de
# calcul est une classe de strategie (`AbsStrategy`) decouverte a l'import, pas une ligne
# en base - il n'y a donc aucun modele a qui confier l'acces, et aucun `scope_parent` a
# declarer. Le point d'acces a la valeur configuree est `configured_perms`, ci-dessus.
# Le nom django reste purement declaratif, comme pour `workflow`.


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
