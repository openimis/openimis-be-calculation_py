import json

from .apps import AbsCalculationRule
from .config import CLASS_RULE_PARAM_VALIDATION, \
    DESCRIPTION_CONTRIBUTION_VALUATION
from contribution_plan.models import ContributionPlanBundleDetails
from core.signals import Signal
from core import datetime
from policyholder.models import PolicyHolderInsuree


class ContributionValuationRule(AbsCalculationRule):

    version = 1
    uuid = "0e1b6dd4-04a0-4ee6-ac47-2a99cfa5e9a8"
    calculation_rule_name = "CV: percent of income"
    description = DESCRIPTION_CONTRIBUTION_VALUATION
    impacted_class_parameter = CLASS_RULE_PARAM_VALIDATION
    date_valid_from = datetime.datetime(2000, 1, 1)
    date_valid_to = None
    status = "active"

    signal_get_rule_name = Signal(providing_args=[])
    signal_get_rule_details = Signal(providing_args=[])
    signal_get_param = Signal(providing_args=[])
    signal_get_linked_class = Signal(providing_args=[])
    signal_calculate_event = Signal(providing_args=[])

    @classmethod
    def ready(cls):
        now = datetime.datetime.now()
        condition_is_valid = (now >= cls.date_valid_from and now <= cls.date_valid_to) \
            if cls.date_valid_to else (now >= cls.date_valid_from and cls.date_valid_to is None)
        if condition_is_valid:
            if cls.status == "active":
                # register signals getParameter to getParameter signal and getLinkedClass ot getLinkedClass signal
                cls.signal_get_rule_name.connect(cls.get_rule_name, dispatch_uid="on_get_rule_name_signal")
                cls.signal_get_rule_details.connect(cls.get_rule_details, dispatch_uid="on_get_rule_details_signal")
                cls.signal_get_param.connect(cls.get_parameters, dispatch_uid="on_get_param_signal")
                cls.signal_get_linked_class.connect(cls.get_linked_class, dispatch_uid="on_get_linked_class_signal")
                cls.signal_calculate_event.connect(cls.run_calculation_rules, dispatch_uid="on_calculate_event_signal")

    @classmethod
    def active_for_object(cls, instance, context):
        return instance.__class__.__name__ == "ContractContributionPlanDetails" \
               and context in ["create", "update"] \
               and cls.check_calculation(instance)

    @classmethod
    def check_calculation(cls, instance):
        match = False
        class_name = instance.__class__.__name__
        if class_name == "ContributionPlan":
            match = str(cls.uuid) == str(instance.calculation)
        elif class_name == "PolicyHolderInsuree":
            match = cls.check_calculation(instance.contribution_plan_bundle)
        elif class_name == "ContractDetails":
            match = cls.check_calculation(instance.contribution_plan_bundle)
        elif class_name == "ContractContributionPlanDetails":
            match = cls.check_calculation(instance.contribution_plan)
        elif class_name == "ContributionPlanBundle":
            list_cpbd = list(ContributionPlanBundleDetails.objects.filter(
                contribution_plan_bundle=instance
            ))
            for cpbd in list_cpbd:
                if match is False:
                    if cls.check_calculation(cpbd.contribution_plan):
                       match = True
        return match

    @classmethod
    def calculate(cls, instance, *args):
        if instance.__class__.__name__ == "ContractContributionPlanDetails":
            # check type of json_ext - in case of string - json.loads
            cp_params, cd_params = instance.contribution_plan.json_ext, instance.contract_details.json_ext
            ph_insuree = PolicyHolderInsuree.objects.filter(
                insuree=instance.contract_details.insuree).first()
            phi_params = ph_insuree.json_ext
            if isinstance(cp_params, str):
                cp_params = json.loads(cp_params)
            if isinstance(cd_params, str):
                cd_params = json.loads(cd_params)
            if isinstance(phi_params, str):
                phi_params = json.loads(phi_params)
            if "rate" in cp_params:
                rate = int(cp_params["rate"])
                if cd_params:
                    if "income" in cd_params:
                        income = float(cd_params["income"])
                    elif "income" in phi_params:
                        income = float(phi_params["income"])
                    else:
                        return False
                elif "income" in phi_params:
                    income = float(phi_params["income"])
                else:
                    return False
                value = float(income) * (rate/100)
                return value
            else:
                return False
        else:
            return False

    @classmethod
    def get_linked_class(cls, sender, class_name, **kwargs):
        list_class = []
        if class_name == "ContributionPlan" or class_name is None:
            list_class.append("Calculation")
        elif class_name == "PolicyHolderInsuree" or class_name is None:
            list_class.append("ContributionPlanBundle")
        elif class_name == "ContractDetails" or class_name is None:
            list_class.append("ContributionPlanBundle")
        elif class_name == "ContractContributionPlanDetails" or class_name is None:
            list_class.append("ContributionPlan")
        elif class_name == "ContributionPlanBundle" or class_name is None:
            list_class.append("ContributionPlan")
        return list_class
