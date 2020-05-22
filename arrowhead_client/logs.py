import logging
import sys
from pathlib import Path

FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler(filename):
    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name, level):
    log_dir = Path.home() / '.arrowhead_system_logs'
    if not log_dir.is_dir():
        Path.mkdir(log_dir)
    log_file_path = Path(log_dir / f'{logger_name}.log')

    if not log_file_path.exists():
        log_file_path.touch()

    logger = logging.getLogger(logger_name)
    if level.lower() == 'debug':
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.addHandler(get_file_handler(log_file_path))

    logger.propagate = False

    logger.info('-------- New instance --------')
    return logger
