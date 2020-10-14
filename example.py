import numpy as np
from ifxRadarSDK import *

# open device
device = Device()

# set device config
device.set_config()

# create frame
frame = device.create_frame_from_device_handle()

# number of virtual active receiving antennas
num_rx = frame.get_num_rx()

# A loop for fetching a finite number of frames comes next..
for frame_number in range(10):
    try:
        device.get_next_frame(frame)
    except RadarSDKFifoOverflowError:
        print("Fifo Overflow")
        exit(1)

    # Do some processing with the obtained frame.
    # In this example we just dump it into the console
    print ("Got frame " + format(frame_number) + ", num_antennas={}".format(num_rx))

    for iAnt in range(0, num_rx):
        mat = frame.get_mat_from_antenna(iAnt)
        print("Antenna", iAnt, "\n", mat)
