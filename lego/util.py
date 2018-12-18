# -------------------------------------------------------------------------------------------------
# Utility functions that don't depend on any application speific code.
# -------------------------------------------------------------------------------------------------

import logging
from logging import Formatter
from logging.handlers import RotatingFileHandler
import os


__all__ = ['create_log_handler', 'load_stage', 'compare_teams']

# 1 MiB
MB = 1024 * 1024

def create_log_handler(name, level=logging.DEBUG, size=MB, count=5) -> RotatingFileHandler:
    """
    Create a rotating log file handler for use by the application.

    :param name: A string representing the name of the log file without the file extension, e.g.
        'example'.
    :param level: The log level. Should be one of the levels defined by `logging` or the integer
        alternative. Defaults to debug.
    :param size: The maximum size of the log file in bytes. Defaults to 1 MiB.
    :param count: The maximum number of log files to keep. Defaults to 5.

    :return: The logging handler.
    """
    logging.basicConfig(level=level)
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    log_file = '{!s}.log'.format(name)
    log_path = os.path.join(log_dir, log_file)

    formatter = Formatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s '
                          '[in %(pathname)s:%(lineno)d]')

    fh = RotatingFileHandler(log_path, 'a', size, count)
    fh.setLevel(level)
    fh.setFormatter(formatter)

    return fh


def load_stage() -> int:
    """
    Load the current stage.

    :return: An integer representing the current stage:
        - 0: First round
        - 1: Second round
        - 2: Quarter final
        - 3: Semi final
        - 4: Final
    """
    cur_path = os.path.dirname(os.path.abspath(__file__))
    stage_path = os.path.join(cur_path, 'tmp', '.stage')

    with open(stage_path) as fh:
        stage = int(fh.read().strip())

    if stage < 0 or stage > 4:
        msg = 'Invalid value for stage: {!s}. Must be an integer in the range 0-4.'
        raise ValueError(msg.format(stage))

    return stage


def compare_teams(team_1, team_2) -> int:
    """
    Comparison function for comparing teams.
    """
    if team_1 < team_2:
        return 1

    if team_1 > team_2:
        return -1

    return 0
