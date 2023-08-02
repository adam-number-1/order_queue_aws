from typing import Generator, Optional

import pdb
import socket
import threading

redis_lock = threading.Lock()
dict_lock = threading.Lock()

class OrderThread(threading.Thread):
    def __init__(self, client_socket, client_address):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address

    def run(self):
        # get the data to parse the http request
        self.request = self.get_data()

    def get_data(self) -> bytes:
        """Return the data of request.
        
        :param socket: a client socket to read bytes from.
        :returns: bytes of the request from the socket.
        """
        pdb.set_trace()
        data: bytes = b''
        content_length: Optional[int] = None
        
        while True:
            # parsing the request line
            # Method SP Request-URI SP HTTP-Version CRLF
            # if it ends with \r\n sequence it will split to [s, '']
            # if just \r\n, it results in two empty bytestrings
            # empty data would end up being empty data
            # bytestring having no CRLF sequence will be just the bytestring
            if content_length == 0:
                return data
            
            if content_length:
                new_chunk: bytes = self.client_socket.recv(4096)
                content_length -= len(new_chunk)
                data += new_chunk

            data: bytes = data + self.client_socket.recv(4096)
            chunks: list[bytes] = data.split(b'\r\n\r\n')
            if not chunks[0]:
                return data
            
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
            except ValueError:
                # wont be able to guess the length of the payload
                # so i return it
                return data
            
            body: bytes = b'\r\n\r\n'.join(body_parts)
            content_length -= len(body)



    def read_request(self) -> str:
        # Read data from the client socket
        request_data = b''
        while True:
            data = self.client_socket.recv(4096)
            print(data)
            request_data += data

        # need some parsing here and stuff


    def extract_http_properties(request_data) -> dict: ...


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
    main()
