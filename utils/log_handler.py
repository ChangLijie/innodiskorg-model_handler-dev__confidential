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
def config_logger(log_name=None, write_mode="a", level="Debug", clear_log=False):
    write_mode = "a"
    logger = logging.getLogger()  # get logger
    logger.setLevel(LOG_LEVEL[level])  # set level

    if not logger.hasHandlers():  # if the logger is not setup
        basic_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s (%(filename)s:%(lineno)s)",
            "%y-%m-%d %H:%M:%S",
        )
        formatter = colorlog.ColoredFormatter(
            "%(asctime)s %(log_color)s [%(levelname)-.4s] %(reset)s %(message)s %(purple)s (%(filename)s:%(lineno)s)",
            "%y-%m-%d %H:%M:%S",
        )

        # add stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(LOG_LEVEL[level.lower()])
        logger.addHandler(stream_handler)
        create_day = datetime.now().strftime("%y-%m-%d")
        log_root_path = os.path.join(DEFAULT_FOLDER, create_day)
        if not os.path.isdir(log_root_path):
            os.makedirs(log_root_path)

        # add file handler

        if log_name:
            # Naming Log file
            if clear_log and os.path.exists(log_name):
                logging.warning("Clearing exist log files")
                os.remove(log_name)
            log_name = os.path.join(log_root_path, log_name)
            # log_name = f"{os.path.splitext(log_name)[0]}-{create_day}.log"
            # file_handler = TimedRotatingFileHandler()
            file_handler = RotatingFileHandler(
                filename=log_name,
                mode=write_mode,
                maxBytes=5 * 1024 * 1024,
                backupCount=2,
                encoding="utf-8",
            )
            file_handler.setFormatter(basic_formatter)
            file_handler.setLevel(LOG_LEVEL["info"])
            logger.addHandler(file_handler)

    # logger.info("Create logger.({})".format(logger.name))
    # logger.info(
    #     "Enabled stream {}".format(
    #         f"and file mode.({log_name})" if log_name else "mode"
    #     )
    # )
    return logger


# ===============================================================================================
if __name__ == "__main__":
    import test

    config_logger(log_name="ivit-t.log", write_mode="w", level="debug")

    logging.info("start")

    test.start()
