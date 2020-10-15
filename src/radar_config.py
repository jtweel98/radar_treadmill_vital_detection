from tools import highest_power_of_two, C

class RadarMetrics:

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

    def __init__(
        self,
        range_resolution=None,
        max_range=None,
        min_range=None,
        speed_resolution=None,
        max_speed=None,
        frame_rate=None,
        adc_sample_rate_hz=None,
        bgt_tx_power=None,
        rx_antenna_number=None,
        if_gain_db=None,
        center_frequency=None,
    ):
        self.__config = self.DEFAULT_CONFIG
        '''
            The below radar metrics come from Mackenzie Goodwin's implementation for breathing rate detection (Dr. Shaker's Lab)
            Can be found here: https://github.com/mackenzieg/radar_infineon_sdk/blob/master/src/radar_config.cpp
        '''
        self.range_resolution = range_resolution or 0.1 # m
        self.max_range = max_range or 2.5 # m
        self.min_range = min_range or 0.2 # m
        self.speed_resolution = speed_resolution or 0.2 # m/s
        self.max_speed = max_speed or 2.0 # m/s
        self.frame_rate = frame_rate or 32 # Hz (I think)
        self.adc_sample_rate_hz = adc_sample_rate_hz or 1000000 # 1,000,000 Hz
        self.bgt_tx_power = bgt_tx_power or 31
        self.rx_antenna_number = rx_antenna_number or self.RX_1
        self.if_gain_db = if_gain_db or 33
        self.center_frequency = center_frequency or 60500000000 # 60,500,000,000 Hz

        self.apply_config()

    def apply_config(self):
        self.__config["lower_frequency_kHz"] = int(0.001 * self.lower_frequency)
        self.__config["upper_frequency_kHz"] = int(0.001 * self.upper_frequency)
        self.__config["num_samples_per_chirp"] = self.num_samples_per_chirp
        self.__config["chirp_to_chirp_time_100ps"] = self.chirp_to_chirp_time_100ps
        self.__config["num_chirps_per_frame"] = self.num_chirps_per_frame
        self.__config["frame_period_us"] = int(1.0e6 / self.frame_rate)
        self.__config["adc_samplerate_Hz"] = self.adc_sample_rate_hz
        self.__config["bgt_tx_power"] = self.bgt_tx_power
        self.__config["rx_antenna_mask"] = self.rx_antenna_number
        self.__config["if_gain_dB"] = self.if_gain_db
    
    @property
    def num_chirps_per_frame(self):
        '''
            The number of bins multiplied with the speed resolution results in the maximum speed. The
            bins of the Doppler transforms represent the -v_max...v_max, that's why the maximum speed
            is divided by 2.

            Doppler transform is an FFT, and usually FFT sizes are powers of 2. If number of samples is
            not a power of two, the FFT input could be zero padded. 
        '''
        num_chirps_per_frame = int(2.0 * self.max_speed / self.speed_resolution)
        return highest_power_of_two(num_chirps_per_frame)


    @property
    def num_samples_per_chirp(self):
        '''
            The number of bins multiplied with the range resolution results in the total range. Due to
            Nyquist theorem only half of the spectrum is evaluated in range transform so the total range
            is reduced by a factor of 2.

            Range transform is an FFT, and usually FFT sizes are powers of 2. If number of samples is
            not a power of two, the FFT input could be zero padded.
        '''
        num_samples_per_chirp = int(2.0 * self.max_range / self.range_resolution)
        return highest_power_of_two(num_samples_per_chirp)

    @property
    def chirp_to_chirp_time_100ps(self):
        '''
            Formula provided by algorithm team, information can be found in some papers
        '''
        return int(1.0e10 * C / (4.0 * self.max_speed * self.center_frequency))

    @property
    def lower_frequency(self):
        return self.center_frequency - int(self.bandwidth * 0.5)

    @property
    def upper_frequency(self):
        return self.center_frequency + int(self.bandwidth * 0.5)

    @property
    def bandwidth(self):
        return C / (2 * self.range_resolution)
    
    @property
    def chirp_length(self):
        return self.num_samples_per_chirp * self.adc_sample_rate_hz

    @property
    def chirp_slope(self):
        return self.bandwidth / self.chirp_length
    
    @property
    def actual_max_range(self):
        '''
            The actual max range will be larger due to increasing num_samples_per_chirp
            to the nearest power of two
        '''
        return self.num_samples_per_chirp * self.range_resolution / 2.0

    @property
    def actual_max_velocity(self):
        '''
            The actual max velocity will be larger due to increasing num_samples_per_chirp
            to the nearest power of two
        '''
        return self.num_chirps_per_frame * self.speed_resolution / 2.0

    @property
    def config_dict(self):
        return self.__config