import socket
import time

import serial.tools.list_ports

DEFAULT_BAUD_RATE = 115200
DEFAULT_UDP_PORT = 5005
DEFAULT_UDP_DESTINATION = "127.0.0.1"


class SerialDevice:
    def __init__(self, port, baud_rate: int = DEFAULT_BAUD_RATE):
        self.port = port
        self.serial = serial.Serial(port.device, baud_rate, timeout=1)
        # self.serial.flushInput()
        # self.serial.flushOutput()

    def read(self):
        return self.serial.readline()


devices: dict[str, SerialDevice] = {}

next_port_check = time.time()
to_remove: list[SerialDevice] = []

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Started udp server on %s:%s" % (DEFAULT_UDP_DESTINATION, DEFAULT_UDP_PORT))

while True:
    now = time.time()
    if next_port_check < now:
        next_port_check = now + 5
        ports = serial.tools.list_ports.comports(include_links=False)
        for port in ports:
            if port.device not in devices:
                devices[port.device] = SerialDevice(port)
                print(f'New device {port.device}')

    for device in devices.values():
        try:
            data = device.read()
            if data:
                sock.sendto(data, (DEFAULT_UDP_DESTINATION, DEFAULT_UDP_PORT))
        except serial.SerialException:
            print(f'Device {device.port.device} disconnected')
            to_remove.append(device)

    for rm in to_remove:
        del devices[rm.port.device]
    to_remove.clear()
    time.sleep(1/60)
