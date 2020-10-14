import numpy as np
from ifxRadarSDK import *
import matplotlib.pyplot as graph

RX = 0

RX_1 = 1
RX_2 = 2
RX_3 = 4

DEFAULT_CONFIG = {
    "num_samples_per_chirp": 64,
    "num_chirps_per_frame": 32,
    "adc_samplerate_Hz": 2000000,
    "frame_period_us": 0,
    "lower_frequency_kHz": 58000000,
    "upper_frequency_kHz": 63000000,
    "bgt_tx_power": 31,
    "rx_antenna_mask": 1,
    "tx_mode": 0,
    "chirp_to_chirp_time_100ps": 1870000,
    "if_gain_dB": 33,
    "frame_end_delay_100ps": 400000000,
    "shape_end_delay_100ps": 1500000,
}

class RadarConfiguration:
    def __init__(self):
        '''
            The below radar metric come from Mackenzie Goodwin's implementation for breathing rate detection (Dr. Shaker's Lab)
            Can be found here: https://github.com/mackenzieg/radar_infineon_sdk/blob/master/src/radar_config.cpp
        '''
        self.config = DEFAULT_CONFIG
        self.range_resolution = 0.1
        self.max_range = 2.5
        self.min_range = 0.2
        self.speed_resolution = 0.2
        self.max_speed = 2.0
        self.frame_rate = 32
        self.adc_sample_rate_hz = 1000000 # 1,000,000 Hz
        self.bgt_tx_power = 31
        self.rx_antenna_number = RX_1 | RX_2 | RX_3
        self.if_gain_db = 33
        self.center_frequency_khz = 60500000 # 60,500,000 KHz

    def apply_config(self):
        LIGHT = 2.99792458e8
        BW = 0.001 * LIGHT / (2 * self.range_resolution)
        self.config["lower_frequency_kHz"] = self.center_frequency_khz - (BW * 0.5 + 0.5) # Uncertain why there is a 0.5 added
        self.config["upper_frequency_kHz"] = self.center_frequency_khz + (BW * 0.5 + 0.5) # Uncertain why there is a 0.5 added
        
        
        # The number of bins multiplied with the range resolution results in the total range. Due to
        # Nyquist theorem only half of the spectrum is evaluated in range transform so the total range
        # is reduced by a factor of 2.

        # Range transform is an FFT, and usually FFT sizes are powers of 2. If number of samples is
        # not a power of two, the FFT input could be zero padded.
        num_samples_per_chirp = 2 * self.max_range / self.range_resolution
        self.config["num_samples_per_chirp"] = highest_power_of_two(num_samples_per_chirp) # TODO enforce 32 bit integer

        # Formula provided by algorithm team, information can be found in some papers
        self.config["chirp_to_chirp_time_100ps"] = 1.0e10 * LIGHT / (4.0 * self.max_speed * 1000 * self.center_frequency_khz) # Need conversion from kHz to Hz

        
        # The number of bins multiplied with the speed resolution results in the maximum speed. The
        # bins of the Doppler transforms represent the -v_max...v_max, that's why the maximum speed
        # is divided by 2.

        # Doppler transform is an FFT, and usually FFT sizes are powers of 2. If number of samples is
        # not a power of two, the FFT input could be zero padded. 
        num_chirps_per_frame = 2 * self.max_speed / self.speed_resolution
        self.config["num_chirps_per_frame"] = highest_power_of_two(num_chirps_per_frame) # TODO enforce 32 bit integer

        # Properties copied from above
        self.config["frame_period_us"] = 1.0e6 / self.frame_rate
        self.config["adc_samplerate_Hz"] = self.adc_sample_rate_hz
        self.config["bgt_tx_power"] = self.bgt_tx_power
        self.config["rx_antenna_number"] = self.rx_antenna_number
        self.config["if_gain_dB"] = self.if_gain_db



def highest_power_of_two(val):
    '''
        Rounds a 32 bit value to the next power of two
        From: https://graphics.stanford.edu/~seander/bithacks.html#RoundUpPowerOf2
    '''
    val -= 1
    val |= val >> 1
    val |= val >> 2
    val |= val >> 4
    val |= val >> 8
    val |= val >> 16
    val += 1
    return val


radar = Device()
radar.set_config(**DEFAULT_CONFIG)

frame = radar.create_frame_from_device_handle()

print("Number of RXs: ", frame.get_num_rx(), "\n")

try:
    radar.get_next_frame(frame)
except RadarSDKError:
    print("Error")
    exit(1)

matrix_data = frame.get_mat_from_antenna(RX)
