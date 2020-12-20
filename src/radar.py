from radar_config import RadarMetrics
from ifxRadarSDK import *
import json
from copy import deepcopy
from threading import Thread

HEADER_LENGTH = 4
BUFFER_MAX = 200

def send_chirp(chirp, client):
    serialized_packet = json.dumps(
        { "packet_type": "chirp", "data": chirp }
    )
    packet_len = str(len(serialized_packet)).zfill(HEADER_LENGTH)
    msg = bytes(packet_len + serialized_packet, 'utf-8')
    client.sendall(msg)

def send_thread_func(buffer, client):
    for chirp in buffer:
        send_chirp(chirp, client)
    return

class Radar:
    
    buffer = [0]*BUFFER_MAX
    buffer_index = 0

    def __init__(self, **kargs):
        self.device = Device()
        self.metrics = RadarMetrics(**kargs)
        self.device.set_config(**self.metrics.config_dict)
        self.frame = self.device.create_frame_from_device_handle()
    
    def next_frame_data(self, rx=0):
        self.device.get_next_frame(self.frame)
        matrix = self.frame.get_mat_from_antenna(rx)
        return matrix

    def refresh(self):
        self.frame = self.device.create_frame_from_device_handle()

    def start_data_stream(self, client_socket):
        while True:
            chirp = self.fetch_first_chirp()
            send_chirp(chirp, client_socket)

    def start_buffered_data_stream(self, client_socket):
        while True:
            chirp = self.fetch_first_chirp()
            if self.buffer_index < len(self.buffer):
                self.buffer[self.buffer_index] = chirp
                self.buffer_index += 1
            else:
                self.buffer_index = 0
                buffer_copy = deepcopy(self.buffer)
                send_thread = Thread(target=send_thread_func, args=(buffer_copy, client_socket))
                send_thread.start()

    def fetch_first_chirp(self):
        frame_data = self.next_frame_data()
        first_chirp = frame_data[0].tolist()
        return first_chirp
    
    def send_config_packet(self, client_socket):
        serialized_config = json.dumps({
            "packet_type": "config",
            "data": {
                "range_resolution": self.metrics.range_resolution,
                "max_range": self.metrics.actual_max_range,
                "min_range": self.metrics.min_range,
                "speed_resolution": self.metrics.speed_resolution,
                "max_speed": self.metrics.actual_max_velocity,
                "frame_rate": self.metrics.frame_rate,
                "adc_sample_rate_hz": self.metrics.adc_sample_rate_hz,
                "rx_antenna_number": self.metrics.rx_antenna_number,
                "center_frequency": self.metrics.center_frequency,
                "num_samples_per_chirp": self.metrics.num_samples_per_chirp,
                "num_chirps_per_frame": self.metrics.num_chirps_per_frame,
                "lower_frequency": self.metrics.lower_frequency,
                "upper_frequency": self.metrics.upper_frequency,
                "bandwidth": self.metrics.bandwidth
            }
        })
        packet_len = str(len(serialized_config))
        packet_len = packet_len.zfill(HEADER_LENGTH)
        msg = bytes(packet_len + serialized_config, 'utf-8')
        client_socket.sendall(msg)

