import logging

# ロガー取得
logger = logging.getLogger("common")


def all_clear(ser):
    logger.error("all clear start")
    ser.close()
    logger.error("all clear end")


def writeFile(filename, msg):
    logger.info("writeFile start")
    f = open(filename, "w")
    f.write(msg)
    f.close()
    logger.info("writeFile end")


def str2byte(string: str) -> bytes:
    return string.encode()


def byte2str(byte: bytes) -> str:
    return byte.decode()


def int2byte(num: int) -> bytes:
    return bytes.fromhex(f"{num:02x}")
