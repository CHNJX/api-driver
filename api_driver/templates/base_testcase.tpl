import os

from api_driver.utils.database_conn import DatabaseConn
from api_driver.utils.service_logger import Logger
from api_driver.testcase_mixin import TestcaseMixin


class TestBase(TestcaseMixin):
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    logger = Logger.getLogger("testcase", base_dir)

    # 需要先获取数据库配置
    # database = DatabaseConn(sql_config)


