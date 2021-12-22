import src.config as config

import serial
import atexit

from src.common import all_clear


def connect_to_serial_port() -> serial.Serial:
    # Connect to USB
    try:
        ser = serial.Serial(config.serialPortDev, baudrate=115200)
    except Exception as e:
        raise ValueError(
            f"Error opening the serial port, your serialPortDev config ({config.serialPortDev}) is probably wrong.\n{e}"
        )

    ser.reset_input_buffer()

    if ser.out_waiting > 0:
        ser.reset_output_buffer()
    atexit.register(all_clear, ser)

    # Set a Timeout of 20 seconds
    ser.timeout = 20

    return ser
