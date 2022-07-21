import socket
from urllib import response

target_host = "127.0.0.1"
target_port = 9998

# create a socket object
# AF_INET indicates we'll use a standard IPv4 address or hostname
# SOCK_STREAM indicates that this will be a TCP client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect to client
client.connect((target_host, target_port))
# send data
client.send(b"GET / HTTP/1.1\r\nHost: Hi Server!\r\n\r\n")

response = client.recv(4096)
print(response.decode('utf8'))
client.close()