import numpy as np
import matplotlib.pyplot as plt
from radar_config import RadarMetrics
from scipy.fft import fft
from scipy import signal
from dsp import DigitalSignalProcessor
from radar import Radar
from copy import copy

import signal
import sys
import time

# Setup Signal Handler
def signal_handler(sig, frame):
    exit(0)
signal.signal(signal.SIGINT, signal_handler)

# Setup Radar Device
radar = Radar(min_range=0)
dsp = DigitalSignalProcessor(radar.metrics)

# Begin sending data here


# # Get N x M buffer ready
# buffer_time = 32 # (s) --> how long we wanna wait filling up the matrix
# N = radar.metrics.num_samples_per_chirp
# M = radar.metrics.frame_rate * buffer_time # total of 1024 fft chirp signals (size N//2) where one chirp is taken per frame

# time_buffer = np.zeros((N, M), dtype=float)
# ftt_buffer = np.zeros((N//2, M), dtype=complex)

# # collect data
# chirps_collected = 0
# while chirps_collected < M:
#     frame_data = radar.next_frame_data(raw=True)
#     first_chirp_sig = frame_data[0].tolist()
#     chirps_collected += 1

#     time_buffer = np.roll(time_buffer, -1, axis=1)
#     time_buffer[:, M-1] = first_chirp_sig

# # process chirps
# chirps_processed = 0

# while chirps_processed < M:
#     chirp = copy(time_buffer[:, chirps_processed])
#     chirp = dsp.decouple_dc(chirp)
#     chirp = dsp.filter_min_distance(chirp)
#     chirp_range_fft = fft(chirp)[0:N//2]
#     chirps_processed += 1

#     ftt_buffer = np.roll(ftt_buffer, -1, axis=1)
#     ftt_buffer[:, M-1] = chirp_range_fft

# t_vals = np.linspace(0, buffer_time, M)

# test_d = 0.8128
# fig, axs = plt.subplots(5)
# axs[0].plot(t_vals, ftt_buffer[int(test_d//radar.metrics.range_resolution) - 2].real)
# axs[1].plot(t_vals, ftt_buffer[int(test_d//radar.metrics.range_resolution) - 1].real)
# axs[2].plot(t_vals, ftt_buffer[int(test_d//radar.metrics.range_resolution) - 0].real)
# axs[3].plot(t_vals, ftt_buffer[int(test_d//radar.metrics.range_resolution) + 1].real)
# axs[4].plot(t_vals, ftt_buffer[int(test_d//radar.metrics.range_resolution) + 2].real)

# plt.plot(t_vals, ftt_buffer[0].real)
# plt.grid()
# plt.show()