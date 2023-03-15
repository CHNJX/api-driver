# -*- coding:utf-8 -*-
# @Time     :2022/6/29 17:12
# @Author   :CHNJX
# @File     :custom_str_utils.py
# @Desc     :字符串的自定义方法
import random
import re


class CustomStrUtils:

    @classmethod
    def get_random_num(cls, formal_str):
        """
        获取随机数占位符的范围
        """
        if "random" not in formal_str:
            raise ValueError(
                f'The random placeholder was not found in the incoming parameter: {formal_str}, expect:random(num) or random(num1,num2)')

        # 匹配上 random中的范围
        try:
            random_range = re.match(r'.*{random\((.*?)\)}', formal_str, flags=0).group(1)
            if ',' in random_range:
                return random_range.split(',')
            return int(random_range)
        except Exception as e:
            raise ValueError(
                f'Wrong random number placeholder format：{formal_str}, expected:random(num) or random(num1,num2)')


if __name__ == '__main__':
    CustomStrUtils.get_random_num('{random(1}')
