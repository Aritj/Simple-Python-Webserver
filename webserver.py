import socket
import urllib.parse
import json

class HttpFields:
    QUERY_DELIMITER = '?'
    QUERY_KVP_DELIMITER = '&'
    QUERY_KV_DELIMITER = '='
    FILENAME_DELIMITER = '.'
    ROUTE_DELIMITER = '/'

class HttpServer:
    DEFAULT_HOST: str = '0.0.0.0'
    DEFAULT_PORT: int = 8000

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
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
        buffer_size: int = 1024
        
        try:
            request = client_connection.recv(buffer_size).decode()
            response = self.process_request(request)
            client_connection.sendall(response.encode())
        finally:
            client_connection.close()

    def process_request(self, request: str) -> str:
        headers: list[str] = request.split('\n')
        http_request_method, url, http_version = headers[0].split()

        if http_request_method not in ['GET']:
            # TODO: Handle HTTP request methods, e.g. POST, PUT
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
            return self.format_http_response(501, f"{http_request_method} not implemented")

        try:
            route, query_dict =  (url, {}) \
                if url.find(HttpFields.QUERY_DELIMITER) == -1 \
                else self.parse_query_string(url)
        except:
            return self.format_http_response(500, "Unable to parse query string.")
        
        if query_dict:
            # TODO: implement custom query string handling
            return json.dumps(query_dict, indent=4)

        try:
            with open(f'www/{self.parse_route(route)}', "r") as file:
                return self.format_http_response(200, file.read())
        except FileNotFoundError:
            return self.format_http_response(404, "File Not Found")

    @staticmethod
    def parse_query_string(url_string: str) -> (str, dict[str, str]):
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
        # change "/" to "index.html"
        route = route if len(route[1:]) else 'index.html'
        
        # assume any route without file extension is ".html", else use provided file extension.
        return route + ".html" \
            if route.find(HttpFields.FILENAME_DELIMITER) == -1 \
            else route
        
    @staticmethod
    def format_http_response(http_status_code: int, html: str) -> str:
        _VERSION = 'HTTP/1.0'
        # TODO: implement missing http_status_codes
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
        match http_status_code:
            case 200:
                return f'{_VERSION} 200 OK\n\n{html}'
            case 400:
                return f'{_VERSION} 400 BAD REQUEST\n\n{html}'
            case 404:
                return f'{_VERSION} 404 NOT FOUND\n\n{html}'
            case 500:
                return f'{_VERSION} 500 INTERNAL SERVER ERROR\n\n{html}'
            case 501:
                return f'{_VERSION} 501 NOT IMPLEMENTED\n\n{html}'

    
if __name__ == '__main__':
    HttpServer('0.0.0.0', 8080).start()