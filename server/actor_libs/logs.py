import logging


def create_logger(name, log_level='ERROR'):
    log_level = log_level.upper()
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '[%(asctime)s -- %(name)s -- %(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, log_level))
    return logger

