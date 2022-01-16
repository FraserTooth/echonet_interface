from typing import Optional

from ._base import *
from ..common import *


def parse_now_power(raw_data: str) -> Optional[int]:
    """
    Parse Power
    Signed long int, 4 bytes - 32bits

    :param raw_data: raw_data in hex string
    :return: power in Watts
    """
    power = twos_complement(raw_data, 32)
    if power >= 2147483647:
        raise ValueError("NOW_POWER - Overflow")
    elif power <= -2147483648:
        raise ValueError("NOW_POWER - Underflow")
    elif power == 2147483646:
        return None
    return power


NOW_POWER = SmartMeterEchonetCommand(
    EPC="E7", PDC=READ_PDC, EDT=READ_EDT, parser=parse_now_power
)
