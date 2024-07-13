import logging
from loguru import logger

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # 获取 `loguru` 级别，如果它存在
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 查找调用者的位置
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

# 移除所有默认的 logging 处理程序
# for handler in logging.root.handlers[:]:
#     logging.root.removeHandler(handler)

# 添加 InterceptHandler 使 `logging` 模块使用 `loguru`
logging.basicConfig(handlers=[InterceptHandler()], level=0)

# 配置 loguru
logger.add("file.log", rotation="500 MB", level="DEBUG")

# 检查 loguru 是否正确输出
logger.debug("这是一个调试消息")
logger.info("这是一个信息消息")
logger.warning("这是一个警告消息")
logger.error("这是一个错误消息")
logger.critical("这是一个关键消息")

# 使用 logging 记录日志，应该被 loguru 捕获并输出
logging.debug("这是一个 logging 调试消息")
logging.info("这是一个 logging 信息消息")
logging.warning("这是一个 logging 警告消息")
logging.error("这是一个 logging 错误消息")
logging.critical("这是一个 logging 关键消息")
