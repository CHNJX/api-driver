# -*- coding:utf-8 -*-
# @Time     :2022/6/29 10:55
# @Author   :CHNJX
# @File     :placeholder.py
# @Desc     :形参占位符转成实参

PLACEHOLDER_PREFIX = '${'
PLACEHOLDER_SUFFIX = '}'


class Placeholder:
    # 声明占位符的前后缀
    @classmethod
    def resolve_str(cls, text: str, parameter: dict):
        """
        转换字符串中携带的占位符
        """
        if parameter is None or len(parameter) == 0 or text is None or text == '':
            return text
        # 计算占位符的起始位置
        start_index = text.find(PLACEHOLDER_PREFIX)
        while start_index != -1:
            # 获取占位符最后的索引
            end_index = text.find(PLACEHOLDER_SUFFIX, start_index + len(PLACEHOLDER_PREFIX))
            if end_index != -1:
                # 取出要替换的变量名
                formal = text[start_index + len(PLACEHOLDER_PREFIX):end_index]
                # 获取占位符后的索引  一遍往后遍历 替换所有占位符
                next_index = end_index + len(PLACEHOLDER_SUFFIX)
                try:
                    actual = str(parameter[formal])
                    if actual:
                        # 替换占位符
                        text = text.replace('${' + formal + '}', actual)
                        next_index = start_index + len(actual)
                except Exception as e:
                    raise ValueError(
                        "Could not resolve placeholder '" + formal + "' in [" + text + "]: " + e.__str__())
                # 替换一次后 查看后续位置是否存在占位符  继续替换
                start_index = text.find(PLACEHOLDER_PREFIX, next_index)
            else:
                start_index = -1
        return text

    @classmethod
    def resolve_dict(cls, dic: dict, parameter: dict):
        """替换字典中值的占位符"""
        if parameter is None or len(parameter) == 0 or dic is None or len(dic) == 0:
            return dic
        res = {}
        for key, value in dic.items():
            if PLACEHOLDER_PREFIX in value:
                res[key] = cls.resolve_str(value, parameter)
        return res
