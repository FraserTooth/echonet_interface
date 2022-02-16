from enum import Enum
from typing import List, Dict, Optional

import serial
from . import config, actions, common, serial_connection
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


def _get_smart_meter_command(actions_list: List[SmartMeterActions]) -> bytes:
    return (
        actions.REQUEST_FROM_SMART_METER
        + _get_OPC(actions_list)
        + _get_action_subcommands(actions_list)
    )


def get_serial_command(
    actions_list: List[SmartMeterActions], ipv6_address: str
) -> bytes:
    echonet_command = _get_smart_meter_command(actions_list)
    return (
        common.str2byte(
            "SKSENDTO 1 {0} 0E1A 1 {1:04X} ".format(ipv6_address, len(echonet_command))
        )
        + echonet_command
    )


# ロガー取得
logger = logging.getLogger("echonet")


def handle_line(
    ser: serial.Serial, line: str
) -> Optional[dict[SmartMeterActions, str]]:
    # Split into sections
    cols = line.strip().split(" ")
    # Echonet should be the last bit
    echonet_result = cols[-1]
    transaction_id = echonet_result[4 : 4 + 4]
    # Should be the meter 028801
    SEOJ = echonet_result[8 : 8 + 6]
    # Should be us 05FF01
    DEOJ = echonet_result[14 : 14 + 6]
    # Should be 72 for response
    ESV = echonet_result[20 : 20 + 2]
    # Number of responses
    OPC = echonet_result[22 : 22 + 2]

    if SEOJ != "028801":
        logger.error("Response not from meter")
        logger.error("SEOJ:" + SEOJ)
        serial_connection.close_serial_connection(ser)
        raise ValueError("Response not from meter, closed connection...")

    if SEOJ == "028801" and ESV == "72":
        raw_data = {}
        num_responses = int(OPC, 16)
        # Start the response reader at the 24th hex character
        reader_point = 24
        for i in range(num_responses):
            # Get Response Type - EPC
            EPC = echonet_result[reader_point : reader_point + 2]
            reader_point += 2  # Move reading point along to PDC
            # Get Data Size in bytes - PDC
            PDC = echonet_result[reader_point : reader_point + 2]
            reader_point += 2  # Move reading point along to Data
            # Get number of characters needed for data (2 for each byte)
            data_chars = int(common.hex2int(PDC) * 2)
            # Get data string
            data_hex = echonet_result[reader_point : reader_point + data_chars]
            raw_data[EPC] = data_hex
            reader_point += data_chars  # Move reading point along to end of Data

        parsed_data = parse(raw_data)

        logger.info(parsed_data)
        return parsed_data
    else:
        return None


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
