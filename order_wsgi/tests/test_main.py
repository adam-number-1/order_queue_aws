from order_wsgi.main import OrderThread

import pytest

class MockSocket:
    def __init__(self, byte_list):
        self.byte_list = byte_list
        self.i = 0

    def recv(self,*args,**kwargs):
        if self.i == len(self.byte_list):
            return b''
        val = self.byte_list[self.i]
        self.i += 1
        return val


# testing instance methods, instance creations etc
class TestOrderThread:
    # python -m pytest tests\test_main.py::TestOrderThread::test_get_data
    @pytest.fixture
    def setup_teardown(self):
        # setup
        yield
        # teardown
    a_test_input_1 = {
        # positional arguments tuple
        'args': (
            
        ),
        'kwargs': {

        }
    }
    a_expected_output_1 = (
        (
            b'ab\r\nContent-Length: 9\r\n\r\n{"a":"b"}',
        )
    )
    a_class_1 = OrderThread
    a_init_1 = {
        # positional arguments tuple
        'args': (
            MockSocket(
                [
                    b'a',
                    b'b\r',
                    b'\nCon',
                    b'tent-Length:',
                    b' 9\r\n',
                    b'\r\n{',
                    b'"a":"b"}',
                ]
            ),
            'whatever`'
        ),
        'kwargs': {

        }   
    }
    a_attrs_1 = {
        
    }
    a_test_input_2 = {
        # positional arguments tuple
        'args': (
            
        ),
        'kwargs': {

        }
    }
    a_expected_output_2 = (
        (
            b'ab\r\nContent-Lengh: 9\r\n\r\n{',
        )
    )
    a_class_2 = OrderThread
    a_init_2 = {
        # positional arguments tuple
        'args': (
            MockSocket(
                [
                    b'a',
                    b'b\r',
                    b'\nCon',
                    b'tent-Lengh:',
                    b' 9\r\n',
                    b'\r\n{',
                    b'"a":"b"}',
                ]
            ),
            'whatever`'
        ),
        'kwargs': {

        }   
    }
    a_attrs_2 = {
        
    }
    @pytest.mark.parametrize(
        "test_input,expected_output,class_,init,attrs",
        [
            (a_test_input_1, a_expected_output_1, a_class_1, a_init_1, a_attrs_1),
            (a_test_input_2, a_expected_output_2, a_class_2, a_init_2, a_attrs_2)
        ]
    )
    def test_get_data(self, test_input, expected_output, class_, init, attrs):
        obj_ = class_(
            *init['args'],
            **init['kwargs']
        )

        obj_.start()
        obj_.join()
        result = obj_.request
        
        if len(expected_output) == 1:
            assert result == expected_output[0]
        elif len(expected_output) > 1:
            assert result == expected_output
        else:
            raise ValueError('Empty expected output')
        
        for attr_name, attr_val in attrs.items():
            obj_.__getattribute__(attr_name) == attr_val
