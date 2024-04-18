import logging


for log_name in ('dliswriter', 'tests'):
    logger = logging.getLogger('dliswriter')
    logger.setLevel(logging.DEBUG)
