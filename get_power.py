import src.echonet as echonet
from src.common import byte2str, str2byte, hex2int
import src.b_route as b_route
from src.serial_connection import connect_to_serial_port
import sys
import time
import logging.handlers

# ロガー取得
logger = logging.getLogger("main")

fmt = "%(asctime)s %(levelname)s %(name)s :%(message)s"
logging.basicConfig(level=10, format=fmt)

ser = connect_to_serial_port()
ipv6_address = b_route.connect_to_broute(ser)

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

    # コマンド送信
    ser.write(command)

    line = ""
    # Find the line we care about
    while line.startswith("ERXUDP") is False:
        line = byte2str(ser.readline())

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
        ser.close()
        sys.exit()

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
            data_chars = int(hex2int(PDC) * 2)
            # Get data string
            data_hex = echonet_result[reader_point : reader_point + data_chars]
            raw_data[EPC] = data_hex
            reader_point += data_chars  # Move reading point along to end of Data

        parsed_data = echonet.parse(raw_data)

        logger.info(parsed_data)
    time.sleep(10)
