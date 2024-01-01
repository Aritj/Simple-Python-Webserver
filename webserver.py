import socket
import urllib.parse

class HttpFields:
    QUERY = "?"
    QUERY_DELIMITER = "&"
    DELIMITER = "."

class HttpServer:
    DEFAULT_HOST = '0.0.0.0'
    DEFAULT_PORT = 8000

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.server_host = host
        self.server_port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def start(self):
        try:
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.server_host, self.server_port))
            self.server_socket.listen(1)
            
            while True:
                client_connection, _ = self.server_socket.accept()
                self.handle_client(client_connection)
        finally:
            self.server_socket.close()

    def handle_client(self, client_connection: socket.socket):
        try:
            request = client_connection.recv(1024).decode()
            response = self.process_request(request)
            client_connection.sendall(response.encode())
        finally:
            client_connection.close()

    def process_request(self, request: str):
        headers = request.split('\n')
        http_request_method, page, http_version = headers[0].split()

        if http_request_method not in ['GET']:
            # TODO: Handle HTTP request methods, e.g. POST, PUT
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
            return self.format_http_response(501, f"{http_request_method} not implemented")

        query_dict = {} if page.find(HttpFields.QUERY) == -1 else self.parse_query_string(page)
        
        if query_dict:
            # TODO: implement custom query string handling
            print(query_dict)

        filename, file_extension = self.extract_page_info(page)
        
        try:
            with open(f'html/{filename}{HttpFields.DELIMITER}{file_extension}', "r") as file:
                return self.format_http_response(200, file.read())
        except FileNotFoundError:
            return self.format_http_response(404, "File Not Found")

    @staticmethod
    def parse_query_string(url_string: str) -> dict[str, str]:
        query_string = url_string[url_string.find(HttpFields.QUERY) + 1:]
        pairs = query_string.split(HttpFields.QUERY_DELIMITER)

        query_dict = {}
        for pair in pairs:
            key, value = pair.split('=')
            query_dict[urllib.parse.unquote(key)] = urllib.parse.unquote(value)

        return query_dict
    
    @staticmethod
    def extract_page_info(page: str) -> (str, str):
        page = page.removeprefix('/')
        filename, extension = page.split(HttpFields.DELIMITER) \
            if HttpFields.DELIMITER in page \
            else (page, "html")
        
        if not filename:
            filename = "index"

        return filename, extension
    
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