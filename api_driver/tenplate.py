# -*- coding:utf-8 -*-
# @Time     :2023/2/7 12:45
# @Author   :CHNJX
# @File     :tenplate.py
# @Desc     :模板工具类
import os

from jinja2 import FileSystemLoader, Environment


class Template:
    def __init__(self):
        loader = FileSystemLoader(os.path.join(
            os.path.dirname(__file__), 'templates'))
        self.env = Environment(loader=loader)

    def get_content(self, tpl_name, **kwargs):
        return self.env.get_template(tpl_name).render(**kwargs)
