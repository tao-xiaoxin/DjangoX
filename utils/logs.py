import copy
import importlib
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Dict, List
from django.conf import settings
from logging import config
from loguru import logger


class LoadLoggingConfig(object):
    def __init__(self):
        self.config: Dict = copy.deepcopy(settings.LOGGING)

    @property
    def get_formatters(self) -> Dict:
        return self.config.get("formatters")

    @property
    def get_handlers(self) -> Dict[str, Dict]:
        hanlders = self.config.get("handlers")
        for _, handler in hanlders.items():
            handler["formatter"] = self.get_formatters[handler["formatter"]]

            filters_key = handler.get("filters", None)
            if filters_key is not None:
                handler["filters"] = self.get_filters(filters_key)

        return hanlders

    def get_filters(self, filter_: List[str]) -> List[Dict]:
        filters = self.config.get("filters")
        return [filters.get(item) for item in filter_ if filters.get(item, None) is not None]


class LevelFilter(logging.Filter):
    def __init__(self, level):
        logging.Filter.__init__(self)
        self.level = level

    def filter(self, record):
        return record.levelno == self.level


class LoguruBaseRotatingHandler(logging.Handler):
    """
    A handler class which writes formatted logging records to disk files.
    """
    def __init__(self, filename, mode="a", maxBytes=0, backupCount=0, encoding="utf-8", delay=False, errors=None, ):
        """
        Open the specified file and use it as the stream for logging.
        :param filename: 指定日志文件名
        :param mode: 写入模式
        :param maxBytes: 文件大小
        :param backupCount: 备份数
        :param encoding: 编码格式
        :param delay: 是否延迟
        :param errors: 错误处理
        """
        logging.Handler.__init__(self)
        filename = os.path.abspath(filename)
        filename_suffix = os.path.basename(filename)
        level, _ = os.path.splitext(filename_suffix)

        self._logger = logger.bind(filename=filename_suffix)
        # 所有已经add的handler
        # noinspection PyUnresolvedReferences,PyProtectedMember
        handler_names = [_._name for _, _ in self._logger._core.handlers.items()]
        _load_config = LoadLoggingConfig()
        for k, handlers in _load_config.get_handlers.items():
            #  通过level来区分不同的handler
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
        """
        Emit a record.
        """
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


def simple_log_injector(conf):
    """
    对内置日志进行反射
    修改默认的logging root输出
    """
    config.dictConfig(conf)
    logging.setLoggerClass(logging.getLogger('django').__class__)
    logging.root = logging.getLogger('django')
