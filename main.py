import socket
import time

import serial.tools.list_ports

DEFAULT_BAUD_RATE = 115200
DEFAULT_UDP_PORT = 5005
DEFAULT_UDP_DESTINATION = "127.0.0.1"


class SerialDevice:
    def __init__(self, port, baud_rate: int = DEFAULT_BAUD_RATE):
        self.port = port
        try:
            self.serial = serial.Serial(port.device, baud_rate, timeout=1)
        except serial.SerialException as e:
            print(f"Failed to initialize device {port.device}: {str(e)}")
            raise

    def read(self):
        """Read data from the serial port if available."""
        if self.serial.in_waiting:
            try:
                return self.serial.readline().decode('utf-8').strip()
            except (serial.SerialException, UnicodeDecodeError) as e:
                print(f"Error reading from {self.port.device}: {str(e)}")
                return None
        return None


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
                try:
                    devices[port.device] = SerialDevice(port)
                    print(f'New device {port.device}')
                except serial.SerialException:
                    print(f'Failed to add device {port.device}')
                    continue

    for device in devices.values():
        try:
            data = device.read()
            if data:
                formatted_data = f"{device.port.device}: {data}"
                print(f'Device {device.port.device} send data: {data}')
                sock.sendto(formatted_data.encode('utf-8'), (DEFAULT_UDP_DESTINATION, DEFAULT_UDP_PORT))
        except serial.SerialException:
            print(f'Device {device.port.device} disconnected')
            to_remove.append(device)

    for rm in to_remove:
        del devices[rm.port.device]
    to_remove.clear()
    time.sleep(1/60)
