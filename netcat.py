import argparse
import socket
import shlex
# subprocess library is a powerful process-creation interface taht gives us ways to interact with client programs
import subprocess
import sys
import textwrap
import threading

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

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return 
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)

    return output.decode()

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