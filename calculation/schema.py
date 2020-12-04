import graphene
import graphene_django_optimizer as gql_optimizer

from core.schema import OrderedDjangoFilterConnectionField
from calculation.models import CalculationRules, CalculationRulesDetails
from calculation.gql.gql_types import CalculationRulesGQLType, CalculationRulesDetailsGQLType


class Query(graphene.ObjectType):
    calculation_rules = OrderedDjangoFilterConnectionField(
        CalculationRulesGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )

    calculation_rules_details = OrderedDjangoFilterConnectionField(
        CalculationRulesDetailsGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )

    def resolve_calculation_rules(self, info, **kwargs):
        query = CalculationRules.objects
        return gql_optimizer.query(query.all(), info)

    def resolve_calculation_rules_details(self, info, **kwargs):
        query = CalculationRulesDetails.objects
        return gql_optimizer.query(query.all(), info)