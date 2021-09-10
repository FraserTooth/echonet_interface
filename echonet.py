import dataclasses
from enum import Enum
from typing import List, Dict

from config import *

import logging
import datetime
import common

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

GET_NOW_POWER = "\x10\x81\x12\x34\x05\xFF\x01\x02\x88\x01\x62\x01\xE7\x01\x01"
GET_EACH30 = "\x10\x81\x12\x34\x05\xFF\x01\x02\x88\x01\x62\x01\xE2\x00"
GET_INSTANTANEOUS_POWER = REQUEST_FROM_SMART_METER + OPC + b"\xE7" + READ_PDC + READ_EDT
GET_EACH30_B = b"\x10\x81\x12\x34\x05\xFF\x01\x02\x88\x01\x62\x01\xE2\x00\x03"
GET_STATUS_B = b"\x10\x81\x12\x34\x05\xFF\x01\x02\x88\x01\x62\x01\x88"
GET_MF_B = b"\x10\x81\x12\x34\x05\xFF\x01\x02\x88\x01\x62\x01\xE1"


class SmartMeterActions(Enum):
    STATUS = "STATUS"
    # Adjuster to change the values of your measurements, should be COEFFICIENT * measurement, usually "1"
    COEFFICIENT = "COEFFICIENT"
    EFFECTIVE_DIGITS = "EFFECTIVE_DIGITS"
    NOW_CUMULATIVE_IMPORT = "NOW_CUMULATIVE_IMPORT"
    CUMULATIVE_UNIT = "CUMULATIVE_UNIT"
    HH_CUMULATIVE_IMPORT = "HH_CUMULATIVE_IMPORT"
    NOW_CUMULATIVE_EXPORT = "NOW_CUMULATIVE_EXPORT"
    HH_CUMULATIVE_EXPORT = "HH_CUMULATIVE_EXPORT"
    HH_CUMULATIVE_RETRIEVAL_DAY = "HH_CUMULATIVE_RETRIEVAL_DAY"
    NOW_POWER = "NOW_POWER"
    NOW_CURRENT = "NOW_CURRENT"
    LAST_HH_CUMULATIVE_IMPORT = "LAST_HH_CUMULATIVE_IMPORT"
    LAST_HH_CUMULATIVE_EXPORT = "LAST_HH_CUMULATIVE_EXPORT"
    HH_CUMULATIVE_IMPORT_EXPORT = "HH_CUMULATIVE_IMPORT_EXPORT"
    HH_CUMULATIVE_IMPORT_EXPORT_RETRIEVAL_DAY = (
        "HH_CUMULATIVE_IMPORT_EXPORT_RETRIEVAL_DAY"
    )


@dataclasses.dataclass
class SmartMeterEchonetCommand:
    EPC: bytes
    PDC: bytes
    EDT: bytes


"""
Valid EPC registers and their commands for a Smart Meter

See the Echonet appendix "Requirements for low -voltage smart electric energy meter class"
"""
SMART_METER_COMMANDS: Dict[SmartMeterActions, SmartMeterEchonetCommand] = {
    SmartMeterActions.STATUS: SmartMeterEchonetCommand(
        EPC=b"\x80", PDC=READ_PDC, EDT=READ_EDT
    ),
    SmartMeterActions.COEFFICIENT: SmartMeterEchonetCommand(
        EPC=b"\xD3", PDC=READ_PDC, EDT=READ_EDT
    ),
    SmartMeterActions.EFFECTIVE_DIGITS: SmartMeterEchonetCommand(
        EPC=b"\xD7", PDC=READ_PDC, EDT=READ_EDT
    ),
    SmartMeterActions.NOW_CUMULATIVE_IMPORT: SmartMeterEchonetCommand(
        EPC=b"\xE0", PDC=READ_PDC, EDT=READ_EDT
    ),
    SmartMeterActions.CUMULATIVE_UNIT: SmartMeterEchonetCommand(
        EPC=b"\xE1", PDC=READ_PDC, EDT=READ_EDT
    ),
    SmartMeterActions.HH_CUMULATIVE_IMPORT: SmartMeterEchonetCommand(
        EPC=b"\xE2", PDC=READ_PDC, EDT=READ_EDT
    ),
    SmartMeterActions.NOW_CUMULATIVE_EXPORT: SmartMeterEchonetCommand(
        EPC=b"\xE3", PDC=READ_PDC, EDT=READ_EDT
    ),
    SmartMeterActions.HH_CUMULATIVE_EXPORT: SmartMeterEchonetCommand(
        EPC=b"\xE4", PDC=READ_PDC, EDT=READ_EDT
    ),
    SmartMeterActions.HH_CUMULATIVE_RETRIEVAL_DAY: SmartMeterEchonetCommand(
        EPC=b"\xE5", PDC=READ_PDC, EDT=READ_EDT
    ),
    SmartMeterActions.NOW_POWER: SmartMeterEchonetCommand(
        EPC=b"\xE7", PDC=READ_PDC, EDT=READ_EDT
    ),
    SmartMeterActions.NOW_CURRENT: SmartMeterEchonetCommand(
        EPC=b"\xE8", PDC=READ_PDC, EDT=READ_EDT
    ),
    SmartMeterActions.LAST_HH_CUMULATIVE_IMPORT: SmartMeterEchonetCommand(
        EPC=b"\xEA", PDC=READ_PDC, EDT=READ_EDT
    ),
    SmartMeterActions.LAST_HH_CUMULATIVE_EXPORT: SmartMeterEchonetCommand(
        EPC=b"\xEB", PDC=READ_PDC, EDT=READ_EDT
    ),
    SmartMeterActions.HH_CUMULATIVE_IMPORT_EXPORT: SmartMeterEchonetCommand(
        EPC=b"\xEC", PDC=READ_PDC, EDT=READ_EDT
    ),
    SmartMeterActions.HH_CUMULATIVE_IMPORT_EXPORT_RETRIEVAL_DAY: SmartMeterEchonetCommand(
        EPC=b"\xED", PDC=READ_PDC, EDT=READ_EDT
    ),
}


def _get_OPC(actions: List[SmartMeterActions]) -> bytes:
    """
    Gets us our two digit OPC hex string: like 0x01

    :param number: the number we want to convert
    :return: the two digit hex code in bytes
    """
    return common.int2byte(len(actions))


def _get_action_subcommands(actions: List[SmartMeterActions]) -> bytes:
    """
    Turn a list of requested actions into a set of subcommands

    :param actions: the actions we want to perform
    :return: the bytes for the command
    """
    subcommand: bytes = b""
    for action in actions:
        command = SMART_METER_COMMANDS.get(action)
        subcommand += command.EPC + command.PDC + command.EDT
    return subcommand


def get_smart_meter_command(actions: List[SmartMeterActions]) -> bytes:
    return (
        REQUEST_FROM_SMART_METER + _get_OPC(actions) + _get_action_subcommands(actions)
    )


# ロガー取得
logger = logging.getLogger("echonet")

# 瞬時電力量ファイル作成処理、表示用処理
def parseE7(line):
    # 内容が瞬時電力計測値(E7)だったら
    hexPower = line[-8:]  # 最後の4バイト（16進数で8文字）が瞬時電力計測値
    power = str(int(hexPower, 16))
    d = datetime.datetime.now()
    filename = WRITE_PATH + POWER_FILE_NAME
    body = "Instantaneous Power: " + power + "[W]"
    body = body + "(" + d.strftime("%H:%M:%S") + ")"
    # writeFile(filename, body)
    logger.info(body)


# 積算電力量ファイル作成処理
def parseE2(res, day):
    logger.info("pathE2 start")
    offset = 8
    pos = offset * 48
    line = res[32 : 32 + pos]
    flg = True
    cnt = 0
    body = day + ","
    powerCSV = day + ","
    while flg:
        start = cnt * offset
        intPower = int(line[start : start + offset], 16)
        strPower = str(intPower)
        num = len(strPower)
        power = strPower[0 : num - 1] + "." + strPower[-1:]
        # power = format(strPower[:-1],".",strPower[-1:])
        body = body + power + ","
        cnt += 1
        if 47 < cnt:
            flg = False
    filename = WRITE_PATH + day + "_" + EACH30_FILE_NAME
    # writeFile(filename, body)
    logger.info(body)
    logger.info("pathE2 end")
