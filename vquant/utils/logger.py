import sys
import logging.handlers

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)


def get_logger(name):
    file_handler = logging.FileHandler('%s.log' % name)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'))
    logger = logging.getLogger(name)
    logger.addHandler(file_handler)
    return logger
