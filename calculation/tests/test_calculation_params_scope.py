"""OP-3322: `calculationParams` only loads instances a rule declares, within row security."""
from unittest import mock

from django.test import RequestFactory, TestCase
from graphene import Schema
from graphene.test import Client

from calculation.apps import CALCULATION_RULES
from calculation.schema import Query
from calculation.tests.test_graphql import MockCalculationRule1
from core.gql_errors import BAD_REQUEST, NOT_FOUND, format_error
from core.models import Role
from core.test_helpers import LogInHelper, create_test_role

PARAMETER = {
    "type": "number",
    "name": "rate",
    "label": {"en": "Rate", "fr": "Rate"},
    "rights": {"read": "153001"},
    "relevance": "True",
    "condition": "",
    "default": "0",
}


class RoleRightRule(MockCalculationRule1):
    """A rule whose parameters go on a RoleRight, read from its Role."""

    uuid = "44444444-4444-4444-4444-444444444444"
    impacted_class_parameter = [{"class": "RoleRight", "parameters": [PARAMETER]}]


QUERY = '''
query {{
  calculationParams(className: "{class_name}", instanceClassName: "{instance_class}",
                    instanceId: "{instance_id}") {{
    calculationParams {{ name }}
  }}
}}
'''


class CalculationParamsScopeTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.original_calculation_rules = CALCULATION_RULES.copy()
        CALCULATION_RULES.clear()
        CALCULATION_RULES.append(RoleRightRule)

    @classmethod
    def tearDownClass(cls):
        CALCULATION_RULES.clear()
        CALCULATION_RULES.extend(cls.original_calculation_rules)
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        cls.user = LogInHelper().get_or_create_user_api()
        cls.role = create_test_role(name="OP3322CalculationRole")

    def setUp(self):
        self.client = Client(Schema(query=Query), format_error=lambda e: format_error(e, debug=False))
        request = RequestFactory().get("/graphql")
        request.user = self.user
        request.user.has_perms = mock.Mock(return_value=True)
        self.context = request

    def _query(self, class_name="RoleRight", instance_class="Role", instance_id=None):
        return self.client.execute(QUERY.format(
            class_name=class_name, instance_class=instance_class,
            instance_id=self.role.id if instance_id is None else instance_id,
        ), context=self.context)

    def _error_code(self, result):
        self.assertTrue(result.get("errors"), result)
        return result["errors"][0]["extensions"]["code"]

    def test_declared_instance_class_returns_the_parameters(self):
        result = self._query()
        self.assertIsNone(result.get("errors"), result)
        names = [p["name"] for p in result["data"]["calculationParams"]["calculationParams"]]
        self.assertEqual(names, ["rate"])

    def test_instance_class_no_rule_links_is_refused(self):
        result = self._query(instance_class="InteractiveUser", instance_id=1)
        self.assertEqual(self._error_code(result), BAD_REQUEST)

    def test_class_name_no_rule_impacts_is_refused(self):
        result = self._query(class_name="UserRole")
        self.assertEqual(self._error_code(result), BAD_REQUEST)

    def test_instance_outside_row_security_is_not_found(self):
        with mock.patch.object(Role, "get_queryset", lambda queryset, user=None: queryset.none()):
            result = self._query()
        self.assertEqual(self._error_code(result), NOT_FOUND)

    def test_unknown_instance_is_not_found(self):
        result = self._query(instance_id="not-an-id")
        self.assertEqual(self._error_code(result), NOT_FOUND)
