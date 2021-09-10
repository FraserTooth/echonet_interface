import config
import echonet
from common import *
import b_route

import sys
import serial
import time
import logging.handlers
import datetime
import atexit

# ロガー取得
logger = logging.getLogger("main")

fmt = "%(asctime)s %(levelname)s %(name)s :%(message)s"
logging.basicConfig(level=10, format=fmt)

# シリアルポート初期化
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

ipv6_address = b_route.connect_to_broute(ser)

# シリアル通信のタイムアウトを設定
ser.timeout = 20

# スマートメーターがインスタンスリスト通知を投げてくる
# (ECHONET-Lite_Ver.1.12_02.pdf p.4-16)
logger.info(byte2str(ser.readline()))

while True:
    echonet_command = echonet.get_smart_meter_command(
        [echonet.SmartMeterActions.NOW_POWER]
    )

    command = (
        str2byte(
            "SKSENDTO 1 {0} 0E1A 1 {1:04X} ".format(ipv6_address, len(echonet_command))
        )
        + echonet_command
    )
    logger.debug("SENDING")

    # コマンド送信
    ser.write(command)

    line = ""
    # Find the line we care about
    while line.startswith("ERXUDP") is False:
        line = byte2str(ser.readline())
        logger.debug(line)

    logger.debug("FOUND LINE")

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
    logger.debug(f"ESV: {ESV}, OPC: {OPC}")

    if SEOJ != "028801":
        logger.error("Response not from meter")
        logger.error("SEOJ:" + SEOJ)
        ser.close()
        sys.exit()

    if SEOJ == "028801" and ESV == "72":
        data = {}
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
            data_chars = int(hex2int(PDC) * 2)
            # Get data string
            data_hex = echonet_result[reader_point : reader_point + data_chars]
            data[EPC] = data_hex
            reader_point += data_chars  # Move reading point along to end of Data

        logger.debug(data)

        if "E7" in data:
            echonet.parse_E7(data["E7"])
        if "E2" in data:
            # 内容が電力計測値(E2)だったら
            d = datetime.datetime.today()
            today = d.strftime("%d")
            d -= datetime.timedelta(days=1)
            logger.info(today)
            echonet.parseE2(echonet_result, d.strftime("%Y%m%d"))
            DAILY_TASK = False
        time.sleep(1)
ser.close()
