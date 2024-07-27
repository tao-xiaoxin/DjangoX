from unittest import TestCase
from utils.common import SnowflakeIDWorker

class TestSnowflakeIDWorker(TestCase):
    def test_next_id(self):
        # 使用示例
        snowflake = SnowflakeIDWorker(1, 1)
        for _ in range(100):
            print(snowflake.next_id())
            print(len(str(snowflake.next_id())))
