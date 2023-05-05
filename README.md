# BSY-Stage-5-Black-Gate

This is a project I worked on as part of subject Introduction to Security (BSY) at FEL CVUT.

The project is ment to create a Command and Controll chanell through the use of Github gists.

The code consists of three main scripts (controller.py, bot.py, connection.py) and two starting scripts (runc.py, runb.py). 

Starting scripts are there for easier running of the scripts when changing ids, tokens, but the main scripts can be run as they have the main function defined.

Controller.py is the script for controlling the bots. It is there to interpret commands from user and pass on to bots and retrieve info from bots. Its duty is to ping bots, checking if they are alive, at random time intervals in order to be less suspicious. By pinging them he checks if they are alive. A bot can be selected by the IP address. 

Bot.py is the script that creates a bot. The bot interacts with the infected host and receives commands from the controller, executes desired commands on the host OS, takes the output and sends back the corresponding reply, with the hidden packet of the response.

Connection.py is the script that is working with Github API, reading and sending comments, as well as contains the messages which are created using steganography. I decided to use stackoverflow-like questions with some grammatical errors. 

The messages used are below.

- Pinging bots <br/>
"Can you tell me why is this causing the code to crash?" <br/>
"Because the reciever fell asleep and missed the message" <br/>

- Get all users <br/>
"Are you the only one working on this code?" <br/>
"Yep, just me :)" <br/>

- Show the contents of a folder <br/>
"Can you show me the whole code?" <br/>
"Just a sec." <br/>

- Show the id <br/>
"Can you identify the problem here?" <br/>
"I will try, but no promisses" <br/>

- Copy files <br/>
"Where sholud I transfer to python or Java" <br/>
"C++ ofcourse" <br/>

- Executing binaries <br/>
"What is running faster Linux or Windows" <br/>
"Linux duhhh” <br/>

- Reading files <br/>
"Why can't I write files using this code??" <br/> 
"Because that code is for reading" <br/>

- Shut down <br/>
"Any idea how to kill a process?" <br/>
"Just unplug the computer" <br/>

The system is ment to work as follows. The controller is issuing commands using the connection.py to send comments to a specified gist. Bots will retrieve last comment and interpret the message and execute the desired command and then it leaves a new comment, as sort of a response to look more natural and it will also leave a hidden encoded string ment for the controller. The controller decodes the string and prints the content which is the result of the executed command.

In order to use gists as a communication channel at all a Github account is needed to generate a Personal Access Token, ID of the gist that is to be used and 32 byte key because the communication must be encrypted. The string is needed only for the running of the controller, bots have to use the key of the controller that they are going to communicate with.

![image36](https://user-images.githubusercontent.com/72748909/236576268-80f821c2-af69-4c62-8b3b-179a8b8aae6c.png)

![image12](https://user-images.githubusercontent.com/72748909/236576321-174a116b-8e4f-4f40-8ee9-c4c7dfb1b13b.png)
