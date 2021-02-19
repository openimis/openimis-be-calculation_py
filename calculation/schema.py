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

    calculation_rules_by_class_name = graphene.Field(
        CalculationRulesListGQLType,
        class_name=graphene.Argument(graphene.String, required=True),
    )

    calculation_rules = graphene.Field(
        CalculationRulesListGQLType,
    )

    def resolve_calculation_rules_by_class_name(parent, info, **kwargs):
        class_name = kwargs.get("class_name", None)
        list_cr = []
        if class_name:
            list_signal_result = get_rule_name(class_name=class_name)
            if list_signal_result:
                for sr in list_signal_result:
                    # get the signal result - calculation rule object
                    #  related to the input class name
                    rule = sr[1]
                    if rule:
                        list_cr.append(
                            CalculationRulesGQLType(
                                calculation_class_name=rule.calculation_rule_name,
                                status=rule.status,
                                description=rule.description,
                                uuid=rule.uuid,
                                class_param=rule.impacted_class_parameter,
                                date_valid_from=rule.date_valid_from,
                                date_valid_to=rule.date_valid_to,
                            )
                        )
        return CalculationRulesListGQLType(list_cr)

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
