# -*- coding:utf-8 -*-
# @Time     :2023/2/3 7:48 上午
# @Author   :CHNJX
# @File     :service_logger.py
# @Desc     :日志构造器

import logging
import os
import sys
import time
from datetime import datetime


class Logger:

    @classmethod
    def getLogger(cls, name, root_path, package_name="log") -> logging:
        logger = logging.getLogger(name)
        if logger.handlers:
            return logger
        logger.setLevel(logging.DEBUG)
        now_string = datetime.now().strftime('%Y%m%d')
        file_name = f'{now_string}_log.log'
        logger_dir = os.path.join(root_path, package_name)
        if not os.path.exists(logger_dir):
            os.mkdir(logger_dir)
        file_path = os.path.join(logger_dir, file_name)
        t = int(time.time())

        # FileHandler
        fh = logging.FileHandler(file_path, mode='a', encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '******%(asctime)s - %(name)s - %(filename)s,line %(lineno)s - %(levelname)s: %(message)s')
        fh.setFormatter(formatter)

        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(formatter)
        sh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
        logger.addHandler(sh)

        return logger
