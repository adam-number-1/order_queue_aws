from collections.abc import Callable, Iterable, Mapping
from datetime import time
from typing import Any, Optional
from wsgiref.simple_server import make_server

import json
import threading

import redis

status_dict = {}  # Module-level dictionary
lock = threading.Lock()  # Lock object
redis_lock = threading.Lock()

client = redis.Redis(host='', port=9999, db=0)


# t1 continuously checks value
def read_result(key: str) -> Optional[str]:
    status: str
    with lock:
        status = status_dict.get(key)
    return status

# t2 modifies value
def write_result(key: str, result_code: str) -> None:
    with lock:
        status_dict[key] = result_code 

def post_order(order: dict) -> str:
    """Saves the order in the redis database.
    
    :param order: dictionary representation of the order.
    :returns: the order id
    """

    # can be other way of setting order id, like uuid
    result: str = order['id']

    # threadsafe storing to redis
    order_key: str = f'order:{result}'
    with redis_lock:
        client.json().set(order_key, '$', order_key)

    return result

def schedule_order(order_id: str) -> None:
    """Schedule order to redis queue"""
    # should probably also be thread safe


def wait_for_completion(order_id: str) -> str:
    """Blocks the execution thread until the order is processed.
    
    :param order_id: id of the order.
    :returns: the status of the completion
    """
    time.sleep(0.5)
    status: Optional[str] = read_result(order_id)

    # should add some timeout
    while not status:
        time.sleep(0.05)
        status = read_result(order_id)
    
    return status
        

def handle_request(environ, start_response):
    """Handle each request in a separate thread"""

    # lets just see first, if i will be able to differentiate between verbs
    # and read the payloads

    # put will create new order passing order payload
    # order goes to db
    # new thread starts
    # order id is sent to redis queue
    # thread waits for processing of the order
    # then return response

    # patch will find the order in the order dictionary and will modify the
    # thread atributes

    # status = '200 OK'
    # headers = [('Content-type', 'text/html')]
    # response = b"Hello, World!"

    # start_response(status, headers)
    # return [response]


def simple_app(environ, start_response):
    # Get the HTTP method (verb)
    method: str = environ['REQUEST_METHOD']
    content_length: int = int(environ.get('CONTENT_LENGTH', 0))
    payload: str = environ['wsgi.input'].read(content_length).decode('utf-8')

    # posting the order
    if method == 'POST':
        # parsing the order
        order: dict = json.loads(payload)

        # posting the order to db - order id is created after 
        order_id: str = post_order(order)
        schedule_order(order_id)
        status = wait_for_completion(order_id)

        # Response data
        headers = [('Content-type', 'text/plain')]
        response_body = order_id.encode(encoding='utf-8')

        # Start the response
        start_response(status, headers)

        # Return the response body
        return [response_body]
    
    # receiving a request from the que processor about the status of the
    # order process completion
    elif method == 'PATCH':
        order_id: str = payload['id']
        process_result: str = payload['process_result']

        write_result(
            order,
            process_result
        )

        # Response data
        headers = [('Content-type', 'text/plain')]

        # Start the response
        start_response("200", headers)

        # Return the response body
        return []

if __name__ == '__main__':
    host = 'localhost'
    port = 8000
    with make_server(host, port, simple_app) as httpd:
        print(f"Serving on {host}:{port}...")
        httpd.serve_forever()

