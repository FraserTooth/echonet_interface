from echonet import *
from config import *
from common import *

import sys
import serial
import time
import logging.handlers
import datetime
import atexit

#ロガー取得
logger = logging.getLogger('main')

logname = "data/b-route.log"
fmt = "%(asctime)s %(levelname)s %(name)s :%(message)s"
logging.basicConfig(level=10, format=fmt)
# logging.basicConfig(level=21, filename=logname, format=fmt)


# ログのファイル出力先を設定
#logger.addHandler(fh)


# シリアルポート初期化
ser = serial.Serial(serialPortDev, baudrate=115200)

ser.reset_input_buffer()

if ser.out_waiting > 0:
        ser.reset_output_buffer()
atexit.register(all_clear,ser)
# Bルート認証パスワード設定
SKSETPWD ="SKSETPWD C " + rbpwd + "\r\n"
ser.write(str2byte(SKSETPWD))
logger.info(byte2str(ser.readline()))
logger.info(byte2str(ser.readline()))

# Bルート認証ID設定
SKSETRBID = "SKSETRBID " + rbid + "\r\n"
ser.write(str2byte(SKSETRBID))
logger.info(byte2str(ser.readline()))
logger.info(byte2str(ser.readline()))

scanDuration = 4;   # スキャン時間。
scanRes = {} # スキャン結果の入れ物
scanRes["Channel"]=""

# スキャンのリトライループ（何か見つかるまで）
while scanRes.get("Channel") == "" :
    # アクティブスキャン（IE あり）を行う
    # 時間かかります。10秒ぐらい？
    SKSCAN = "SKSCAN 2 FFFFFFFF " + str(scanDuration) + "\r\n"
    ser.write(str2byte(SKSCAN))

    # スキャン1回について、スキャン終了までのループ
    scanEnd = False
    while not scanEnd :
        line = ser.readline()
        lineStr = byte2str(line)
        logger.info(lineStr)

        if lineStr.startswith("EVENT 22") :
            # スキャン終わったよ（見つかったかどうかは関係なく）
            scanEnd = True
        elif lineStr.startswith("  ") :
            # スキャンして見つかったらスペース2個あけてデータがやってくる
            # 例
            #  Channel:39
            #  Channel Page:09
            #  Pan ID:FFFF
            #  Addr:FFFFFFFFFFFFFFFF
            #  LQI:A7
            #  PairID:FFFFFFFF
            cols = lineStr.strip().split(':')
            scanRes[cols[0]] = cols[1]
    scanDuration+=1

    if 14 < scanDuration and not scanRes.has_key("Channel"):
        # 引数としては14まで指定できるが、7で失敗したらそれ以上は無駄っぽい
        logger.error("スキャンリトライオーバー")
        ser.close()
        sys.exit()  #### 糸冬了 ####

# スキャン結果からChannelを設定。
SKSREGS2 = "SKSREG S2 " + scanRes["Channel"] + "\r\n"
ser.write(str2byte(SKSREGS2))
logger.info(byte2str(ser.readline()))
logger.info(byte2str(ser.readline()))

# スキャン結果からPan IDを設定
SKSREGS3 = "SKSREG S3 " + scanRes["Pan ID"] + "\r\n"
ser.write(str2byte(SKSREGS3))
logger.info(byte2str(ser.readline()))
logger.info(byte2str(ser.readline()))

# MACアドレス(64bit)をIPV6リンクローカルアドレスに変換。
# (BP35A1の機能を使って変換しているけど、単に文字列変換すればいいのではという話も？？)
SKLL64 = "SKLL64 " + scanRes["Addr"] + "\r\n"
ser.write(str2byte(SKLL64))
logger.info(byte2str(ser.readline()))
ipv6Addr = byte2str(ser.readline()).strip()

# PANA 接続シーケンスを開始します。
SKJOIN = "SKJOIN " + ipv6Addr + "\r\n"
ser.write(str2byte(SKJOIN))
logger.info(byte2str(ser.readline()))
logger.info(byte2str(ser.readline()))

# PANA 接続完了待ち（10行ぐらいなんか返してくる）
bConnected = False
while not bConnected :
    line = byte2str(ser.readline())
    if line.startswith("EVENT 24") :
        logger.error("PANA 接続失敗")
        ser.close()
        sys.exit()  #### 糸冬了 ####
    elif line.startswith("EVENT 25") :
        # 接続完了！
        bConnected = True

# シリアル通信のタイムアウトを設定
ser.timeout = 20

# スマートメーターがインスタンスリスト通知を投げてくる
# (ECHONET-Lite_Ver.1.12_02.pdf p.4-16)
logger.info(byte2str(ser.readline()))

DAILY_TASK = False
today = ""
task_cnt = 0
while True :

    #いつもは即時値取得
    if not DAILY_TASK :
        command = "SKSENDTO 1 {0} 0E1A 1 {1:04X} ".format(ipv6Addr, len(GET_INSTANTANEOUS_POWER))
        # コマンド送信
        ser.write(str2byte(command) + GET_INSTANTANEOUS_POWER)
    #初回起動時または、日付が変更されたら前日の30分値を取得
    if DAILY_TASK :
        if task_cnt == 0 :
            logger.debug("task_cnt 0")
            command = "SKSENDTO 1 {0} 0E1A 1 {1:04X} ".format(ipv6Addr, len(GET_EACH30_B))
            # コマンド送信
            ser.write(str2byte(command) + GET_EACH30_B)
        #if task_cnt == 1 :
        #    logger.debug("task_cnt 1")
        #    command = "SKSENDTO 1 {0} 0E1A 1 {1:04X} ".format(ipv6Addr, len(GET_STATUS_B))
        #    # コマンド送信
        #    ser.write(str2byte(command) + GET_STATUS_B)
        #if task_cnt == 2 :
        #    logger.debug("task_cnt 2")
        #    command = "SKSENDTO 1 {0} 0E1A 1 {1:04X} ".format(ipv6Addr, len(GET_MF_B))
        #    # コマンド送信
        #    ser.write(str2byte(command) + GET_MF_B)

    # Read in 3 unused lines
    ser.readline()
    ser.readline()
    ser.readline()

    # The main line we care about
    line = byte2str(ser.readline())         # ERXUDPが来るはず

    # 受信データはたまに違うデータが来たり、
    # 取りこぼしたりして変なデータを拾うことがあるので
    # チェックを厳しめにしてます。
    if line.startswith("ERXUDP") :
        cols = line.strip().split(' ')
        res = cols[8]   # UDP受信データ部分
        #tid = res[4:4+4];
        seoj = res[8:8+6]
        #deoj = res[14,14+6]
        ESV = res[20:20+2]
        #OPC = res[22,22+2]
        # logger.debug("EPC:" + seoj)
        # logger.debug("ESV:" + ESV)
        #エラー処理ここに入ったら落ちる
        if seoj != "028801" :
            logger.error("seoj:" + seoj )
            ser.close()
            sys.exit()  #### 糸冬了 ####

        if seoj == "028801" and ESV == "72" :
            # スマートメーター(028801)から来た応答(72)なら
            EPC = res[24:24+2]
            # logger.debug("EPC:" + EPC)
            if EPC == "E7" :
                # 内容が瞬時電力計測値(E7)だったら
                parseE7(line)
            if EPC == "E2" :
                # 内容が電力計測値(E2)だったら
                d = datetime.datetime.today()
                today = d.strftime("%d")
                d -= datetime.timedelta(days = 1)
                logger.info(today)
                parseE2(res,d.strftime("%Y%m%d"))
                DAILY_TASK = False
                #task_cnt += 1
            #if EPC == "D7" :
            #    task_cnt += 1
            #if EPC == "88" :
            #    DAILY_TASK = False
            #    task_cnt += 0
        time.sleep(1)
ser.close()