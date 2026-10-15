import socket
import time
import json
import argparse
import serial.tools.list_ports
from serial.tools.list_ports_common import ListPortInfo

DEFAULT_BAUD_RATE = 115200
DEFAULT_UDP_PORT = 5005
DEFAULT_UDP_DESTINATION = "127.0.0.1"

parser = argparse.ArgumentParser(
    prog='Serial to UDP',
    description='pipe serial input into udp',
    epilog='developed by Tweaklab AG / Philip Whitfield')
parser.add_argument('--exclude', nargs='+',
                    help="keywords on product or manufacturer string that will skip a device if matched")
parser.add_argument('--include', nargs='+',
                    help="keywords on product or manufacturer string that will only include a device if matched")
args = parser.parse_args()

devices: dict[str, SerialDevice] = {}

is_first_loop = True

class SerialDevice:
    def __init__(self, port, baud_rate: int = DEFAULT_BAUD_RATE):
        self.port = port
        try:
            self.serial = serial.Serial(port.device, baud_rate, timeout=1)
        except serial.SerialException as e:
            if is_first_loop or not devices:
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


next_port_check = time.time()
to_remove: list[SerialDevice] = []

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Started udp server on %s:%s" % (DEFAULT_UDP_DESTINATION, DEFAULT_UDP_PORT))


def port_info(port: ListPortInfo):
    return f"port: {port.device}, product: {port.product}, manufacturer: {port.manufacturer}"


while True:
    now = time.time()
    if next_port_check < now:
        next_port_check = now + 5
        ports = serial.tools.list_ports.comports(include_links=False)
        for port in ports:
            if args.exclude and any(
                    exclude in str(port.product) or exclude in str(port.manufacturer) for exclude in args.exclude):
                if is_first_loop or not devices:
                    print("Skipping device due to exclude filter - ", port_info(port))
                continue
            if args.include and not any(
                    include in str(port.product) or include in str(port.manufacturer) for include in args.include):
                if is_first_loop or not devices:
                    print("Skipping device due to include filter - ", port_info(port))
                continue
            # print(port.device)
            # print(port.product, port.manufacturer)
            # continue
            if port.device not in devices:
                try:
                    print("attempt to open - ", port_info(port))
                    devices[port.device] = SerialDevice(port)
                    print(f'New device {port.device}')
                except serial.SerialException:
                    if not devices:
                        print(f'Failed to add device {port.device}')
                    continue

    for device in devices.values():
        try:
            data = device.read()
            if data:
                try:
                    # Try to parse as JSON
                    parsed_data = json.loads(data)
                    json_data = {
                        "device": device.port.device,
                        "data": parsed_data  # Use parsed JSON as a nested object
                    }
                except json.JSONDecodeError:
                    # If not valid JSON, treat as plain string
                    json_data = {
                        "device": device.port.device,
                        "data": data
                    }
                formatted_data = json.dumps(json_data)
                print(f'Device {device.port.device} send data: {data}')
                sock.sendto(formatted_data.encode('utf-8'), (DEFAULT_UDP_DESTINATION, DEFAULT_UDP_PORT))
        except serial.SerialException:
            print(f'Device {device.port.device} disconnected')
            to_remove.append(device)

    for rm in to_remove:
        del devices[rm.port.device]
    to_remove.clear()
    is_first_loop = False
    time.sleep(1 / 90)
