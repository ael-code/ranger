import logging
from collections import deque

LOG_FORMAT = "[%(levelname)s] %(message)s"
LOG_FORMAT_EXT = "%(asctime)s,%(msecs)d [%(name)s] |%(levelname)s| %(message)s"
LOG_DATA_FORMAT = "%H:%M:%S"


class QueueHandler(logging.Handler):
    """
    This handler store logs events into a queue.
    """

    def __init__(self, queue):
        """
        Initialize an instance, using the passed queue.
        """
        logging.Handler.__init__(self)
        self.queue = queue

    def enqueue(self, record):
        """
        Enqueue a log record.
        """
        self.queue.append(record)

    def emit(self, record):
        self.enqueue(self.format(record))


log_queue = deque(maxlen=1000)
queue_handler = QueueHandler(log_queue)
stderr_handler = logging.StreamHandler()
concise_formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATA_FORMAT)
extended_formatter = logging.Formatter(fmt=LOG_FORMAT_EXT, datefmt=LOG_DATA_FORMAT)


def setup_logging(debug=True):
    """
    All the produced logs using the standard logging function
    will be collected in a queue by the `queue_handler` as well
    as outputted on the standard error `stderr_handler`.

    The verbosity and the format of the log message is
    controlled by the `debug` parameter

     - debug=False:
            a concise log format will be used, debug messsages will be discarded
            and only important message will be passed to the `stderr_handler`

     - debug=True:
            an extended log format will be used, all messages will be processed
            by both the handlers
    """
    if debug:
        # print all logging in extended format
        queue_log_level = logging.DEBUG
        stderr_log_level = logging.DEBUG
        formatter = extended_formatter
    else:
        # print only warning and critical message
        # in a concise format
        queue_log_level = logging.INFO
        stderr_log_level = logging.WARNING
        formatter = concise_formatter

    queue_handler.setLevel(queue_log_level)
    queue_handler.setFormatter(formatter)
    stderr_handler.setLevel(stderr_log_level)
    stderr_handler.setFormatter(formatter)

    main_logger = logging.getLogger()
    # remove all the handlers
    main_logger.handlers = []
    # enable propagation of all log levels
    main_logger.setLevel(0)

    main_logger.addHandler(queue_handler)
    main_logger.addHandler(stderr_handler)
