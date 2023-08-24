import logging
import coloredlogs


FORMAT = '%(name)s [%(levelname)s] %(asctime)s: %(message)s'


def install_logger(logger, level=logging.DEBUG):
    coloredlogs.install(
        logger=logger,
        fmt=FORMAT,
        level=level,
        level_styles={
            'debug': {'color': 35},
            'info': {'color': 74},
            'warning': {'color': 190},
            'error': {'color': 124}
        },
        field_styles={
            'asctime': {'color': 102},
            'name': {'color': 102},
            'levelname': {'color': 231}
        }
    )
