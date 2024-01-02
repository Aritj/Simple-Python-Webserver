import socket
import urllib.parse
import json

class HttpStatus:
    OK: int = 200
    BAD_REQUEST: int = 400
    NOT_FOUND: int = 404
    INTERNAL_SERVER_ERROR: int = 500
    NOT_IMPLEMENTED = 501

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

class HttpFields:
    QUERY_DELIMITER = '?'
    QUERY_KV_DELIMITER = '='
    QUERY_KVP_DELIMITER = '&'
    FILENAME_DELIMITER = '.'
    ROUTE_DELIMITER = '/'

class HttpServer:
    def __init__(self, host: str = '0.0.0.0', port: int = 8000) -> None:
        self.server_host = host
        self.server_port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
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

        try:
            route, query_dict = self.parse_query_string(url)
        except:
            return HttpStatus.create_status_message(HttpStatus.INTERNAL_SERVER_ERROR, "Unable to parse query string.")
        
        if query_dict:
            return json.dumps(query_dict, indent=4)

        try:
            with open(f'www/{self.parse_route(route)}', "r") as file:
                return HttpStatus.create_status_message(HttpStatus.OK, file.read())
        except FileNotFoundError:
            return HttpStatus.create_status_message(HttpStatus.NOT_FOUND, "File Not Found")

    @staticmethod
    def parse_query_string(url_string: str) -> (str, dict[str, str]):
        if url_string.find(HttpFields.QUERY_DELIMITER) == -1:
            return url_string, {}

        route_index: int = 0
        query_string: str = url_string[url_string.find(HttpFields.QUERY_DELIMITER) + 1:]
        pairs: list[str] = query_string.split(HttpFields.QUERY_KVP_DELIMITER)

        query_dict: dict[str, str] = {}
        for pair in pairs:
            key, value = pair.split('=')
            query_dict[urllib.parse.unquote(key)] = urllib.parse.unquote(value)

        return url_string.split(HttpFields.QUERY_DELIMITER)[route_index], query_dict
    
    @staticmethod
    def parse_route(route: str) -> (str, list[str], str):
        if route == "/":
            route = "index.html"

        has_file_extension = route.find(HttpFields.FILENAME_DELIMITER) >= 0
        
        # assume any route without file extension is ".html", else use provided file extension.
        return route \
            if has_file_extension \
            else route + ".html"

    
if __name__ == '__main__':
    HttpServer('0.0.0.0', 8080).start()