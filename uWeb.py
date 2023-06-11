import gc
import _thread
import uos
import usocket as socket

DEFAULT_PAGE = "index.html"
PAGE_404 = b"HTTP/1.0 404 Not Found\r\nContent-Type: text/plain\r\n\r\nPage not found"
STOP_COMMAND = "/stop"

# Global vars to be used in the webpage:
w_name = "weufwefiui"
w_color = "blue"


def handle_request(client_socket, server_socket):
    try:
        request = client_socket.makefile("rwb", 0)
        request_lines = request.readline().decode().split("\r\n")
        command = None

        # Find the first line containing the request method and path
        for line in request_lines:
            if line.startswith("GET ") or line.startswith("POST "):
                command = line.split()[1]  # Extract the command (path)
                break

        print("Received request:", command)

        if not command or command == "/":
            command = DEFAULT_PAGE

        if command == STOP_COMMAND:
            print("Server stopping...")
            uos.dupterm(None)  # Release the terminal
            client_socket.close()
            server_socket.close()
            _thread.exit()  # Terminate the current thread
            return

        elif command == "/test":
            print("TEST")
            x = 23
            print(x)
            command = DEFAULT_PAGE

        response = get_page(command)
        if response is None:
            response = PAGE_404

        print("Sending response:", response.decode())
        client_socket.send(response)

    finally:
        request.close()
        client_socket.close()

    # Perform garbage collection
    gc.collect()


def get_page(page):
    try:
        with open(page, "r") as file:
            content = file.read()
            formatted_content = format_fstrings(content)
            return formatted_content.encode()
    except OSError:
        return None
    except Exception as e:
        print("Error reading file:", e)
        return None


def format_fstrings(content):
    import re

    def eval_fstring(match):
        expr = match.group(1)
        try:
            # Define allowed variables for f-strings evaluation
            # ----------------------------------------------- #

            allowed_globals = {"name": w_name, "color": w_color}

            # ----------------------------------------------- #
            return str(eval(expr, allowed_globals))
        except Exception as e:
            print("Error evaluating f-string expression:", e)
            return match.group(0)  # Return the original f-string if evaluation fails

    pattern = re.compile(r'\{([^{}]+)}')
    formatted_content = re.sub(pattern, eval_fstring, content)
    return formatted_content


def main():
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 80))
    server_socket.listen(5)

    print("Server started")

    while True:
        client_socket, addr = server_socket.accept()  # noqa
        print("New connection from:", addr)
        _thread.start_new_thread(handle_request, (client_socket, server_socket))


# Run the server
main()
