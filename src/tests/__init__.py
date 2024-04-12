import logging
from dliswriter.utils.logging import install_colored_logger


for log_name in ('dliswriter', 'tests'):
    logger = logging.getLogger('dliswriter')
    logger.setLevel(logging.DEBUG)
    install_colored_logger(logger)
