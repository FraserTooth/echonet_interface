from enum import Enum
from typing import List, Dict

from . import config, actions, common
import logging


GET_NOW_POWER = "\x10\x81\x12\x34\x05\xFF\x01\x02\x88\x01\x62\x01\xE7\x01\x01"
GET_EACH30 = "\x10\x81\x12\x34\x05\xFF\x01\x02\x88\x01\x62\x01\xE2\x00"
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


"""
Valid EPC registers and their commands for a Smart Meter

See the Echonet appendix "Requirements for low -voltage smart electric energy meter class"
"""
SMART_METER_COMMANDS: Dict[SmartMeterActions, actions.SmartMeterEchonetCommand] = {
    SmartMeterActions.NOW_POWER: actions.NOW_POWER,
    SmartMeterActions.NOW_CURRENT: actions.NOW_CURRENT,
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
        subcommand += common.hex2byte(command.EPC) + command.PDC + command.EDT
    return subcommand


def get_smart_meter_command(actions_list: List[SmartMeterActions]) -> bytes:
    return (
        actions.REQUEST_FROM_SMART_METER
        + _get_OPC(actions_list)
        + _get_action_subcommands(actions_list)
    )


# ロガー取得
logger = logging.getLogger("echonet")


def parse(raw_data: Dict[str, str]) -> Dict[SmartMeterActions, str]:
    parsed_data = {}
    # Find the element and run the parser
    for epc in raw_data:
        for action_name in SMART_METER_COMMANDS:
            action = SMART_METER_COMMANDS[action_name]
            if action.EPC == epc:
                parsed_data[action_name] = action.parser(raw_data[epc])
    return parsed_data


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
    filename = config.WRITE_PATH + day + "_" + config.EACH30_FILE_NAME
    # writeFile(filename, body)
    logger.info(body)
    logger.info("pathE2 end")
