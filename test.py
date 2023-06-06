import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ("127.0.0.1", 5005)
s.bind(server_address)

print("====> LISTENING %s:%s <====" % server_address)

while True:
    data, address = s.recvfrom(4096)
    print(data.decode('utf-8'))