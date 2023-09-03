import pytest
from unittest.mock import Mock, patch
from typing import Any

import pdb

from order_processor.main import process_order
# test class for module level functions
# could probably make it one, since the functions differ very little
# but what i dont want is to import stuff, i want to simpy copy
# maybe i can put the functionality outside and just inject it

mock_client = Mock()
def mock_get_item(*args, **kwargs):
    if kwargs == {
            "TableName":'order_table',
            "Key":{
                'string': {
                    'N': 'order_id_1'
                }
            },
            "ProjectionExpression": 'id, cartItems'    
        }:
            
            result = {
                'Item': {
                    'id': {
                        'N': 'order_id_1'
                    },
                    'cartItems': {
                        'L': [
                            {
                                'M': {
                                    'id': {
                                        'N': 'item_id_1'
                                    },
                                    'orderedQuantity': {
                                        'N': '6'
                                    }
                                }
                            },
                            {
                                'M': {
                                    'id': {
                                        'N': 'item_id_2'
                                    },
                                    'orderedQuantity': {
                                        'N': '2'
                                    }
                                }
                            }
                        ]
                    }
                }
            }

            return result
    
    if kwargs == {
            "TableName":'order_table',
            "Key":{
                'string': {
                    'N': 'order_id_2'
                }
            },
            "ProjectionExpression": 'id, cartItems'    
        }:
            
            result = {
                'Item': {
                    'id': {
                        'N': 'order_id_2'
                    },
                    'cartItems': {
                        'L': [
                            {
                                'M': {
                                    'id': {
                                        'N': 'item_id_1'
                                    },
                                    'orderedQuantity': {
                                        'N': '6'
                                    }
                                }
                            },
                            {
                                'M': {
                                    'id': {
                                        'N': 'item_id_2'
                                    },
                                    'orderedQuantity': {
                                        'N': '6'
                                    }
                                }
                            }
                        ]
                    }
                }
            }

            return result
    
    if kwargs == {
            "TableName":'items_table',
            "Key":{
                'string': {
                    'N': 'item_id_1'
                }
            },
            "ProjectionExpression": 'id, availableQuantity'    
        }:
            
            result = {
                'Item': {
                    'id': {
                        "N": 'item_id_1'
                    },
                    'availableQuantity': {
                        'N': '10'
                    }
                }
            }
            
            return result
    
    if kwargs == {
            "TableName":'items_table',
            "Key":{
                'string': {
                    'N': 'item_id_2'
                }
            },
            "ProjectionExpression": 'id, availableQuantity'    
        }:
            
            result = {
                'Item': {
                    'id': {
                        "N": 'item_id_2'
                    },
                    'availableQuantity': {
                        'N': '5'
                    }
                }
            }
            
            return result

mock_client.get_item.side_effect = mock_get_item

class TestModule:
    # python -m pytest --pdb C:\Users\adams\projects\order_queue_aws\order_processor\tests\test_order_processor\test_main.py::TestModule::test_process_order
    # SETUP TEARDOWN FIXTURE
    # this sets the and cleans up the tested environment
    @pytest.fixture
    def a_validate_side_effect(self) -> bool:
        def validate(tc_key, *args,**kwargs):
            if not tc_key:
                return True
            else:
                raise ValueError('Test case is missing side effect validation')

        return validate

    @pytest.fixture
    def a_setup_teardown(self):
        def setup_teardown(tc_key, *args,**kwargs):
            if not tc_key:
                yield None
            else:
                raise ValueError('Test case is missing setup-teardown')

        return setup_teardown

    a_test_input_1 = {
        # positional arguments tuple
        'args': (
            'order_id_1',
            mock_client
        ),
        'kwargs': {

        }
    }
    a_expected_output_1 = (
        'Done'
    )
    a_test_input_2 = {
        # positional arguments tuple
        'args': (
            'order_id_2',
            mock_client
        ),
        'kwargs': {

        }
    }
    a_expected_output_2 = (
        'Failed'
    )
    
    a_side_effect_key_1 = None
    a_setup_teardown_key_1 = None

    @pytest.mark.parametrize(
        "test_input,expected_output,se_key,st_key",
        [
            (
                a_test_input_1, 
                a_expected_output_1,
                a_side_effect_key_1,
                a_setup_teardown_key_1
            ),
            (
                a_test_input_2, 
                a_expected_output_2,
                a_side_effect_key_1,
                a_setup_teardown_key_1
            )
        ]
    )
    def test_process_order(
        self, 
        test_input, 
        expected_output, 
        se_key,
        st_key,
        a_validate_side_effect,
        a_setup_teardown
    ):
        # setup environment
        st = a_setup_teardown(st_key)
        next(st)

        # get the result
        result = process_order(
            *test_input['args'],
            **test_input['kwargs']
        )
        
        # testing result
        if len(expected_output) == 1:
            assert result == expected_output[0]
        elif len(expected_output) > 1:
            assert result == expected_output
        else:
            raise ValueError('Empty expected output')
        
        # testing the environment changes
        assert a_validate_side_effect(se_key)

        # assert calls for updae_item
        test_input['args'][1].update_item.assert_any_call(
            TableName='items_table',
            Key={
                'string': {
                    'N': 'item_id_1'
                }
            },
            UpdateExpression="SET availabeQuantity = :av",
            ExpressionAttributeValues={
                ':av': {
                    'N': '4'
                }
            },
            ReturnValues='NONE'
        )
        test_input['args'][1].update_item.assert_any_call(
            TableName='items_table',
            Key={
                'string': {
                    'N': 'item_id_2'
                }
            },
            UpdateExpression="SET availabeQuantity = :av",
            ExpressionAttributeValues={
                ':av': {
                    'N': '3'
                }
            },
            ReturnValues='NONE'
        )

        # environment cleanup
        try:
            next(st)
        except StopIteration:
            pass
        else:
            ValueError('unexpected after teardown state')