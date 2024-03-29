# Generated by Django 3.2.16 on 2023-01-26 09:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0003_add_calculation_roles_for_admin'),
        ('contribution_plan', '0009_contributionplan_roles_for_admin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calculationrulesdetails',
            name='calculation_rules',
        ),
        migrations.RemoveField(
            model_name='calculationrulesdetails',
            name='user_created',
        ),
        migrations.RemoveField(
            model_name='calculationrulesdetails',
            name='user_updated',
        ),
        migrations.RemoveField(
            model_name='historicalcalculationrules',
            name='history_user',
        ),
        migrations.RemoveField(
            model_name='historicalcalculationrules',
            name='user_created',
        ),
        migrations.RemoveField(
            model_name='historicalcalculationrules',
            name='user_updated',
        ),
        migrations.RemoveField(
            model_name='historicalcalculationrulesdetails',
            name='calculation_rules',
        ),
        migrations.RemoveField(
            model_name='historicalcalculationrulesdetails',
            name='history_user',
        ),
        migrations.RemoveField(
            model_name='historicalcalculationrulesdetails',
            name='user_created',
        ),
        migrations.RemoveField(
            model_name='historicalcalculationrulesdetails',
            name='user_updated',
        ),
        migrations.DeleteModel(
            name='CalculationRules',
        ),
        migrations.DeleteModel(
            name='CalculationRulesDetails',
        ),
        migrations.DeleteModel(
            name='HistoricalCalculationRules',
        ),
        migrations.DeleteModel(
            name='HistoricalCalculationRulesDetails',
        ),
    ]
