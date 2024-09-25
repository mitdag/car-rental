import inspect
import os
from datetime import datetime


class Logger:
    def __init__(self, info_file: str, error_file: str):
        self.__info_file__ = info_file
        self.__error_file__ = error_file

    def error(self, message):
        self.__print_to_file__(inspect.stack()[1], self.__error_file__, message)

    def info(self, message):
        self.__print_to_file__(inspect.stack()[1], self.__info_file__, message)

    def __print_to_file__(self, stack, out_file, message):
        caller_file = stack.filename[stack.filename.index("/app/"):]
        now = datetime.utcnow()

        with open(out_file, mode="a+") as log:
            log.write(
                f"{now.strftime('%Y-%m-%d-%H:%M:%S')} -- {caller_file} -- line[{stack.lineno}] -- {message}\n")


current_dir = os.path.dirname(__file__)
logs_path = current_dir[:current_dir.rindex("/")] + "/static/logs/"

logger = Logger(logs_path + "info.txt", logs_path + "error.txt")
