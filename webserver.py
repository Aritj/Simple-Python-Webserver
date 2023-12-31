import socket

class HttpFields:
    QUERY = "?"
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
        http_request_type, page, http_version = headers[0].split()

        if http_request_type not in ['GET']:
            pass

        if HttpFields.QUERY in page:
            query = page.split(HttpFields.QUERY)[1]
            print(f'Query: {query}')

        filename, file_extension = self.extract_page_info(page)
        
        print(f'html/{filename}{HttpFields.DELIMITER}{file_extension}')
        try:
            with open(f'html/{filename}{HttpFields.DELIMITER}{file_extension}', "r") as file:
                return 'HTTP/1.0 200 OK\n\n' + file.read()
        except FileNotFoundError:
            return f'HTTP/1.0 404 NOT FOUND\n\nFile Not Found'

    @staticmethod
    def extract_page_info(page: str) -> (str, str):
        page = page.removeprefix('/')
        filename, extension = page.split(HttpFields.DELIMITER) \
            if HttpFields.DELIMITER in page \
            else (page, "html")
        
        if not filename:
            filename = "index"

        return filename, extension
    
if __name__ == '__main__':
    HttpServer('0.0.0.0', 8080).start()