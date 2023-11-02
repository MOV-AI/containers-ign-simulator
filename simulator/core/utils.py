import logging

class StdoutLogger(logging.Logger):
    """To avoid other tasks/processes messing with logging module
    use this instead"""

    def __init__(self, name: str, log_level=None):
        logging.Logger.__init__(self, name=name)

        self._handler = logging.StreamHandler(sys.stdout)
        if log_level is None:
            log_level = os.getenv("LOG_LEVEL", "INFO").upper()

        self._handler.setLevel(level=log_level)

    def handle(self, record):
        self._handler.emit(record)