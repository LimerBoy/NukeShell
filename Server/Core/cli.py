#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Author : LimerBoy
# github.com/LimerBoy/NukeShell

# Import modules
from colorama import Fore
from os import name, system
from argparse import ArgumentParser

# Parse command line
def ParseArgs():
    parser = ArgumentParser(description="NukeShell server arguments")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Listen IP")
    parser.add_argument("--port", type=int, default=5125, help="Listen port")
    return parser.parse_args()

# Clear terminal window
def Clear():
    system("cls" if name == "nt" else "clear")

# Terminal banner
Banner = rf"""{Fore.LIGHTGREEN_EX}
     _      _     _  __ _____   ____  _     _____ _     _    
    / \  /|/ \ /\/ |/ //  __/  / ___\/ \ /|/  __// \   / \   
    | |\ ||| | |||   / |  \    |    \| |_|||  \  | |   | |   
    | | \||| \_/||   \ |  /_   \___ || | |||  /_ | |_/\| |_/\
    \_/  \|\____/\_|\_\\____\  \____/\_/ \|\____\\____/\____/
                                        {Fore.LIGHTYELLOW_EX}Created by LimerBoy{Fore.RESET}
"""

