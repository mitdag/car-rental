import inspect
import os
from datetime import datetime
from pathlib import Path


class Logger:
    def __init__(self, info_file: str, error_file: str):
        self.__info_file__ = info_file
        self.__error_file__ = error_file

    def error(self, message):
        self.__print_to_file__(inspect.stack()[1], self.__error_file__, message)

    def info(self, message):
        self.__print_to_file__(inspect.stack()[1], self.__info_file__, message)

    def __print_to_file__(self, stack, out_file, message):
        caller_file = Path(stack.filename)
        try:
            caller_file = caller_file.relative_to("/app")
        except ValueError:
            caller_file = caller_file.name

        now = datetime.utcnow()

        out_file_path = Path(out_file)
        out_file_path.parent.mkdir(parents=True, exist_ok=True)

        with out_file_path.open(mode="a", encoding="utf-8") as log:
            log.write(
                f"{now:%Y-%m-%d %H:%M:%S} -- {caller_file} -- line[{stack.lineno}] -- {message}\n"
            )


current_dir = Path(os.path.dirname(__file__)).as_posix()
logs_path = current_dir[: current_dir.rindex("/")] + "../../logs/"

logger = Logger(logs_path + "info.txt", logs_path + "error.txt")
