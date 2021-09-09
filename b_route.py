import serial
import logging.handlers
from config import *
import sys

from common import str2byte, byte2str

logger = logging.getLogger('b-route')

fmt = "%(asctime)s %(levelname)s %(name)s :%(message)s"
logging.basicConfig(level=10, format=fmt)


def connect_to_broute(ser: serial.Serial) -> str:
    # Send B-Route Password
    set_password_command = "SKSETPWD C " + rbpwd + "\r\n"
    ser.write(str2byte(set_password_command))
    logger.info(byte2str(ser.readline()))
    logger.info(byte2str(ser.readline()))

    # Send B-Route ID
    set_id_command = "SKSETRBID " + rbid + "\r\n"
    ser.write(str2byte(set_id_command))
    logger.info(byte2str(ser.readline()))
    logger.info(byte2str(ser.readline()))

    scanDuration = 4  # スキャン時間。
    scan_results = {"Channel": ""}

    while scan_results.get("Channel") == "":
        # アクティブスキャン（IE あり）を行う
        # 時間かかります。10秒ぐらい？
        SKSCAN = "SKSCAN 2 FFFFFFFF " + str(scanDuration) + "\r\n"
        ser.write(str2byte(SKSCAN))

        # スキャン1回について、スキャン終了までのループ
        scanEnd = False
        while not scanEnd:
            line = ser.readline()
            lineStr = byte2str(line)
            logger.info(lineStr)

            if lineStr.startswith("EVENT 22"):
                # スキャン終わったよ（見つかったかどうかは関係なく）
                scanEnd = True
            elif lineStr.startswith("  "):
                # スキャンして見つかったらスペース2個あけてデータがやってくる
                # 例
                #  Channel:39
                #  Channel Page:09
                #  Pan ID:FFFF
                #  Addr:FFFFFFFFFFFFFFFF
                #  LQI:A7
                #  PairID:FFFFFFFF
                cols = lineStr.strip().split(':')
                scan_results[cols[0]] = cols[1]
        scanDuration += 1

        if 14 < scanDuration and not scan_results.has_key("Channel"):
            # 引数としては14まで指定できるが、7で失敗したらそれ以上は無駄っぽい
            logger.error("スキャンリトライオーバー")
            ser.close()
            sys.exit()  #### 糸冬了 ####

    # スキャン結果からChannelを設定。
    SKSREGS2 = "SKSREG S2 " + scan_results["Channel"] + "\r\n"
    ser.write(str2byte(SKSREGS2))
    logger.info(byte2str(ser.readline()))
    logger.info(byte2str(ser.readline()))

    # スキャン結果からPan IDを設定
    SKSREGS3 = "SKSREG S3 " + scan_results["Pan ID"] + "\r\n"
    ser.write(str2byte(SKSREGS3))
    logger.info(byte2str(ser.readline()))
    logger.info(byte2str(ser.readline()))

    # MACアドレス(64bit)をIPV6リンクローカルアドレスに変換。
    # (BP35A1の機能を使って変換しているけど、単に文字列変換すればいいのではという話も？？)
    SKLL64 = "SKLL64 " + scan_results["Addr"] + "\r\n"
    ser.write(str2byte(SKLL64))
    logger.info(byte2str(ser.readline()))
    ipv6_address = byte2str(ser.readline()).strip()

    # PANA 接続シーケンスを開始します。
    SKJOIN = "SKJOIN " + ipv6_address + "\r\n"
    ser.write(str2byte(SKJOIN))
    logger.info(byte2str(ser.readline()))
    logger.info(byte2str(ser.readline()))

    # PANA 接続完了待ち（10行ぐらいなんか返してくる）
    bConnected = False
    while not bConnected:
        line = byte2str(ser.readline())
        if line.startswith("EVENT 24"):
            logger.error("PANA 接続失敗")
            ser.close()
            sys.exit()  #### 糸冬了 ####
        elif line.startswith("EVENT 25"):
            # 接続完了！
            bConnected = True
    return ipv6_address
