import socket

from urllib.parse import urlparse, parse_qs, ParseResult
from typing import Callable, Type, ClassVar, Dict

class HttpStatus:
    OK: int = 200
    BAD_REQUEST: int = 400
    NOT_FOUND: int = 404
    INTERNAL_SERVER_ERROR: int = 500
    NOT_IMPLEMENTED = 501

    @staticmethod
    def create_status_message(http_status_code: int, message: str):
        http_version = 'HTTP/1.0'
        # TODO: implement missing http_status_codes
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

        match http_status_code:
            case 200: return f'{http_version} 200 OK\n\n{message}'
            case 400: return f'{http_version} 400 BAD REQUEST\n\n{message}'
            case 404: return f'{http_version} 404 NOT FOUND\n\n{message}'
            case 500: return f'{http_version} 500 INTERNAL SERVER ERROR\n\n{message}'
            case 501: return f'{http_version} 501 NOT IMPLEMENTED\n\n{message}'
            case _: return f'{http_version} {http_status_code} UNKNOWN STATUS\n\n{message}'

class HttpFields:
    QUERY_DELIMITER: str = '?'
    QUERY_KV_DELIMITER: str = '='
    QUERY_KVP_DELIMITER: str = '&'
    FILENAME_DELIMITER: str = '.'
    ROUTE_DELIMITER: str = '/'

class HttpServer:
    route_registry: ClassVar[Dict[str, Callable]] = {}

    def __init__(self, host: str = '0.0.0.0', port: int = 8000) -> None:
        self.server_host = host
        self.server_port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @classmethod
    def route(cls: Type['HttpServer'], path: str) -> Callable[[Callable[..., str]], Callable[..., str]]:
        def decorator(func: Callable[..., str]) -> Callable[..., str]:
            cls.route_registry[path] = func
            return func
        return decorator
    
    def start(self) -> None:
        try:
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.server_host, self.server_port))
            self.server_socket.listen(1)
            
            while True:
                client_connection, _ = self.server_socket.accept()
                self.handle_client(client_connection)
        finally:
            self.server_socket.close()

    def handle_client(self, client_connection: socket.socket) -> None:
        buffer_size: int = 1024 # TODO: optimize this value
        
        try:
            request = client_connection.recv(buffer_size).decode()
            response = self.process_request(request)
            client_connection.sendall(response.encode())
        finally:
            client_connection.close()

    def process_request(self, request: str) -> str:
        headers: list[str] = request.split('\n')
        http_request_method, url, _ = headers[0].split() # "GET /index.html HTTP/1.1"

        if http_request_method not in ['GET']:
            # TODO: Handle HTTP request methods, e.g. POST, PUT https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
            return HttpStatus.create_status_message(HttpStatus.NOT_IMPLEMENTED, f"{http_request_method} not implemented")

        url: ParseResult = urlparse(url)
        qs: dict[str, list[str]] = parse_qs(url.query)

        if url.path in self.route_registry:
            try:
                return self.route_registry[url.path](qs) # app function wants query string
            except:
                return self.route_registry[url.path]() # app funtion doesn't want query string
        
        return HttpStatus.create_status_message(HttpStatus.NOT_FOUND, "Route Not Found")

def render_template(filename: str) -> str:
    try:
        with open(f'www/{filename}', "r") as file:
            return HttpStatus.create_status_message(HttpStatus.OK, file.read())
    except FileNotFoundError:
        return HttpStatus.create_status_message(HttpStatus.NOT_FOUND, "File Not Found")