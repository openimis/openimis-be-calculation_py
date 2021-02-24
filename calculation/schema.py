import graphene
from .apps import CALCULATION_RULES, CalculationConfig
from .services import get_rule_name, get_parameters, get_linked_class
from django.contrib.contenttypes.models import ContentType


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


class LabelParamGQLType(graphene.ObjectType):
    name_en = graphene.String()
    name_fr = graphene.String()


class RightParamGQLType(graphene.ObjectType):
    read = graphene.String()
    write = graphene.String()
    update = graphene.String()
    replace = graphene.String()


class OptionParamGQLType(graphene.ObjectType):
    value = graphene.String()
    label = graphene.Field(LabelParamGQLType)


class CalculationParamsGQLType(graphene.ObjectType):
    type = graphene.String()
    name = graphene.String()
    label = graphene.Field(LabelParamGQLType)
    rights = graphene.Field(RightParamGQLType)
    option_set = graphene.List(OptionParamGQLType)
    default_value = graphene.String()


class CalculationParamsListGQLType(graphene.ObjectType):
    calculation_params = graphene.List(CalculationParamsGQLType)


class LinkedClassListGQLType(graphene.ObjectType):
    linked_classes = graphene.List(graphene.String)


class Query(graphene.ObjectType):

    calculation_rules_by_class_name = graphene.Field(
        CalculationRulesListGQLType,
        class_name=graphene.Argument(graphene.String, required=True),
    )

    calculation_rules = graphene.Field(
        CalculationRulesListGQLType,
    )

    calculation_params = graphene.Field(
        CalculationParamsListGQLType,
        class_name=graphene.Argument(graphene.String, required=True),
        instance_uuid=graphene.Argument(graphene.UUID, required=True),
        instance_class_name=graphene.Argument(graphene.String, required=True),
    )

    linked_class = graphene.Field(
        LinkedClassListGQLType,
        class_name_list=graphene.Argument(graphene.List(graphene.String), required=False),
    )

    def resolve_calculation_rules_by_class_name(parent, info, **kwargs):
        if not info.context.user.has_perms(CalculationConfig.gql_query_calculation_rule_perms):
           raise PermissionError("Unauthorized")

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
        if not info.context.user.has_perms(CalculationConfig.gql_query_calculation_rule_perms):
           raise PermissionError("Unauthorized")

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

    def resolve_calculation_params(parent, info, **kwargs):
        if not info.context.user.has_perms(CalculationConfig.gql_query_calculation_rule_perms):
           raise PermissionError("Unauthorized")

        # get the obligatory params from query
        class_name = kwargs.get("class_name", None)
        instance_uuid = kwargs.get("instance_uuid", None)
        instance_class_name = kwargs.get("instance_class_name", None)

        # get the instance class name to get instance object by uuid
        instance_type = ContentType.objects.get(model=f'{instance_class_name}')
        instance_class = instance_type.model_class()
        instance = instance_class.objects.get(id=instance_uuid)

        list_params = []
        if class_name:
            # use service to send signal to all class to obtain params related to the instance
            list_signal_result = get_parameters(class_name=class_name, instance=instance)
            if list_signal_result:
                for sr in list_signal_result:
                    # get the signal result - calculation param object
                    #  related to the input class name and instance
                    params = sr[1]
                    if params:
                       for param in params:
                           rights = RightParamGQLType(
                               read=param['rights']['read'] if 'read' in param['rights'] else None,
                               write=param['rights']['write'] if 'write' in param['rights'] else None,
                               update=param['rights']['update'] if 'update' in param['rights'] else None,
                               replace=param['rights']['replace'] if 'replace' in param['rights'] else None,
                           )
                           label = LabelParamGQLType(
                               name_en=param['label']['en'] if 'en' in param['label'] else None,
                               name_fr=param['label']['fr'] if 'fr' in param['label'] else None,
                           )
                           option_set = [OptionParamGQLType(
                               value=ov["value"],
                               label=LabelParamGQLType(name_en=ov["label"]["en"], name_fr=ov["label"]["fr"])
                           ) for ov in param["optionSet"]] if "optionSet" in param else []
                           list_params.append(
                                CalculationParamsGQLType(
                                    type=param['type'],
                                    name=param['name'],
                                    label=label,
                                    rights=rights,
                                    option_set=option_set,
                                    default_value=param['default'],
                                )
                           )
        return CalculationParamsListGQLType(list_params)

    def resolve_linked_class(parent, info, **kwargs):
        if not info.context.user.has_perms(CalculationConfig.gql_query_calculation_rule_perms):
           raise PermissionError("Unauthorized")
        result_linked_class = []
        # get the params from query
        class_name_list = kwargs.get("class_name_list", None)
        list_signal_result = get_linked_class(class_name_list=class_name_list)
        for sr in list_signal_result:
            result_linked_class = result_linked_class + sr[1]
        return LinkedClassListGQLType(list(set(result_linked_class)))
