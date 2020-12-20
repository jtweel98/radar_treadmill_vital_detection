from radar import Radar
import json
import socket
import signal
import sys
import time

# Constants
HOST = "192.168.50.97" # Change this to raspberry Pi IP address (type "hostname -I" in rp terminal)

# Global Variables
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Setup Signal Handler
def signal_handler(sig, frame):
    sock.close()
    exit(0)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python {command} <port>".format(command=sys.argv[0]))
        exit(0)

    PORT = int(sys.argv[1])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(1)
    print("Listening on port {port} ...".format(port=PORT))

    client_socket, client_addr = sock.accept()
    print("Connected by: ", client_addr)

    radar = Radar(min_range=0, range_resolution = 0.1)

    try:
        # Send config data first
        radar.send_config_packet(client_socket)

        # Commence data stream
        radar.start_data_stream(client_socket)
    except Exception as e:
        print(e)
        sock.close()
