import logging

#ロガー取得
logger = logging.getLogger('common')

def all_clear(ser) :
    logger.error("all clear start")
    ser.close()
    logger.error("all clear end")

def writeFile(filename,msg) :
    logger.info("writeFile start")
    f = open(filename,'w')
    f.write(msg)
    f.close()
    logger.info("writeFile end")

def str2byte(str):
    return str.encode()

def byte2str(byte):
    return byte.decode()