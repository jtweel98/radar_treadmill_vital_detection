from mk_radar import Radar
import json
import socket
import signal
import sys
import time

# Constants
HOST = "192.168.0.168"
PORT = 4242

# Global Variables
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
radar = Radar(min_range=0, range_resolution = 0.1)

# Setup Signal Handler
def signal_handler(sig, frame):
    sock.close()
    exit(0)
signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    sock.connect((HOST, PORT))
    print("Connected To: ", (HOST, PORT))

    # Send config data first
    radar.send_config_packet(sock)

    # Commence data stream
    radar.start_data_stream(sock)

# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("Usage: python {command} <port>".format(command=sys.argv[0]))
#         exit(0)

#     PORT = int(sys.argv[1])
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.bind((HOST, PORT))
#     sock.listen(1)
#     print("Listening on port {port} ...".format(port=PORT))

#     # print("Radar Config:")
#     # print(str(radar.metrics))

#     client_socket, client_addr = sock.accept()
#     print("Connected by: ", client_addr)

#     try:
#         # Send config data first
#         radar.send_config_packet(client_socket)

#         # Commence data stream
#         radar.start_data_stream(client_socket)
#     except Exception as e:
#         print(e)
#         sock.close()
