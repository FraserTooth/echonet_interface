import meter.echonet as echonet
from meter.common import byte2str, hex2int
import meter.b_route as b_route
from meter.serial_connection import connect_to_serial_port
import time
import logging.handlers
import meter.influx as db

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
    command = echonet.get_serial_command(
        [echonet.SmartMeterActions.NOW_POWER], ipv6_address
    )

    # Send Command
    ser.write(command)

    line = ""
    # Find the line we care about
    while line.startswith("ERXUDP") is False:
        line = byte2str(ser.readline())
        if len(line) == 0:
            # Serial Connection has Hung
            print("Looks like we've hung...")
            break

    if len(line) > 0:
        try:
            data = echonet.handle_line(ser, line)
            if data is not None:
                db.write_to_influx(data)
        except ValueError:
            # Reconnect
            ser = connect_to_serial_port()
            ipv6_address = b_route.connect_to_broute(ser)

    time.sleep(3)
