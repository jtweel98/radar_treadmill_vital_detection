from radar_config import RadarMetrics
from scipy.fft import fft
from scipy import signal
import numpy as np
from copy import copy
from radar_tools import C

class DigitalSignalProcessor:
    def __init__(self, radar_metrics):
        self.radar_metrics = radar_metrics
    
    def hp_filter_butterworth(self, sig, cutoff, order=8):
        fs = self.radar_metrics.adc_sample_rate_hz
        sos = signal.butter(order, cutoff, 'hp', fs=fs, output='sos')
        return signal.sosfilt(sos, sig)
    
    def decouple_dc(self, sig):
        sig -= np.mean(sig)
        return sig

    def ss_fft(self, sig, zero_pad=0):
        # single side fft
        sig_cpy = list(copy(sig))

        if zero_pad > 0:
            sig_cpy += (zero_pad - len(sig))*[0]

        fs = self.radar_metrics.adc_sample_rate_hz
        N = len(sig_cpy)
        freq_spec = fft(sig_cpy)
        ss_freq_spec = freq_spec[0:N // 2]
        x_f = np.linspace(0, fs / 2, N // 2)

        return ss_freq_spec, x_f, N // 2

    def if_to_d(self, if_sig):
        S = self.radar_metrics.chirp_slope
        return C * if_sig / (2.0 * S)
    
    def d_to_if(self, dis):
        S = self.radar_metrics.chirp_slope
        return S * 2.0 * dis / C
    
    def filter_min_distance(self, sig):
        fc = self.d_to_if(self.radar_metrics.min_range)
        return self.hp_filter_butterworth(sig, fc)
