import cv2
import time
import signal
import sys

# Constants
BELT_LENGTH = 2.481 # [m]
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30

# threshold for "whiteness" of pixel, 0 being black 255 being full white
THRESHOLD = 30 # might need to decrease this in a darker environement

# Setup Video Capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
cap.set(cv2.CAP_PROP_FPS, FPS)

show_image = False
is_marker = False
prev_time = time.time()

# Register Signal Handler
def signal_handler(sig, frame):
    # Release the capture
    cap.release()
    cv2.destroyAllWindows()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

while True:
    _, img = cap.read()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary_img = cv2.threshold(img, 25, 255, cv2.THRESH_BINARY)

    mean_white_val = binary_img.mean()

    if mean_white_val >= THRESHOLD and not is_marker:
        is_marker = True
        cur_time = time.time()
        print("frequency: ", 0.0568182*BELT_LENGTH/(cur_time - prev_time)) # Convert to MPH (same as treadmill's output)
        prev_time = cur_time
    elif mean_white_val == 0:
        is_marker = False

    if show_image:
        cv2.imshow("Binary Image", binary_img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
