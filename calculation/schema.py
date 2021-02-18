import graphene
from .apps import CALCULATION_RULES
from .services import get_rule_name


class CalculationRulesGQLType(graphene.ObjectType):
    calculation_class_name = graphene.String()
    status = graphene.String()
    description = graphene.String()
    uuid = graphene.UUID()
    class_param = graphene.JSONString()
    date_valid_from = graphene.Date()
    date_valid_to = graphene.Date()


class CalculationRulesListGQLType(graphene.ObjectType):
    calculation_rules = graphene.List(CalculationRulesGQLType)


class Query(graphene.ObjectType):

    calculation_rule = graphene.Field(
        CalculationRulesGQLType,
        class_name=graphene.Argument(graphene.String, required=True),
    )

    calculation_rules = graphene.Field(
        CalculationRulesListGQLType,
    )

    def resolve_calculation_rule(parent, info, **kwargs):
        class_name = kwargs.get("class_name", None)
        calculation_object = None
        if class_name:
            calculation_object = get_rule_name(class_name=class_name)[0][1]
        return CalculationRulesGQLType(
            calculation_class_name=calculation_object.calculation_rule_name,
            status=calculation_object.status,
            description=calculation_object.description,
            uuid=calculation_object.uuid,
            class_param=calculation_object.impacted_class_parameter,
            date_valid_from=calculation_object.date_valid_from,
            date_valid_to=calculation_object.date_valid_to,
        )

    def resolve_calculation_rules(parent, info, **kwargs):
        list_cr = []
        for cr in CALCULATION_RULES:
            list_cr.append(
                CalculationRulesGQLType(
                    calculation_class_name=cr.calculation_rule_name,
                    status=cr.status,
                    description=cr.description,
                    uuid=cr.uuid,
                    class_param=cr.impacted_class_parameter,
                    date_valid_from=cr.date_valid_from,
                    date_valid_to=cr.date_valid_to,
                )
            )
        return CalculationRulesListGQLType(list_cr)
