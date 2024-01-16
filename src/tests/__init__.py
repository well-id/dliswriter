import logging
from dlis_writer.utils.logging import install_colored_logger


for log_name in ('dlis_writer', 'tests'):
    logger = logging.getLogger('dlis_writer')
    logger.setLevel(logging.DEBUG)
    install_colored_logger(logger)
