import logging
import coloredlogs    # type: ignore  # untyped library


FORMAT = '%(name)s [%(levelname)s] %(asctime)s: %(message)s'  #: format for console log messages


def install_logger(logger: logging.Logger, level: int = logging.DEBUG):
    """Set up a colored logging output.

    Args:
        logger  :   The logger to install as a colored logger.
        level   :   The minimum level of messages for them to be displayed in the console logs.

    Both arguments are passed to 'coloredlogs.install'.
    """

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
