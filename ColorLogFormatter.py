import logging

class ColorFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[98;21m"
    green = "\x1b[92;21m"
    yellow = "\x1b[93;21m"
    red = "\x1b[31;91m"
    bold_red = "\x1b[91;1m"
    reset = "\x1b[0m"
    format = "%(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
