from radar_config import RadarMetrics
from ifxRadarSDK import *
from dsp import DigitalSignalProcessor
import numpy as np

class Radar:

    def __init__(self, **kargs):
        self.metrics = RadarMetrics(**kargs)
        self.device = Device()
        self.device.set_config(**self.metrics.config_dict)
        self.frame = self.device.create_frame_from_device_handle()
    
    def next_frame_data(self, rx=0, filter=False):
        try:
            self.device.get_next_frame(self.frame)
        except RadarSDKFifoOverflowError as e:
            print(e)
            exit(1)
        
        # filter based on min distance
        matrix = self.frame.get_mat_from_antenna(rx)
        if filter:
            dsp = DigitalSignalProcessor(self.metrics)
            fc = dsp.d_to_if(self.metrics.min_range)
            for i in range(len(matrix)):
                matrix[i] = dsp.decouple_dc(matrix[i])
                matrix[i] = dsp.hp_filter_butterworth(matrix[i], fc)
            return np.matrix(matrix)
        return matrix
        


        