import graphene
from core import prefix_filterset, ExtendedConnection
from graphene_django import DjangoObjectType
from calculation.models import CalculationRules, CalculationRulesDetails


class CalculationRulesGQLType(DjangoObjectType):

    class Meta:
        model = CalculationRules
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "calculation_class_name": ["exact"],
            "description": ["exact"],
            "priority": ["exact", "lt", "lte", "gt", "gte"],
            "status": ["exact", "lt", "lte", "gt", "gte"],
            "date_created": ["exact", "lt", "lte", "gt", "gte"],
            "date_updated": ["exact", "lt", "lte", "gt", "gte"],
            "user_created": ["exact"],
            "user_updated": ["exact"],
            "is_deleted": ["exact"],
            "version": ["exact"]
        }

        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        return CalculationRules.get_queryset(queryset, info)


class CalculationRulesDetailsGQLType(DjangoObjectType):

    class Meta:
        model = CalculationRulesDetails
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            #**prefix_filterset("calculation_rules__", CalculationRules._meta.filter_fields),
            "status": ["exact", "lt", "lte", "gt", "gte"],
            "main": ["exact"],
            "date_created": ["exact", "lt", "lte", "gt", "gte"],
            "date_updated": ["exact", "lt", "lte", "gt", "gte"],
            "user_created": ["exact"],
            "user_updated": ["exact"],
            "is_deleted": ["exact"],
            "version": ["exact"]
        }

        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        return CalculationRulesDetails.get_queryset(queryset, info)