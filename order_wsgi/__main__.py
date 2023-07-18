from collections.abc import Callable, Iterable, Mapping
from datetime import time
from typing import Any
from wsgiref.simple_server import make_server
import threading

status_dict = {}  # Module-level dictionary
lock = threading.Lock()  # Lock object

# t1 continuously checks value
def thread1_func(key: str) -> dict:
    done: bool
    status: str
    with lock:
        done = status_dict[key]['done']
        status = status_dict[key]['done']
    return done, status

# t2 modifies value
def thread2_func(key: str, new_status: str) -> None:
    with lock:
        status_dict[key]['done'] = True
        status_dict[key]['status'] = new_status 

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

def run_server():
    """Run the WSGI server"""
    server = make_server('localhost', 8000, handle_request)
    server.serve_forever()

