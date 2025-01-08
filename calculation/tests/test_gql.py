import base64
import json
from dataclasses import dataclass

from core.models import User, filter_validity
from core.models.openimis_graphql_test_case import openIMISGraphQLTestCase
from core.test_helpers import create_test_interactive_user
from django.conf import settings
from graphene_django.utils.testing import GraphQLTestCase
from graphql_jwt.shortcuts import get_token
from location.models import Location
from location.test_helpers import create_test_location, assign_user_districts
from rest_framework import status
from insuree.test_helpers import create_test_insuree
from policy.test_helpers import create_test_policy
from contribution.models import Premium, PayTypeChoices
from calculation.calculation_rule import ContributionValuationRule
from location.test_helpers import create_test_location, create_test_health_facility, create_test_village
from payer.models import Payer
from product.models import Product
import datetime

# from openIMIS import schema


@dataclass
class DummyContext:
    """ Just because we need a context to generate. """
    user: User


class CalcualtionGQLTestCase(openIMISGraphQLTestCase):
    GRAPHQL_URL = f'/{settings.SITE_ROOT()}graphql'
    # This is required by some version of graphene but is never used. It should be set to the schema but the import
    # is shown as an error in the IDE, so leaving it as True.
    GRAPHQL_SCHEMA = True
    admin_user = None
    ca_user = None
    ca_token = None
    test_village = None
    test_insuree = None
    policy = None
    product = None
    payer = None
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin_user = create_test_interactive_user(username="testLocationAdmin")
        cls.admin_token = get_token(cls.admin_user, DummyContext(user=cls.admin_user))

    def test_by_class_name(self):
      
        response = self.query(
            '''
        query{
            calculationRulesByClassName(className: "ContractDetails"){
                calculationRules{
                    calculationClassName, status, description, uuid, classParam, dateValidFrom, dateValidTo, fromTo, type, subType
                }
                
                
            }
        }
            ''',
            headers={"HTTP_AUTHORIZATION": f"Bearer {self.admin_token}"},
        )

        content = json.loads(response.content)
        self.assertTrue('data' in content and 'calculationRulesByClassName' in content['data'])
        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)
        
    def test_simple(self):
      
        response = self.query(
            '''
        query{
            calculationRules{
                calculationRules{
                    calculationClassName, status, description, uuid, classParam, dateValidFrom, dateValidTo, fromTo, type, subType
                }
                
            }
        }
            ''',
            headers={"HTTP_AUTHORIZATION": f"Bearer {self.admin_token}"},
        )

        content = json.loads(response.content)
        self.assertTrue('data' in content and 'calculationRules' in content['data'])
        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)

        # Add some more asserts if you like
        
    def test_account_payable(self):
      
        response = self.query(
            '''

            query{
            calculationRules(calcruleType: "account_payable")
            {
                calculationRules{uuid, calculationClassName}
            }
            }
            ''',
            headers={"HTTP_AUTHORIZATION": f"Bearer {self.admin_token}"},
        )

        content = json.loads(response.content)
        self.assertTrue('data' in content and 'calculationRules' in content['data'])

        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)

        # Add some more asserts if you like


    def test_account_receivable(self):
      
        response = self.query(
            '''

            query{
            calculationRules(calcruleType: "account_receivable")
            {
                calculationRules{uuid, calculationClassName}
            }
            }
            ''',
            headers={"HTTP_AUTHORIZATION": f"Bearer {self.admin_token}"},
        )

        content = json.loads(response.content)
        self.assertTrue('data' in content and 'calculationRules' in content['data'])
        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)

        # Add some more asserts if you like

    def test_uuid(self):
      
        response = self.query(
            f'''

            query{{
            calculationRules(calculation: "{ContributionValuationRule.uuid}")
            {{
                calculationRules{{uuid, calculationClassName}}
            }}
            }}
            ''',
            headers={"HTTP_AUTHORIZATION": f"Bearer {self.admin_token}"},
        )

        content = json.loads(response.content)
        self.assertTrue('data' in content and 'calculationRules' in content['data'])
        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)

        # Add some more asserts if you like
                
                
    def test_params(self):
      
        response = self.query(
            '''
        query{
             linkedClass{
                 linkedClasses
                
            }
        }
            ''',
            headers={"HTTP_AUTHORIZATION": f"Bearer {self.admin_token}"},
        )

        content = json.loads(response.content)
        self.assertTrue('data' in content and 'linkedClass' in content['data'])
        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)

        # Add some more asserts if you like