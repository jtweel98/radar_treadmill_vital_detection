import cv2
import time
import signal
import sys
import socket

# Constants
HOST = "192.168.50.97" # Change this to raspberry Pi IP address (type "hostname -I" in rp terminal)
HEADER_LENGTH = 4
BELT_LENGTH = 2.481 # [m]
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30
# threshold for greyscale value of pixel, 0 being black 255 being full white
THRESHOLD = 30 # might need to decrease this in a darker environement
BINARY_THRESHOLD = 50

# Global Variables
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cap = cv2.VideoCapture(0)
prev_time = time.time()
is_marker = False

# Helper Functions
def send_speed(speed, client_socket):
    speed = str(round(speed, 2))
    try:
        packet_len = str(len(speed)).zfill(HEADER_LENGTH)
        msg = bytes(packet_len + speed, 'utf-8')
        client_socket.sendall(msg)
        print(msg)
    except Exception as e:
        print(e)
        sock.close()
        exit(0)

def begin_measurement(client_socket):
    global is_marker, prev_time
    while True:
        _, img = cap.read()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, img = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY)

        mean_white_val = img.mean()

        # cv2.imshow("Test", img)
        # key = cv2.waitKey(1) & 0xFF
        # if key == ord("q"):
        #     break

        if mean_white_val >= THRESHOLD and not is_marker:
            is_marker = True
            cur_time = time.time()
            # speed = 2.23694*BELT_LENGTH/(cur_time - prev_time)
            speed = BELT_LENGTH/(cur_time - prev_time)
            prev_time = cur_time
            send_speed(speed, client_socket)
        elif mean_white_val == 0:
            is_marker = False

# Register Signal Handler
def signal_handler(sig, frame):
    sock.close()
    # Release the capture
    cap.release()
    cv2.destroyAllWindows()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python {command} <port>".format(command=sys.argv[0]))
        exit(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)

    PORT = int(sys.argv[1])
    sock.bind((HOST, PORT))
    print("Listening on port {port} ...".format(port=PORT))
    sock.listen(1)

    client_socket, client_addr = sock.accept()
    print("Connected by: ", client_addr)

    begin_measurement(client_socket)
