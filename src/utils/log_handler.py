import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

import colorlog

DEFAULT_FOLDER = "./log"
# ===============================================================================================
LOG_LEVEL = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}


# ===============================================================================================
def config_logger(
    file_name=None,
    write_mode="a",
    level="Debug",
    clear_log=False,
    logger_name=None,
    sub_folder=None,
):
    logger = logging.getLogger(logger_name) if logger_name else logging.getLogger()
    logger.setLevel(LOG_LEVEL[level.lower()])

    if not logger.hasHandlers():  # 如果尚未設置處理器
        basic_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s (%(filename)s:%(lineno)s)",
            "%y-%m-%d %H:%M:%S",
        )
        formatter = colorlog.ColoredFormatter(
            "%(asctime)s %(log_color)s [%(levelname)-.4s] %(reset)s %(message)s %(purple)s (%(filename)s:%(lineno)s)",
            "%y-%m-%d %H:%M:%S",
        )

        # 添加流處理器
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(LOG_LEVEL[level.lower()])
        logger.addHandler(stream_handler)

        # 創建日志目錄
        create_day = datetime.now().strftime("%y-%m-%d")
        log_root_path = os.path.join(DEFAULT_FOLDER, create_day)

        if sub_folder:  # 如果指定了子目錄
            log_root_path = os.path.join(log_root_path, sub_folder)

        if not os.path.isdir(log_root_path):
            os.makedirs(log_root_path)

        # 添加文件處理器
        if file_name:
            file_name = os.path.join(log_root_path, file_name)
            if clear_log and os.path.exists(file_name):
                logging.warning("Clearing existing log file")
                os.remove(file_name)

            file_handler = RotatingFileHandler(
                filename=file_name,
                mode=write_mode,
                maxBytes=5 * 1024 * 1024,  # 5MB
                backupCount=2,
                encoding="utf-8",
            )
            file_handler.setFormatter(basic_formatter)
            file_handler.setLevel(LOG_LEVEL[level.lower()])
            logger.addHandler(file_handler)

    return logger


# ===============================================================================================
if __name__ == "__main__":
    import test

    logger = config_logger(
        file_name="ivit-t.log", write_mode="w", level="debug", logger_name="test_logger"
    )
    logger.info("start")

    test.start()
