import logging
import sys
from flask.logging import default_handler as default_flask_handler

FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return  console_handler

def get_file_handler(filename):
    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(FORMATTER)
    return file_handler

def get_logger(logger_name, level):
    file_name = f'logs/{logger_name}.log'
    logger = logging.getLogger(logger_name)
    if level.lower() == 'debug':
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler(file_name))

    logger.propagate = False

    logger.info('-------- New instance --------')
    return logger
