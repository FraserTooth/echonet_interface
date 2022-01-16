from typing import Optional
from dataclasses import dataclass

from ._base import SmartMeterEchonetCommand, READ_EDT, READ_PDC
from ..common import *


@dataclass
class NowCurrentMeasurement:
    r_phase: Optional[float]
    t_phase: Optional[float]


def parse_now_current(raw_data: str) -> NowCurrentMeasurement:
    """
    Parse Current
    Signed short x2, 4 bytes in total, so 16 bits each

    From Appendix_Release_N_E.pdf:
      "This property indicates the measured effective instantaneous R and T phase currents in 0.1A unit."

    :param raw_data: raw_data in hex string
    :return: a tuple of the r_phase and t_phase values
    """
    r_phase_raw = raw_data[0:4]
    t_phase_raw = raw_data[4:8]

    r_phase = twos_complement(r_phase_raw, 16) / 10
    t_phase = twos_complement(t_phase_raw, 16) / 10
    if r_phase >= 3276.7 or t_phase >= 3276.7:
        raise ValueError("NOW_CURRENT - Overflow")
    elif r_phase <= -3276.8 or t_phase <= -3276.8:
        raise ValueError("NOW_CURRENT - Underflow")

    if r_phase == 3276.6:
        r_phase = None
    if t_phase == 3276.6:
        t_phase = None
    return NowCurrentMeasurement(r_phase=r_phase, t_phase=t_phase)


NOW_CURRENT = SmartMeterEchonetCommand(
    EPC="E8", PDC=READ_PDC, EDT=READ_EDT, parser=parse_now_current
)
