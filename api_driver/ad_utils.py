# -*- coding:utf-8 -*-
# @Time     :2023/3/1 11:08
# @Author   :CHNJX
# @File     :ad_utils.py
# @Desc     :public utils
import ast
from os import makedirs
import os
from urllib.parse import unquote
import re


def covert_list_to_dict(list_data):
    """
    将har list data 转换成dict
    :param list_data
        list_data (list)
            [
                {"name": "v", "value": "1"},
                {"name": "w", "value": "2"}
            ]

    :return:
        dict:
            {"v": "1", "w": "2"}
    """
    return {item['name']: item.get('value') for item in list_data}


def convert_x_www_form_to_dict(form_data: str):
    """
    将form表单数据装换成dict字典数据
    :param form_data:  (str): a=1&b=2
    :return: (dict) {"a":1, "b":2}
    """
    if isinstance(form_data, str):
        res_dict = {}
        for kev_value in form_data.split('&'):
            try:
                key, value = kev_value.split('=')
            except ValueError:
                raise Exception(f"错误的 x_www_form_urlencoded 数据: {form_data}")
            # unquote('abc%20def') -> 'abc def'.
            res_dict[key] = unquote(value)
        return res_dict
    else:
        return form_data


def get_class_and_func(api_file, url, method) -> tuple:
    """
    获取到类名和方法名
    :param api_file: 对应api文件
    :param url:     对应请求url
    :param method:  请求方式
    :return:
    """
    api_class = ''
    func_name = ''
    with open(api_file, 'r', encoding='utf-8') as f:
        cd = ast.parse(f.read())
        for item in cd.body:
            if isinstance(item, ast.ClassDef) and item.body:
                for func in item.body:
                    if isinstance(func, ast.FunctionDef):
                        func_str = ast.dump(func)
                        if url in func_str and method.lower() in func_str:
                            pattern = "name='(.*?)'"
                            api_class = re.search(pattern, ast.dump(item)).group(1)
                            func_name = re.search(pattern, ast.dump(func)).group(1)
                            break
    return api_class, func_name


def write(content, file_path):
    """
    将内容写入文档中
    :param content:  要写入的内容
    :param file_path: 文件路径（不存在则会进行创建）
    :return: None
    """
    dir_ = os.path.dirname(file_path)
    if not os.path.exists(dir_):
        os.makedirs(dir_)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def create_folder(path):
    """
    创建目录
    :param path: 目录路径
    :return: None
    """
    makedirs(path)
    print(f'create folder {path}')




