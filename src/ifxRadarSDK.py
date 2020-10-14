"""Python wrapper for Infineon Radar SDK

The package expects the library (radar_sdk.dll on Windows, libradar_sdk.so on
Linux) either in the same directory as this file (ifxRadarSDK.py) or in a
subdirectory ../../libs/ARCH/ relative to this file where ARCH is depending on
the platform either win32_x86, win32_x64, raspi, or linux_x64.
"""

from ctypes import *
import platform
import platform, os, sys
import numpy as np

# by default,
#   from ifxRadarSDK import *
# would import all objects, including the ones from ctypes. To avoid name space
# pollution, we list what symbols should be exported.
__all__ = ["sdk_version", "sdk_min_version", "error_get", "error_clear", "Frame", "Device", "RadarSDKError"]

# version of sdk, will be initialized in initialize_module()
sdk_version = None

# minimum version of SDK required
sdk_min_version = "1.1.1"

# mapping of error code to the respective exception
error_mapping = {}

def check_version(version):
    """Check that version is at least py_sdk_min_ver"""
    major,minor,patch = version.split(".")
    min_major,min_minor,min_patch = sdk_min_version.split(".")

    if major > min_major:
        return True
    elif major < min_major:
        return False

    if minor > min_minor:
        return True
    elif minor < min_minor:
        return False

    if patch >= min_patch:
        return True
    elif patch < min_patch:
        return False

def find_library():
    """Find path to dll/shared object"""
    system = None
    libname = None
    if platform.system() == "Windows":
        libname = "radar_sdk.dll"
        is64bit = bool(sys.maxsize > 2**32)
        if is64bit:
            system = "win32_x64"
        else:
            system = "win32_x86"
    elif platform.system() == "Linux":
        libname = "libradar_sdk.so"
        machine = os.uname()[4]
        if machine == "x86_64":
            system = "linux_x64"
        elif machine == "armv7l":
            system = "raspi"

    if system == None or libname == None:
        raise RuntimeError("System not supported")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    for reldir in (".", os.path.join("../../../libs/", system)):
        libpath = os.path.join(script_dir, reldir, libname)
        if os.path.isfile(libpath):
            return libpath

    raise RuntimeError("Cannot find " + libname)

# structs
class DeviceConfigStruct(Structure):
    """Wrapper for structure ifx_Device_Config_t"""
    _fields_ = (('num_samples_per_chirp', c_uint32),
                ('num_chirps_per_frame', c_uint32),
                ('adc_samplerate_Hz', c_uint32),
                ('frame_period_us', c_uint64),
                ('lower_frequency_kHz', c_uint32),
                ('upper_frequency_kHz', c_uint32),
                ('bgt_tx_power', c_uint8),
                ('rx_antenna_mask', c_uint8),
                ('tx_mode', c_uint8),
                ('chirp_to_chirp_time_100ps', c_uint64),
                ('if_gain_dB', c_uint8),
                ('frame_end_delay_100ps', c_uint64),
                ('shape_end_delay_100ps', c_uint64),
                ('cb_context', c_void_p))

class MatrixRStruct(Structure):
    _fields_ = (('d', POINTER(c_float)),
                ('rows', c_uint32),
                ('cols', c_uint32),
                ('lda', c_uint32, 31),
                ('owns_d', c_uint8, 1))


class FrameStruct(Structure):
    _fields_ = (('num_rx', c_uint8),
                ('rx_data', POINTER(POINTER(MatrixRStruct))))

FrameStructPointer = POINTER(FrameStruct)
MatrixRStructPointer = POINTER(MatrixRStruct)
DeviceConfigStructPointer = POINTER(DeviceConfigStruct)

def initialize_module():
    """Initialize the module and return ctypes handle"""
    dll = CDLL(find_library())

    dll.ifx_radar_sdk_get_version_string.restype = c_char_p
    dll.ifx_radar_sdk_get_version_string.argtypes = None

    sdk_version = dll.ifx_radar_sdk_get_version_string().decode("ascii")
    if not check_version(sdk_version):
        # exception about non matching dll
        raise RuntimeError("radar SDK is version %s, but required at least %s" % (sdk_version, sdk_min_version))

    # error
    dll.ifx_error_to_string.restype = c_char_p
    dll.ifx_error_to_string.argtypes = [c_int]

    dll.ifx_error_clear.restype = None
    dll.ifx_error_clear.argtypes = None

    dll.ifx_error_get.restype = c_int
    dll.ifx_error_get.argtypes = None

    # device
    dll.ifx_device_create.restype = c_void_p
    dll.ifx_device_create.argtypes = None

    dll.ifx_device_create_by_uuid.restype = c_void_p
    dll.ifx_device_create_by_uuid.argtypes = [POINTER(c_uint8)]

    dll.ifx_device_get_shield_uuid.restype = c_bool
    dll.ifx_device_get_shield_uuid.argtypes = [c_void_p, POINTER(c_uint8)]

    dll.ifx_device_set_config.restype = None
    dll.ifx_device_set_config.argtypes = [c_void_p, DeviceConfigStructPointer]

    dll.ifx_device_destroy.restype = None
    dll.ifx_device_destroy.argtypes = [c_void_p]

    dll.ifx_device_create_frame_from_device_handle.restype = FrameStructPointer
    dll.ifx_device_create_frame_from_device_handle.argtypes = [c_void_p]

    dll.ifx_device_get_next_frame.restype = c_int
    dll.ifx_device_get_next_frame.argtypes = [c_void_p , FrameStructPointer]

    # frame
    dll.ifx_frame_create_r.restype = FrameStructPointer
    dll.ifx_frame_create_r.argtypes = [c_uint8, c_uint32, c_uint32]

    dll.ifx_frame_destroy_r.restype = None
    dll.ifx_frame_destroy_r.argtypes = [FrameStructPointer]

    dll.ifx_frame_get_mat_from_antenna_r.restype = MatrixRStructPointer
    dll.ifx_frame_get_mat_from_antenna_r.argtypes = [FrameStructPointer, c_uint8]

    error_api_base = 0x00010000
    error_dev_base = 0x00011000
    error_app_base = 0x00020000

    # list of all
    errors = {
        error_api_base+0x01: "RadarSDKArgumentNullError",
        error_api_base+0x02: "RadarSDKArgumentInvalidError",
        error_api_base+0x03: "RadarSDKArgumentOutOfBoundsError",
        error_api_base+0x04: "RadarSDKArgumentInvalidExpectedRealError",
        error_api_base+0x05: "RadarSDKArgumentInvalidExpectedComplexError",
        error_api_base+0x06: "RadarSDKIndexOutOfBoundsError",
        error_api_base+0x07: "RadarSDKDimensionMismatchError",
        error_api_base+0x08: "RadarSDKMemoryAllocationFailedError",
        error_api_base+0x09: "RadarSDKInplaceCalculationNotSupportedError",
        error_api_base+0x0A: "RadarSDKMatrixSingularError",
        error_api_base+0x0B: "RadarSDKMatrixNotPositiveDefinitieError",
        error_api_base+0x0C: "RadarSDKNotSupportedError",
        # device related errors
        error_dev_base+0x00: "RadarSDKNoDeviceError",
        error_dev_base+0x01: "RadarSDKDeviceBusyError",
        error_dev_base+0x02: "RadarSDKCommunicationError",
        error_dev_base+0x03: "RadarSDKNumSamplesOutOfRangeError",
        error_dev_base+0x04: "RadarSDKRxAntennaCombinationNotAllowedError",
        error_dev_base+0x05: "RadarSDKIfGainOutOfRangeError",
        error_dev_base+0x06: "RadarSDKSamplerateOutOfRangeError",
        error_dev_base+0x07: "RadarSDKRfOutOfRangeError",
        error_dev_base+0x08: "RadarSDKTxPowerOutOfRangeError",
        error_dev_base+0x09: "RadarSDKChirpRateOutOfRangeError",
        error_dev_base+0x0a: "RadarSDKFrameRateOutOfRangeError",
        error_dev_base+0x0b: "RadarSDKNumChirpsNotAllowedError",
        error_dev_base+0x0C: "RadarSDKFrameSizeNotSupportedError",
        error_dev_base+0x0D: "RadarSDKTimeoutError",
        error_dev_base+0x0E: "RadarSDKFifoOverflowError",
        error_dev_base+0x0F: "RadarSDKTxAntennaModeNotAllowedError"
    }

    for errcode, name in errors.items():
        descr = dll.ifx_error_to_string(errcode).decode("ascii")

        # dynamically generate the class in the modules global scope
        pycode = """
global %s
class %s(RadarSDKError):
    '''%s'''
    def __init__(self):
        super().__init__(%d)
        """ % (name,name,descr,errcode)
        exec(pycode)

        # export the error class
        __all__.append(name)

        # add the class to the list of exceptions
        error_mapping[errcode] = eval(name)

    return dll

class RadarSDKError(Exception):
    def __init__(self, error):
        """Create new RadarSDKException with error code given by error"""
        self.error = error
        self.message = dll.ifx_error_to_string(error).decode("ascii")

    def __str__(self):
        """Exception message"""
        return self.message

dll = initialize_module()


def error_get():
    """Get last SDK error"""
    return dll.ifx_error_get()

def error_clear():
    """Clear SDK error"""
    dll.ifx_error_clear()




def check_rc(error_code=None):
    """Raise an exception if error_code is not IFX_OK (0)"""
    if error_code == None:
        error_code = dll.ifx_error_get()
        error_clear()
    if error_code:
        if error_code in error_mapping:
            raise error_mapping[error_code]()
        else:
            raise RadarSDKError(error_code)


class Frame():
    def __init__(self, num_antennas, num_chirps_per_frame, num_samples_per_chirp):
        """Create frame for time domain data acquisition

        This function initializes a data structure that can hold a time domain
        data frame according to the dimensions provided as parameters.

        If a device is connected then the method Device.create_frame_from_device_handle
        can be used instead of this function, as that function reads the
        dimensions from configured the device handle.

        Parameters:
            num_antennas            Number of virtual active Rx antennas configured in the device
            num_chirps_per_frame    Number of chirps configured in a frame
            num_samples_per_chirp   Number of chirps configured in a frame
        """
        self.handle = dll.ifx_frame_create_r(num_antennas, num_chirps_per_frame, num_samples_per_chirp)
        check_rc()

    @classmethod
    def create_from_pointer(cls, framepointer):
        """Create Frame from FramePointer"""
        self = cls.__new__(cls)
        self.handle = framepointer
        return self

    def __del__(self):
        """Destroy frame handle"""
        if hasattr(self, "handle"):
            dll.ifx_frame_destroy_r(self.handle)

    def get_num_rx(self):
        """Return the number of virtual active Rx antennas in the radar device"""
        return self.handle.contents.num_rx

    def get_mat_from_antenna(self, antenna, copy=True):
        """Get matrix from antenna

        If copy is True, a copy of the original matrix is returned. If copy is
        False, the matrix is not copied and the matrix must *not* be used after
        the frame object has been destroyed.

        Parameters:
            antenna     number of antenna
            copy        if True a copy of the matrix will be returned
        """
        # we don't have to free mat because the matrix is saved in the frame
        # handle.
        # matrices are in C order (row major order)
        mat = dll.ifx_frame_get_mat_from_antenna_r(self.handle, antenna)
        d = mat.contents.d
        shape = (mat.contents.rows, mat.contents.cols)
        return np.array(np.ctypeslib.as_array(d, shape), order="C", copy=copy)


class Device():
    def __init__(self, uuid=None):
        """Create new device

        Search for a Infineon radar sensor device connected to the host machine
        and connects to the first found sensor device.

        The device is automatically closed by the destructor. If you want to
        close the device yourself, you can use the keyword del:
            device = Device()
            # do something with device
            ...
            # close device
            del device

        Optional parameters:
            uuid:       open the radar device with unique id given by uuid
                        the uuid is represented as a 32 character string of
                        hexadecimal characters. In addition, the uuid may
                        contain dash characters (-) which will be ignored.
                        Both examples are valid and correspond to the same
                        uuid:
                            0123456789abcdef0123456789abcdef
                            01234567-89ab-cdef-0123-456789abcdef
        """
        if uuid == None:
            self.handle = dll.ifx_device_create()
        else:
            # remove - from uuid
            uuid = uuid.replace("-", "")

            try:
                uuid_bytes = [int(uuid[i:i + 2],16) for i in range(0, len(uuid), 2)]
            except ValueError:
                raise ValueError("uuid is not a valid unique id")

            uuid_array = c_uint8 *16
            c_array = uuid_array(*uuid_bytes)
            self.handle = dll.ifx_device_create_by_uuid(c_array)

        # check return code
        check_rc()

    def set_config(self,
               num_samples_per_chirp = 64,
               num_chirps_per_frame = 32,
               adc_samplerate_Hz = 2000000,
               frame_period_us = 0,
               lower_frequency_kHz = 58000000,
               upper_frequency_kHz = 63000000,
               bgt_tx_power = 31,
               rx_antenna_mask = 7,
               tx_mode = 0,
               chirp_to_chirp_time_100ps = 1870000,
               if_gain_dB = 33,
               frame_end_delay_100ps = 400000000,
               shape_end_delay_100ps = 1500000):
        """Configure device and start acquisition of time domain data

        The board is configured according to the parameters provided
        through config and acquisition of time domain data is started.

        Parameters:
            num_samples_per_chirp:
                This is the number of samples acquired during each chirp of a
                frame. The duration of a single chirp depends on the number of
                samples and the sampling rate.

            num_chirps_per_frame:
                This is the number of chirps a single data frame consists of.

            adc_samplerate_Hz:
                This is the sampling rate of the ADC used to acquire the
                samples during a chirp. The duration of a single chirp depends
                on the number of samples and the sampling rate.

            frame_period_us:
                This is the time period that elapses between the beginnings of
                two consecutive frames. The reciprocal of this parameter is
                the frame rate.

            lower_frequency_kHz:
                This is the start frequency of the FMCW frequency ramp.

            upper_frequency_kHz:
                This is the end frequency of the FMCW frequency ramp.

            bgt_tx_power:
                This value controls the power of the transmitted RX signal.
                This is an abstract value between 0 and 31 without any
                physical meaning. Refer to BGT60TR13AIP data sheet do
                learn more about the TX power BGT60TR13AIP is capable of.

            rx_antenna_mask:
                In this mask each bit represents one RX antenna of
                BGT60TR13AIP. If a bit is set the according RX antenna is
                enabled during the chirps and the signal received through that
                antenna is captured.

            tx_mode:
                This is relevant only for devices with 2 TX antennas.
                (BGT60ATR24C). For BGT60TR13AIP this value should be 0 (also default)
                Possible values are
                    0 -> only Tx 1 is transmitting for all chirps (Default)
                    1 -> only Tx 2 is transmitting for all chirps
                    2 -> Time-division multiplex, alternating between Tx 1 and
                         Tx 2 on each transmitted chirp (only BGT60ATR24C)

            chirp_to_chirp_time_100ps:
                This is the time period that elapses between the beginnings of two
                consecutive chirps in a frame.

            if_gain_dB:
                This is the amplification factor that is applied to the IF signal
                coming from the RF mixer before it is fed into the ADC.

            frame_end_delay_100ps:
                This parameter defines the delay after each frame in 100
                picoseconds steps. In order to set this value frame_period_us must
                be set to 0, otherwise this value will be ignored.

            shape_end_delay_100ps:
                This parameter defines the delay after each shape in 100
                picoseconds steps. In order to set this value
                chirp_to_chirp_time_100ps must be set to 0, otherwise this value
                will be ignored.
        """
        config = DeviceConfigStruct(num_samples_per_chirp,
                                    num_chirps_per_frame,
                                    adc_samplerate_Hz,
                                    frame_period_us,
                                    lower_frequency_kHz,
                                    upper_frequency_kHz,
                                    bgt_tx_power,
                                    rx_antenna_mask,
                                    tx_mode,
                                    chirp_to_chirp_time_100ps,
                                    if_gain_dB,
                                    frame_end_delay_100ps,
                                    shape_end_delay_100ps)
        dll.ifx_device_set_config(self.handle, byref(config))
        check_rc()

    def get_next_frame(self, frame):
        """Retrieve next frame of time domain data from device

        Retrieve the next complete frame of time domain data from the connected
        device. The samples from all chirps and all enabled RX antennas will be
        copied to the provided data structure frame.
        """
        ret = dll.ifx_device_get_next_frame(self.handle, frame.handle)
        check_rc(ret)

    def create_frame_from_device_handle(self):
        """Create frame for time domain data acquisition

        This method checks the current configuration of the specified sensor
        device and initializes a data structure that can hold a time domain
        data frame according acquired through that device.
        """
        frame_p = dll.ifx_device_create_frame_from_device_handle(self.handle)
        check_rc()
        return Frame.create_from_pointer(frame_p)

    def get_shield_uuid(self):
        """Get the unique id for the radar shield"""
        uuid_array = c_uint8 *16
        c_array = uuid_array()
        if dll.ifx_device_get_shield_uuid(self.handle, c_array):
            uuid = ""
            for x in c_array:
                uuid += "%02x" % x
            return uuid
        else:
            return None

    def __del__(self):
        """Destroy device handle"""
        if hasattr(self, "handle"):
            dll.ifx_device_destroy(self.handle)
