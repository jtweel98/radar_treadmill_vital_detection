import numpy as np
import matplotlib.pyplot as plt
from radar_config import RadarMetrics
from scipy.fft import fft
from scipy import signal
from dsp import DigitalSignalProcessor
from radar import Radar

import signal
import sys
import time

# Setup Signal Handler
def signal_handler(sig, frame):
    plt.grid()
    plt.show()
    exit(0)
    
signal.signal(signal.SIGINT, signal_handler)

# Setup Radar Device
radar = Radar(min_range=0)
dsp = DigitalSignalProcessor(radar.metrics)

# Collect Data
time_data = radar.next_frame_data()
# Reduce to average IF signal of all chrips
time_data = time_data.mean(0).tolist()[0]

ss_fft, x_f, N = dsp.ss_fft(time_data, zero_pad=2**10)

plt.plot(dsp.if_to_d(x_f), np.abs(ss_fft) / N)

print("Plotting Range FFT")

plt.grid()
plt.show()
from radar_tools import highest_power_of_two
