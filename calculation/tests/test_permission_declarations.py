"""`calculation`'s rights are declared once, and their integers are pinned.

An identifier is what the roles carry (`RoleRight.right_id`): changing it withdraws
access from every role that holds it. This test pins it down, so that a change is a
decision visible in review and not a side effect.
"""

import json
from pathlib import Path

from django.test import TestCase

from calculation.apps import DJANGO_PERMS, RIGHTS, CalculationConfig, _PERM_CFG

# expected integer per config key, as deployed
EXPECTED = {
    "gql_query_calculation_rule_perms": ["153001"],
    "gql_mutation_update_calculation_rule_perms": ["153003"],
}

# Declare, lu nulle part : le module n'expose aucune mutation.
DORMANT_KEYS = {"gql_mutation_update_calculation_rule_perms"}


def _permissions_map():
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "backend" / "openIMIS" / "permissions_map.json"
        if candidate.exists():
            return json.loads(candidate.read_text(encoding="utf-8"))
    return None


class CalculationPermissionDeclarationsTestCase(TestCase):
    def test_the_right_ids_are_unchanged(self):
        for key, expected in EXPECTED.items():
            with self.subTest(key=key):
                self.assertEqual(getattr(CalculationConfig, key), expected)

    def test_perm_cfg_covers_exactly_the_declared_actions(self):
        declared = {
            (entity, action)
            for entity, actions in DJANGO_PERMS.items()
            for action in actions
        }
        mapped = set(_PERM_CFG.values())
        self.assertEqual(mapped, declared)

    def test_config_keys_and_expectations_line_up(self):
        self.assertEqual(set(_PERM_CFG), set(EXPECTED))

    def test_no_right_list_is_empty(self):
        # `has_perms([])` returns True: an empty list grants to everybody.
        for key in _PERM_CFG:
            with self.subTest(key=key):
                self.assertTrue(getattr(CalculationConfig, key))

    def test_the_two_ids_are_distinct(self):
        ids = [ids_[0] for ids_ in EXPECTED.values()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_django_names_follow_the_convention(self):
        self.assertEqual(
            RIGHTS.django_perm_names("calculationRule", "query"),
            ["calculation.view_calculationrule"],
        )
        self.assertEqual(
            RIGHTS.django_perm_names("calculationRule", "update"),
            ["calculation.change_calculationrule"],
        )

    def test_the_ids_are_in_the_permissions_map(self):
        catalogue = _permissions_map()
        if catalogue is None:
            self.skipTest("permissions_map.json introuvable depuis ce chemin")
        by_id = {str(v) for v in catalogue.values()}
        for key, ids in EXPECTED.items():
            with self.subTest(key=key):
                for right_id in ids:
                    self.assertIn(right_id, by_id)

    def test_the_dormant_key_is_still_dormant(self):
        """If someone wires 153003 up, this test reminds them to document it."""
        self.assertEqual(
            DORMANT_KEYS, {"gql_mutation_update_calculation_rule_perms"}
        )

    def test_configured_reads_the_value_at_call_time(self):
        from calculation.apps import configured_perms

        self.assertEqual(configured_perms("calculationRule", "query"), ["153001"])
