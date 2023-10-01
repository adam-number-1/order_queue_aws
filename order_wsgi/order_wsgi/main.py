from datetime import datetime
from time import sleep
from typing import Generator, Optional

import boto3
import json
import socket
import threading

from order_wsgi.redis_con import redis_connection

dynamo_client = boto3.client('dynamodb')

# cd order_wsgi      
# python -m order_wsgi.main
status_dict = {}

# i wil reuse one connection instead of making many
redis_lock = threading.Lock()

# lock for redis queue
queue_lock = threading.Lock()

# this will keep the state fo responses
dict_lock = threading.Lock()

# this will keep the state fo responses
dynamo_lock = threading.Lock()

def await_status(order_id: int):
    status = None
    while not status:
        print(f'retrieving status for {order_id}')
        sleep(2)
        with dict_lock:
            status = status_dict.get(order_id)
    return status

def get_id() -> int:
    current_timestamp = int(datetime.now().timestamp()*1000)
    print(f'new id requested {current_timestamp}')
    return current_timestamp

def get_verb(headers: bytes) -> bytes:
    result = []
    print(headers)
    for l in headers:
        if l == 32:
            break
        result.append(l)
    return bytes(result)

def insert_order(order_id: int, order_obj: dict) -> None:

    cart_items: dict[str, list] = {
        'L': []
    }
    for cart_item in order_obj['cartItems']:
        cart_items['L'].append(
            {
                'M': {
                    'id': {
                        'N': str(cart_item['id'])
                    },
                    'orderedQuantity': {
                        'N': str(cart_item['orderedQuantity'])
                    }
                }
            }
        )

    with dynamo_lock:
        # here needs to be put item in the dynamodb
        print(f'order {order_id} goes to db')
        _ = dynamo_client.put_item(
            TableName='orders_table',
            Item={
                'id': {
                    'N': str(order_id)
                },
                'cartItems': cart_items
            }
        )
    

def queue_order(order_id):
    with queue_lock:
        print(f'putting order {order_id} to redis queue')
        redis_connection.lpush('order_queue', order_id)

def update_status(order_update_obj: bytes):
    print(order_update_obj)
    update_dict = json.loads(order_update_obj)
    update_dict['id'] = int(update_dict['id'])
    with dict_lock:
        print(f'updating status of {update_dict}')
        status_dict[update_dict['id']] = update_dict['status']

class OrderThread(threading.Thread):
    def __init__(self, client_socket, client_address):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address

    def run(self):
        # get the data to parse the http request
        headers, payload = self.get_data()
        print(headers, payload)
        verb = get_verb(headers)
        if verb == b'POST': 
            order_id = get_id()
            insert_order(order_id, payload)
            queue_order(order_id)
            status = await_status(order_id)

            if status == 'Done':
                self.client_socket.sendall(b'HTTP/1.1 200\r\n')

            elif status == 'Failed':
                self.client_socket.sendall(b'HTTP/1.1 400\r\n')

            else:
                self.client_socket.sendall(b'HTTP/1.1 500\r\n')

        elif verb == b'PUT':
            update_status(payload)
            self.client_socket.sendall(b'HTTP/1.1 200\r\n')
        self.client_socket.close()          

    def get_data(self) -> bytes:
        """Return the data of request.
        
        :param socket: a client socket to read bytes from.
        :returns: bytes of the request from the socket.
        """
        data: bytes = b''
        headers: bytes
        payload: bytes
        content_length: Optional[int] = None
        
        while True:
            # parsing the request line
            # Method SP Request-URI SP HTTP-Version CRLF
            # if it ends with \r\n sequence it will split to [s, '']
            # if just \r\n, it results in two empty bytestrings
            # empty data would end up being empty data
            # bytestring having no CRLF sequence will be just the bytestring
            if content_length == 0:
                self.request = (headers, payload)
                return headers, payload
            
            if content_length:
                new_chunk: bytes = self.client_socket.recv(4096)
                content_length -= len(new_chunk)
                payload += new_chunk
                continue

            data: bytes = data + self.client_socket.recv(4096)
            chunks: list[bytes] = data.split(b'\r\n\r\n')
            if not chunks[0]:
                self.request = (headers, payload)
                return data, b''
            
            if len(chunks) == 1:
                # this means there was no CRLFCRLF sequence yet
                continue

            headers, *body_parts = chunks
            # Content-Length: 26012
            # potential Vaue error on unpack
            try:
                # expect only two chunks after splitting by content length
                _, post_headers = headers.split(b'Content-Length: ') 
                # i expect the bye length to be on left and whatever chunks on right
                byte_length, *_ = post_headers.split(b'\r\n')
                # potential value error
                content_length = int(byte_length)
                payload: bytes = b'\r\n\r\n'.join(body_parts)
            except ValueError:
                # wont be able to guess the length of the payload
                # so i return it
                self.request = (headers, payload)
                return headers, payload
            
            
            content_length -= len(payload)

def main():
    host = '127.0.0.1'
    port = 8080

    # Create a socket and bind it to the specified host and port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))

    # Start listening for incoming connections
    server_socket.listen(3)
    print(f"Server listening on {host}:{port}")

    while True:
        # Accept a connection from a client
        client_socket, client_address = server_socket.accept()
        print(f"Connected to {client_address}")

        # here is an alternate threaded approach
        new_order_thread = OrderThread(client_socket, client_address)
        new_order_thread.start()

if __name__ == "__main__":
    dynamo_client = boto3.client('dynamodb')
    main()

