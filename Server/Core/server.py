#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Author : LimerBoy
# github.com/LimerBoy/NukeShell

# Import modules
from sys import exit
from time import sleep
from colorama import Fore
from threading import Thread
from Core.clients import Client, ClientsManager
from socket import socket, \
    AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET, SHUT_RDWR


""" TCP server class """
class ServerListen:
    """ Constructor """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.ServerStopped = False
        self.server = self.InitServer(host, port)
        Thread(target=self.AcceptClients).start()

    # Stop server
    def StopServer(self):
        self.ServerStopped = True
        ConnectedClients = ClientsManager.GetConnectedClients()
        clients = len(ConnectedClients)
        print(f"\n{Fore.RED}[Server]{Fore.WHITE} Disconnecting {clients} clients ...")
        # Disconnect all clients
        for client in ConnectedClients:
            Thread(target=client.Disconnect).start()
        # Wait for all clients disconnection
        # while len(ConnectedClients) != 0:
        #    print(len(ConnectedClients))
        #    sleep(0.2)
        sleep(clients / 2)
        # Stop tcp server
        print(f"{Fore.RED}[Server]{Fore.WHITE} Stopping server ...")
        self.server.shutdown(SHUT_RDWR)
        self.server.close()
        exit(1)

    # Initialize server socket
    @staticmethod
    def InitServer(host="0.0.0.0", port=5125) -> socket:
        # Create sockets
        server = socket(
            AF_INET,
            SOCK_STREAM
        )
        # Settings
        server.settimeout(50)
        server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # Bind socket
        server.bind((host, port))
        server.listen(5)
        print(f"{Fore.GREEN}[Server]{Fore.WHITE} Listening at {host}:{port} ...{Fore.RESET}")
        return server

    # Accept all connections
    def AcceptClients(self):
        while True:
            # Client connected
            try:
                connection, address = self.server.accept()
                Client(connection, address)
            except OSError as e:
                if self.ServerStopped:
                    return
                connection.close()
                print(f"{Fore.RED}[Server]{Fore.WHITE} Failed to accept client", *address, Fore.RESET, e)
                self.__init__(self.host, self.port)
                break


