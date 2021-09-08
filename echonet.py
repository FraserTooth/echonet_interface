GET_NOW_POWER = "\x10\x81\x12\x34\x05\xFF\x01\x02\x88\x01\x62\x01\xE7\x01\x01"
GET_EACH30 =   "\x10\x81\x12\x34\x05\xFF\x01\x02\x88\x01\x62\x01\xE2\x00"
GET_NOW_POWER_B = b'\x10\x81\x12\x34\x05\xFF\x01\x02\x88\x01\x62\x01\xE7\x01\x01'
GET_EACH30_B =    b'\x10\x81\x12\x34\x05\xFF\x01\x02\x88\x01\x62\x01\xE2\x00\x03'
GET_STATUS_B =   b'\x10\x81\x12\x34\x05\xFF\x01\x02\x88\x01\x62\x01\x88'
GET_MF_B =   b'\x10\x81\x12\x34\x05\xFF\x01\x02\x88\x01\x62\x01\xE1'


from echonet import *
from config import *

import logging
import datetime

#ロガー取得
logger = logging.getLogger('echonet')

#瞬時電力量ファイル作成処理、表示用処理
def parthE7(line) :
    # 内容が瞬時電力計測値(E7)だったら
    logger.info("pathE7 start")
    hexPower = line[-8:]    # 最後の4バイト（16進数で8文字）が瞬時電力計測値
    power = str(int(hexPower, 16))
    d = datetime.datetime.now()
    filename = WRITE_PATH + POWER_FILE_NAME
    body = "瞬時電力:"+power+"[W]"
    body = body + "(" +d.strftime("%H:%M:%S") + ")"
    # writeFile(filename, body)
    logger.info(body)
    logger.info("pathE7 end")

#積算電力量ファイル作成処理
def parthE2(res,day) :
    logger.info("pathE2 start")
    offset = 8
    pos= offset*48
    line = res[32:32+pos]
    flg = True
    cnt = 0
    body = day + ","
    powerCSV = day + ","
    while flg:
        start = cnt*offset
        intPower = int(line[start:start+offset],16)
        strPower = str(intPower)
        num = len(strPower)
        power = strPower[0:num-1] + "." + strPower[-1:]
        #power = format(strPower[:-1],".",strPower[-1:])
        body = body +  power + ","
        cnt += 1
        if 47 < cnt :
            flg = False
    filename = WRITE_PATH + day + "_" + EACH30_FILE_NAME
    # writeFile(filename, body)
    logger.info(body)
    logger.info("pathE2 end")