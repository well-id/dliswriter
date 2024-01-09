__version__ = '0.0.5'

import logging
from dlis_writer.utils.logging import install_logger


dlis_logger = logging.getLogger('dlis_writer')
dlis_logger.setLevel(logging.DEBUG)
install_logger(dlis_logger)
