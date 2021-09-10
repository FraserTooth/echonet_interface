from dataclasses import dataclass
from typing import Callable, Any

# ECHONET Lite Header
EHD = b"\x10\x81"
# Transaction ID
TID = b"\x12\x34"

# Source ECHONET Lite object specification (see Appendix section "Requirements for controller class")
SEOJ = b"\x05\xFF\x01"
# Destination ECHONET Lite object specification (see Appendix section "Requirements for low -voltage smart electric energy meter class")
DEOJ = b"\x02\x88\x01"

# ECHONET Lite Service Code - Property value read request
ESV = b"\x62"

# Processing Target Property Counters - Can set this higher to request more at a time
OPC = b"\x01"

# ECHONET Lite Property - Defines the register we will be accessing on the device
EPC = ""

# Property data counter - Length of our data send (will usually be 0 for reads)
READ_PDC = b"\x00"

# ECHONET Property Value Data - our data being sent (will usually be 0 for reads)
READ_EDT = b"\x00"

REQUEST_FROM_SMART_METER = EHD + TID + SEOJ + DEOJ + ESV


@dataclass
class SmartMeterEchonetCommand:
    EPC: str
    PDC: bytes
    EDT: bytes
    parser: Callable[[str], Any]
