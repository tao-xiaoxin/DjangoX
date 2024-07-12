import copy
import importlib
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Dict, List

from django.conf import settings
from loguru import logger


class LoadLoggingConfig(object):
    def __init__(self):
        self.config: Dict = copy.deepcopy(settings.LOGGING)

    @property
    def get_formatters(self) -> Dict:
        return self.config.get("formatters")

    @property
    def get_handlers(self) -> Dict[str, Dict]:
        handlers = self.config.get("handlers")
        for handler_key, handler_value in handlers.items():
            handler_value["formatter"] = self.get_formatters[handler_value["formatter"]]

            filters_key = handler_value.get("filters", None)
            if filters_key is not None:
                handler_value["filters"] = self.get_filters(filters_key)

        return handlers

    def get_filters(self, filter_: List[str]) -> List[Dict]:
        filters = self.config.get("filters")
        return [filters.get(item) for item in filter_ if filters.get(item, None) is not None]


class LevelFilter(logging.Filter):
    def __init__(self, level):
        logging.Filter.__init__(self)
        self.level = level

    def filter(self, record):
        return record.levelno == self.level


class Formatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)

    def format(self, record):
        # 重写format方法
        record.message = record.getMessage()
        record.asctime = self.formatTime(record, self.datefmt)
        return self._fmt % record.__dict__


# class LoguruBaseRotatingHandler(logging.Handler):
#     """
#     A handler class which writes log records to a rotating file.
#     """
#
#     def __init__(self, filename, mode="a", maxBytes=0, backupCount=0, encoding="utf-8", delay=False, errors=None, ):
#         super().__init__()
#         filename = os.path.abspath(filename)
#         filename_suffix = os.path.basename(filename)
#         level, _ = os.path.splitext(filename_suffix)
#         print("level", level)
#         # Map the level from filename or another source to a valid loguru level
#         valid_loguru_levels = {'DEBUG': 'DEBUG', 'INFO': 'INFO', 'WARNING': 'WARNING', 'ERROR': 'ERROR',
#                                'CRITICAL': 'CRITICAL'}
#         loguru_level = valid_loguru_levels.get(level, 'INFO')  # Default to 'INFO' if level is not recognized
#         self._logger = logger.bind(filename=filename_suffix)
#         # 所有已经add的handler
#         handler_names = [handler._name for _, handler in self._logger._core.handlers.items()]
#         _load_config = LoadLoggingConfig()
#         for k, handlers in _load_config.get_handlers.items():
#             print("k", k)
#             if k == level:
#                 if filename == handlers.get("filename", None):
#                     file_handler = RotatingFileHandler(filename, mode, maxBytes, backupCount, encoding, delay, errors)
#                     handler_repr = repr(file_handler)
#                     if handler_repr not in handler_names:
#                         _formatter = handlers["formatter"]
#
#                         formatter_class = logging.Formatter(
#                             _formatter["formats"], datefmt=_formatter.get("datefmt", None)
#                         )
#                         # file_handler.setFormatter(formatter_class)
#
#                         filter_list = handlers["filters"]
#                         for filter_dict in filter_list:
#                             module_path, class_name = filter_dict["()"].rsplit(".", 1)
#                             module = importlib.import_module(module_path)
#                             filter_obj = getattr(module, class_name)(filter_dict["level"])
#                             file_handler.addFilter(filter_obj)
#
#                         """
#                         这个format重置默认的message格式，不然loguru的format会覆盖logging的format [message]字段格式
#                         """
#                         self._logger.add(
#                             file_handler,
#                             enqueue=True,
#                             backtrace=False,
#                             diagnose=True,
#                             format="{message}",
#                         )
#         del _load_config
#         # Add loguru handler with validated or mapped log level
#         self._logger.add(
#             filename,
#             format=settings.LOG_FORMAT,
#             level=loguru_level,
#             rotation=settings.LOG_ROTATION,
#             retention=settings.LOG_RETENTION,
#             enqueue=True,
#             backtrace=settings.LOG_BACKTRACE,
#             diagnose=settings.LOG_DIAGNOSE,
#             encoding=encoding
#         )
#
#     def emit(self, record):
#         """
#         Emit a record.
#         :param record: The record to be emitted.
#         """
#         try:
#             level = self._logger.level(record.levelname).name
#         except ValueError:
#             level = record.levelno
#
#         frame, depth = logging.currentframe(), 2
#         while frame.f_code.co_filename == logging.__file__:
#             frame = frame.f_back
#             depth += 1
#
#         self._logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class LoguruBaseRotatingHandler(logging.Handler):
    def __init__(
            self,
            filename,
            mode="a",
            maxBytes=0,
            backupCount=0,
            encoding="utf-8",
            delay=False,
            errors=None,
    ):
        logging.Handler.__init__(self)
        filename = os.path.abspath(filename)
        filename_suffix = os.path.basename(filename)
        level, _ = os.path.splitext(filename_suffix)

        self._logger = logger.bind(filename=filename_suffix)
        # 所有已经add的handler
        handler_names = [_._name for _, _ in self._logger._core.handlers.items()]
        _load_config = LoadLoggingConfig()
        for k, handlers in _load_config.get_handlers.items():
            if k == level:
                if filename == handlers.get("filename", None):
                    file_handler = RotatingFileHandler(filename, mode, maxBytes, backupCount, encoding, delay, errors)
                    handler_repr = repr(file_handler)
                    if handler_repr not in handler_names:
                        _formatter = handlers["formatter"]

                        formatter_class = logging.Formatter(
                            _formatter["format"], datefmt=_formatter.get("datefmt", None)
                        )
                        file_handler.setFormatter(formatter_class)

                        filter_list = handlers["filters"]
                        for filter_dict in filter_list:
                            module_path, class_name = filter_dict["()"].rsplit(".", 1)
                            module = importlib.import_module(module_path)
                            filter_obj = getattr(module, class_name)(filter_dict["level"])
                            file_handler.addFilter(filter_obj)

                        """
                        这个format重置默认的message格式，不然loguru的format会覆盖logging的format [message]字段格式
                        """
                        self._logger.add(
                            file_handler,
                            enqueue=True,
                            backtrace=False,
                            diagnose=True,
                            format="{message}",
                        )
        del _load_config

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = self._logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        self._logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
