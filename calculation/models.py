from django.conf import settings
from django.db import models
from core import models as core_models, fields
from graphql import ResolveInfo
from jsonfallback.fields import FallbackJSONField


class CalculationRulesManager(models.Manager):
    def filter(self, *args, **kwargs):
        keys = [x for x in kwargs if "itemsvc" in x]
        for key in keys:
            new_key = key.replace("itemsvc", self.model.model_prefix)
            kwargs[new_key] = kwargs.pop(key)
        return super(CalculationRulesManager, self).filter(*args, **kwargs)


class CalculationRules(core_models.HistoryBusinessModel):
    calculation_class_name = models.CharField(db_column='CalculationsClassName', blank=True, null=True, max_length=255)
    description = models.CharField(db_column='Description', blank=True, null=True, max_length=255)
    priority = models.IntegerField(db_column='Priority', blank=True, null=True)
    status = models.IntegerField(db_column='Status', blank=True, null=True)

    objects = CalculationRulesManager()

    @classmethod
    def get_queryset(cls, queryset, user):
        queryset = cls.filter_queryset(queryset)
        if isinstance(user, ResolveInfo):
            user = user.context.user
        if settings.ROW_SECURITY and user.is_anonymous:
            return queryset.filter(id=-1)
        if settings.ROW_SECURITY:
            pass
        return queryset

    class Meta:
        db_table = 'tblCalculationRules'


class CalculationRulesDetailsManager(models.Manager):
    def filter(self, *args, **kwargs):
        keys = [x for x in kwargs if "itemsvc" in x]
        for key in keys:
            new_key = key.replace("itemsvc", self.model.model_prefix)
            kwargs[new_key] = kwargs.pop(key)
        return super(CalculationRulesDetailsManager, self).filter(*args, **kwargs)


class CalculationRulesDetails(core_models.HistoryModel):
    calculation_rules = models.ForeignKey(CalculationRules, db_column='CalculationRulesUUID', on_delete=models.deletion.DO_NOTHING)
    status = models.IntegerField(db_column='Status', blank=True, null=True)
    main = models.BooleanField(db_column='Main', blank=True, null=True)
    params = FallbackJSONField(db_column="Params", blank=True, null=True)
    class_params = FallbackJSONField(db_column="ClassParams", blank=True, null=True)

    objects = CalculationRulesDetailsManager()

    @classmethod
    def get_queryset(cls, queryset, user):
        queryset = cls.filter_queryset(queryset)
        if isinstance(user, ResolveInfo):
            user = user.context.user
        if settings.ROW_SECURITY and user.is_anonymous:
            return queryset.filter(id=-1)
        if settings.ROW_SECURITY:
            pass
        return queryset

    class Meta:
        db_table = 'tblCalculationRulesDetails'