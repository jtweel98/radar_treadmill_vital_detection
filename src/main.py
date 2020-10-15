import numpy as np
from ifxRadarSDK import *
import matplotlib.pyplot as plt
from radar_config import RadarMetrics
from scipy.fft import fft
from tools import C

import signal
import sys
import time

radar_metrics = RadarMetrics(range_resolution=0.05, adc_sample_rate_hz=2000000)
radar_config = radar_metrics.config_dict

radar = Device()
radar.set_config(**radar_config)
frame = radar.create_frame_from_device_handle()

def signal_handler(sig, frame):
    plt.grid()
    plt.show()
    exit(0)
    
signal.signal(signal.SIGINT, signal_handler)

print("Collecting Data...")

while True:
    try:
        radar.get_next_frame(frame)
    except RadarSDKError:
        print("Error")
        exit(1)

    time_data = frame.get_mat_from_antenna(0)

    for if_data in time_data:
        if_data -= np.mean(if_data)
        N = len(if_data)
        T = 1.0 / radar_metrics.adc_sample_rate_hz
        x_t = np.linspace(0, N * T, N)
        freq_spec = fft(if_data)
        x_f = np.linspace(0, radar_metrics.adc_sample_rate_hz / 2, N // 2)
        x_d = x_f * C / (2.0 * radar_metrics.chirp_slope)
        plt.subplot(211)
        plt.plot(x_d, 2.0 / N * np.abs(freq_spec[0:N//2]))
        plt.subplot(212)
        plt.plot(x_t, if_data)
    time.sleep(0.1)
