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


def hex2byte(hex: str) -> bytes:
    return bytes.fromhex(hex)


def byte2str(byte: bytes) -> str:
    return byte.decode()


def int2byte(num: int) -> bytes:
    return bytes.fromhex(f"{num:02x}")


def hex2int(hex: str) -> int:
    return int(hex, 16)


def twos_complement(hex: str, bits: int) -> int:
    """compute the 2's complement of int value val"""
    val = int(hex, 16)
    if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)  # compute negative value
    return val  # return positive value as is
