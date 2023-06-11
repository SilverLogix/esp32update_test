# Import required modules
import gc  # Helps clean up and organize memory
import _thread  # Allows running multiple things at the same time
import uos  # Helps interact with the computer's operating system
import usocket as socket  # Helps with sending and receiving data over the internet
import utime  # Helps with time-related operations

# Define constants
DEFAULT_PAGE = "index.html"  # The default webpage to show
PAGE_404 = b"HTTP/1.0 404 Not Found\r\nContent-Type: text/plain\r\n\r\nPage not found"  # A message for when a page isn't found
STOP_COMMAND = "/stop"  # A special command to stop the server
THREAD_TIMEOUT = 1  # How long to wait for a request before moving on

# Global variables for the webpage
w_name = "weufwefiui"  # A name to use in the webpage
w_color = "blue"  # A color to use in the webpage


# Define the WebServer class
class WebServer:
    def __init__(self):
        self.server_socket = None  # The server's connection point for clients
        self.active_thread = None  # The currently running task

    def handle_request(self, client_socket, server_socket):
        try:
            request = client_socket.makefile("rwb", 0)  # creates a file-like object for reading and writing data over a network socket
            request_lines = request.readline().decode().split("\r\n")  # Reads the lines of the request

            command = None  # The specific request made by the client

            # Find the first line containing the request method and path
            for line in request_lines:
                if line.startswith("GET ") or line.startswith("POST "):
                    command = line.split()[1]  # Extracts the path from the request
                    break

            print("Received request:", command)

            if not command or command == "/":
                command = DEFAULT_PAGE  # If no specific page is requested, use the default page

            if command == STOP_COMMAND:
                print("Server stopping...")
                uos.dupterm(None)  # Closes the server's connection to the computer's terminal
                client_socket.close()  # Closes the connection to the client
                server_socket.close()  # Closes the server's connection point for clients
                _thread.exit()  # Stops the currently running task (thread)
                return

            elif command == "/test":
                print("TEST")
                x = 23  # A special number for testing
                print(x)
                command = DEFAULT_PAGE  # After testing, show the default page

            response = self.get_page(command)  # Gets the content of the requested page
            if response is None:
                response = PAGE_404  # If the page doesn't exist, show a special message

            print("Sending response:", response.decode())
            client_socket.send(response)  # Sends the response back to the client

        finally:
            request.close()  # Closes the request file
            client_socket.close()  # Closes the connection to the client

            # Cleans up and organizes memory to keep things tidy
            gc.collect()

    def get_page(self, page):
        try:
            with open(page, "r") as file:
                content = file.read()  # Reads the content of the webpage file
                formatted_content = self.format_fstrings(content)  # Makes the webpage more interesting and dynamic
                return formatted_content.encode()  # Prepares the content to be sent over the internet
        except OSError:
            return None  # If the file doesn't exist or can't be opened, return None
        except Exception as e:
            print("Error reading file:", e)
            return None  # If there's any other error, return None

    def format_fstrings(self, content):
        import re  # Helps find and replace special expressions in the webpage

        def eval_fstring(match):
            expr = match.group(1)  # Extracts the special expression inside the braces
            try:
                # Define allowed variables for evaluating the special expression
                allowed_globals = {"name": w_name, "color": w_color}

                return str(eval(expr, allowed_globals))  # Evaluates the special expression and converts it to a string
            except Exception as e:
                print("Error evaluating f-string expression:", e)
                return match.group(0)  # If there's an error, return the original special expression

        pattern = re.compile(r'\{([^{}]+)}')  # The pattern to find the special expressions in the webpage
        formatted_content = re.sub(pattern, eval_fstring, content)  # Replaces the special expressions with their evaluated values
        return formatted_content

    def handle_request_with_timeout(self, client_socket, server_socket):
        self.active_thread = _thread.start_new_thread(self.handle_request, (client_socket, server_socket))  # Starts handling the request in a separate thread

        utime.sleep(THREAD_TIMEOUT)  # Waits for the specified timeout

        if self.active_thread is not None:
            _thread.exit()  # If the active thread is still running, stop it

    def start(self):
        self.server_socket = socket.socket()  # Creates a connection point (socket) for the server
        self.server_socket.bind(('0.0.0.0', 80))  # Binds the socket to listen on all available interfaces on port 80
        self.server_socket.listen(5)  # Starts listening for client connections with a maximum backlog of 5 clients

        print("Server started")

        while True:
            client_socket, addr = self.server_socket.accept()  # Accepts a client connection
            print("New connection from:", addr)
            self.handle_request_with_timeout(client_socket, self.server_socket)  # Handles the client's request with a timeout

    def stop(self):
        print("Server stopping...")
        uos.dupterm(None)  # Closes the server's connection to the computer's terminal
        self.server_socket.close()  # Closes the server's connection point for clients
        _thread.exit()  # Stops the currently running task (thread)


# Create an instance of the WebServer class and run it
server = WebServer()
server.start()
