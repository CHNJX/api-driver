# -*- coding:utf-8 -*-
# @Time     :2023/2/3 4:05 下午
# @Author   :CHNJX
# @File     :testcase_mixin.py
# @Desc     :testcase 通用方法

from jsonschema import validate

import json
import logging
import os

from api_driver.utils.custom_str_utils import CustomStrUtils
from api_driver.utils.fake import Fake
from api_driver.utils.placeholder import Placeholder


class TestcaseMixin:
    logger: logging.Logger

    # 将字典中的形参转换成实参
    def replace_formal_dict_2_actual(self, formal_data: dict):
        for key, value in formal_data.items():
            if isinstance(value, str):
                formal_data[key] = self.replace_formal_str_2_actual(value)
            elif isinstance(value, dict):
                self.replace_formal_dict_2_actual(value)
            elif isinstance(value, list):
                self.replace_formal_list_2_actual(value)

    # 将列表中的形参转成实参
    def replace_formal_list_2_actual(self, formal_list: list):
        for i in range(len(formal_list)):
            i_value = formal_list[i]
            if isinstance(i_value, str):
                formal_list.insert(i, self.replace_formal_str_2_actual(i_value))
            elif isinstance(i_value, list):
                self.replace_formal_list_2_actual(i_value)
            elif isinstance(i_value, dict):
                self.replace_formal_dict_2_actual(i_value)

    # 字符串形参替换
    def replace_formal_str_2_actual(self, formal_str):
        if "${random" in formal_str:
            self.logger.info(f'对 {formal_str} 进行占位符替换')
            formal_map = {}
            # 对随机数形参进行替换
            random_range = CustomStrUtils.get_random_num(formal_str)
            if isinstance(random_range, int):
                # 获取到了random范围 生成随机数
                random_num = Fake.get_random_string(random_range)
                # 将形参和实参存到map中
                formal_map[f'random({random_range})'] = random_num
            elif isinstance(random_range, list):
                random_num = Fake.get_range_random(int(random_range[0]), int(random_range[1]))
                # 将形参和实参存到map中
                formal_map[f'random({random_range[0]},{random_range[1]})'] = random_num
            else:
                self.logger.error('随机数占位符替换失败：' + formal_str)
                return formal_str
            return Placeholder.resolve_str(formal_str, formal_map)
        elif "${timeStamp}" in formal_str:
            # 获取时间戳
            ts = Fake.get_time_stamp()
            return Placeholder.resolve_str(formal_str, {'timeStamp': ts})
        else:
            return formal_str

    def assert_schema(self, res, schema_file_dir, schema_file):
        schema = json.loads(open(os.path.join(schema_file_dir, schema_file), 'r', encoding='utf-8').read())
        validate(res, schema)
