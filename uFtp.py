import _thread
import os
import socket

DEFAULT_PORT = 21
STOP_COMMAND = "QUIT"
PASV_COMMAND = "PASV"
LIST_COMMAND = "LIST"
RETR_COMMAND = "RETR"
STOR_COMMAND = "STOR"
CWD_COMMAND = "CWD"
MKD_COMMAND = "MKD"
MKF_COMMAND = "MKF"


class FTPServer:
    def __init__(self, port=DEFAULT_PORT):
        self.server_socket = None
        self.active_thread = None
        self.port = port

    def handle_request(self, client_socket, addr):
        print("New connection from:", addr)

        # Send welcome message to the client
        client_socket.send(b"220 Welcome to the FTP server\r\n")

        current_dir = os.getcwd()

        try:
            data_socket = None

            while True:
                # Receive client commands
                command = client_socket.recv(1024).decode().strip()
                print("Received command:", command)

                if command == STOP_COMMAND:
                    print("Client requested to quit.")
                    break

                if command == PASV_COMMAND:
                    # Enter passive mode and send data port information to the client
                    data_socket = self.enter_passive_mode(client_socket)
                    continue

                if data_socket:
                    if command == LIST_COMMAND:
                        # List files and directories
                        self.send_file_list(client_socket, data_socket)

                    elif command.startswith(RETR_COMMAND):
                        # Retrieve a file
                        filename = command.split(maxsplit=1)[1]
                        self.send_file(client_socket, data_socket, filename)

                    elif command.startswith(STOR_COMMAND):
                        # Store a file
                        filename = command.split(maxsplit=1)[1]
                        self.receive_file(client_socket, data_socket, filename)

                    elif command.startswith(CWD_COMMAND):
                        # Change working directory
                        directory = command.split(maxsplit=1)[1]
                        response = self.change_directory(directory)
                        client_socket.send(response.encode())

                    elif command.startswith(MKD_COMMAND):
                        # Create a directory
                        directory = command.split(maxsplit=1)[1]
                        response = self.create_directory(directory)
                        client_socket.send(response.encode())

                    elif command.startswith(MKF_COMMAND):
                        # Create a file
                        filename = command.split(maxsplit=1)[1]
                        response = self.create_file(filename)
                        client_socket.send(response.encode())

                    else:
                        client_socket.send(b"502 Command not implemented\r\n")
                else:
                    client_socket.send(b"425 Use PASV first\r\n")

        finally:
            if data_socket:
                data_socket.close()
            client_socket.close()

    def enter_passive_mode(self, client_socket):
        data_socket = socket.socket()
        data_socket.bind(('0.0.0.0', 0))
        data_socket.listen(1)
        ip, port = data_socket.getsockname()

        response = "227 Entering Passive Mode ({},{},{},{},{}).\r\n".format(
            *ip.split('.'), port >> 8 & 0xFF, port & 0xFF
        )
        client_socket.send(response.encode())

        return data_socket

    def send_file_list(self, client_socket, data_socket):
        file_list = os.listdir()
        response = "\r\n".join(file_list) + "\r\n"
        client_socket.send(b"150 Here comes the directory listing\r\n")
        data_socket.send(response.encode())
        data_socket.close()
        client_socket.send(b"226 Directory send OK\r\n")

    def send_file(self, client_socket, data_socket, filename):
        if os.path.isfile(filename):
            client_socket.send(b"150 Opening data connection\r\n")
            with open(filename, "rb") as file:
                data = file.read(1024)
                while data:
                    data_socket.send(data)
                    data = file.read(1024)
            data_socket.close()
            client_socket.send(b"226 Transfer complete\r\n")
        else:
            client_socket.send(b"550 File not found\r\n")

    def receive_file(self, client_socket, data_socket, filename):
        client_socket.send(b"150 Opening data connection\r\n")
        try:
            with open(filename, "wb") as file:
                data = data_socket.recv(1024)
                while data:
                    file.write(data)
                    data = data_socket.recv(1024)
            data_socket.close()
            client_socket.send(b"226 Transfer complete\r\n")
        except OSError:
            client_socket.send(b"550 Failed to store file\r\n")

    def change_directory(self, directory):
        try:
            os.chdir(directory)
            return "250 Directory changed to {}\r\n".format(os.getcwd())
        except OSError:
            return "550 Failed to change directory\r\n"

    def create_directory(self, directory):
        try:
            os.mkdir(directory)
            return "250 Directory created {}\r\n".format(directory)
        except OSError:
            return "550 Failed to create directory\r\n"

    def create_file(self, filename):
        try:
            with open(filename, "w") as file:
                file.write("")
            return "250 File created {}\r\n".format(filename)
        except OSError:
            return "550 Failed to create file\r\n"

    def handle_request_with_thread(self, client_socket, addr):
        self.active_thread = _thread.start_new_thread(self.handle_request, (client_socket, addr))

    def start(self):
        self.server_socket = socket.socket()
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        print("FTP Server started on port", self.port)

        while True:
            client_socket, addr = self.server_socket.accept()
            self.handle_request_with_thread(client_socket, addr)

    def stop(self):
        print("Server stopping...")
        self.server_socket.close()
        _thread.exit()


# Create an instance of the FTPServer class and run it
# server = FTPServer()
 #server.start()
