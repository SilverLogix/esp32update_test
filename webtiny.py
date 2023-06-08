import _thread
import usocket as socket
import gc


class WebServer:
    def __init__(self, host='0.0.0.0', port=80):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.thread = None
        self.lock = _thread.allocate_lock()

    def handle_client(self, client_socket):
        # Receive data from the client
        request = client_socket.recv(1024)
        print("Received request:\n", request)

        # Parse the request
        request_lines = request.split(b'\r\n')
        if len(request_lines) > 0:
            # Extract the command from the request
            command_line = request_lines[0].decode()
            command = command_line.split()[1]

            # Set the default style and content
            http = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n'
            head = '<html><head><title>ESP Web Server</title><meta name="viewport" content="width=device-width, initial-scale=1"><link rel="icon" href="data:,">'
            style = '<style>body { background-color: #8b0000; }</style></head>'
            content = '<h1>404 Not Found</h1>'

            # Handle different commands
            if command == '/':
                style = '<style>body { background-color: #add8e6; }</style></head>'
                content = "<h1>Hello, World!</h1>"

            elif command == '/about':
                style = '<style>body { background-color: #ffffff; }</style></head>'
                content = "<h1>About page</h1>"
                print("\nABOUT\n")

            elif command == '/?reset':
                from machine import reset
                reset()

            # Build the response
            import html
            response = f"{html.http}{html.title_01}{html.style}{html.content}"

            # Send the response back to the client
            client_socket.send(response.encode())

        # Close the client socket
        client_socket.close()

    def handle_client_wrapper(self, client_socket):
        # Handle the client request in a separate thread
        try:
            self.handle_client(client_socket)
        except Exception as e:
            print("Error handling client request:", e)
        finally:
            # Perform garbage collection after handling the client request
            gc.collect()

    def start(self):
        try:
            # Create the server socket
            self.server_socket = socket.socket()

            # Bind the socket to the host and port
            self.server_socket.bind((self.host, self.port))
            print("Server listening on", self.host, "port", self.port, "\n")

            # Start listening for client connections
            self.server_socket.listen(5)

            self.running = True
            _thread.stack_size(8192)
            self.thread = _thread.start_new_thread(self.run_server, ())
            print("WEB Stack:", _thread.stack_size())
        except Exception as e:
            print("Error: Unable to start the server.")
            print(e)

    def run_server(self):
        while self.running:
            # Accept a client connection
            client_socket, addr = self.server_socket.accept()
            print("Client connected from", addr)

            # Acquire the lock before handling the client request
            self.lock.acquire()

            # Start a new thread to handle the client request
            try:
                _thread.start_new_thread(self.handle_client_wrapper, (client_socket,))
            except OSError as e:
                print(e)

            # Release the lock after starting the thread
            self.lock.release()

    def stop(self):
        self.running = False

        # Wait for the server thread to finish
        if self.thread is not None:
            _thread.exit()

        # Close the server socket
        if self.server_socket is not None:
            self.server_socket.close()
