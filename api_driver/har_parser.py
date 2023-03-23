# -*- coding:utf-8 -*-
# @Time     :2023/2/28 18:30
# @Author   :CHNJX
# @File     :har_parser.py
# @Desc     :har parse code
import base64
import json
import logging
import os
import re
import sys
from json import JSONDecodeError
from urllib.parse import urlparse

from api_driver.template import Template
from api_driver import ad_utils

# 忽略的请求头
IGNORE_REQUEST_HEADERS = [
    "host",
    "accept",
    "content-length",
    "connection",
    "accept-encoding",
    "accept-language",
    "origin",
    "referer",
    "cache-control",
    "pragma",
    "cookie",
    "upgrade-insecure-requests",
    ":authority",
    ":method",
    ":scheme",
    ":path",
    "sec-ch-ua",
    'sec-ch-ua-platform',
    'sec-fetch-dest',
    'sec-fetch-mode',
    'sec-fetch-site',
    'x-requested-with',
    'sec-ch-ua-mobile'
]


class HarParser:

    def __init__(self, har_file_path: str, exclude_url: str = None, api_object: str = None):
        if '/' not in har_file_path and '\\' not in har_file_path:
            har_file_path = 'har/' + har_file_path
        self.har_file = har_file_path
        self.exclude_url = exclude_url or ""
        self.api_class = ''
        self.func_name = ''
        self.module_dir = []
        self.api_object = api_object.replace('\\', '/', -1) if api_object else None

    def load_har_2_entry_json(self) -> list[dict]:
        """
        load har data
        :return:
            list: entries
            [
                {
                    "request": {},
                    "response": {}
                },
                {
                    "request": {},
                    "response": {}
                }
            ]
        """
        with open(self.har_file, 'r+', encoding='utf-8') as f:
            try:
                entry_json = json.loads(f.read())
                return entry_json['log']['entries']
            except (KeyError, TypeError):
                sys.exit(1)

    def __make_step_validate(self, step_dict, entry_json):
        """
        解析har数据 组装断言需要的数据
        :return:
            {
                "validate":[
                    {"equals": ['key1','expected1']}
                    {"in": ['key2','expected2']}
                ]
            }
        """
        # 对响应状态码进行断言
        step_dict["validate"].append(
            {"equals": ["status_code", entry_json["response"].get("status")]}
        )

        resp_content_dict = entry_json['response'].get('content')

        # 对请求头进行断言
        headers = ad_utils.covert_list_to_dict(entry_json['response'].get('headers', []))
        if 'Content-Type' in headers:
            step_dict["header_validate"].append(
                {"equals": ["Content-Type", headers["Content-Type"]]}
            )

        text = resp_content_dict.get("text")
        if not text:
            return
        mime_type: str = resp_content_dict.get("mimeType")
        # 根据编码格式对text内容进行解码
        if mime_type and mime_type.startswith('application/json'):
            encoding = resp_content_dict.get('encoding')
            if encoding and encoding == 'base64':
                content = base64.b64decode(text).decode('utf-8')
            else:
                content = text
            try:
                resp_content_json = json.loads(content)
            except JSONDecodeError:
                logging.warning(
                    "响应无法转换成json格式: {}".format(content.encode("utf-8"))
                )
                return

            if not isinstance(resp_content_json, dict):
                return
            for key, value in resp_content_json.items():
                if isinstance(value, (dict, list)):
                    continue
                if key == 'timestamp':
                    continue
                step_dict["json_validate"].append(
                    {"equals": [key, value]}
                )

    def __make_request_data(self, step_dict: dict, entry_json: dict):
        """
        将har中请求数据进行封装
        :param entry_json:
            entry_json (dict):
                {
                    "request": {
                        "method": "POST",
                        "postData": {
                            "mimeType": "application/x-www-form-urlencoded; charset=utf-8",
                            "params": [
                                {"name": "a", "value": 1},
                                {"name": "b", "value": "2"}
                            }
                        },
                    },
                    "response": {...}
                }

        :returns:
            {
                "request": {
                    "method": "POST",
                    "data": {"v": "1", "w": "2"}
                }
            }
        """
        method = entry_json['request'].get('method')
        # 判断请求是否通过body进行传输
        if method in ['POST', 'PUT', 'PATCH']:
            post_data = entry_json['request'].get('postData', {})
            mimetype: str = post_data.get('mimeType')

            if 'text' in post_data:
                data = post_data.get('text')
            else:
                params = post_data.get('params', [])
                data = ad_utils.covert_list_to_dict(params)
            request_data_key = 'data'
            # 判断是表单还是json
            if not mimetype:
                pass
            elif mimetype.startswith("application/json"):
                try:
                    data = json.loads(data)
                    request_data_key = 'json'
                except JSONDecodeError:
                    pass
            elif mimetype.startswith("application/x-www-form-urlencoded"):
                data = ad_utils.convert_x_www_form_to_dict(data)

            step_dict['request'][request_data_key] = data

    def __make_request_method(self, step_dict, entry_json):
        """
        获取har中的请求方式
        """
        method = entry_json["request"].get("method")
        if not method:
            logging.exception("method missed in request.")
            sys.exit(1)
        step_dict['request']['method'] = method

    def __make_request_headers(self, step_dict: dict, entry_json: dict):
        """
        获取har中对应header数据
        :param entry_json:
           entry_json (dict):
               {
                   "request": {
                       "headers": [
                           {"name": "Host", "value": "httprunner.top"},
                           {"name": "Content-Type", "value": "application/json"},
                           {"name": "User-Agent", "value": "iOS/10.3"}
                       ],
                   },
                   "response": {}
               }

           :return:
               {
                   "request": {
                       headers: {"Content-Type": "application/json"}
               }

        """
        step_headers = {}
        for header in entry_json['request'].get('headers', []):
            if header['name'].lower() in IGNORE_REQUEST_HEADERS:
                # 直接忽略不进行处理
                continue
            step_headers[header['name']] = header['value']
        if step_headers:
            step_dict['request']['headers'] = step_headers

    def __make_request_url(self, step_dict: dict, entry_json: dict):
        """
        将json数据中url的信息进行提取
        :param entry_json:
            entry_json (dict):
                    {
                        "request": {
                            "url": "https://httprunner.top/home?v=1&w=2",
                            "queryString": [
                                {"name": "v", "value": "1"},
                                {"name": "w", "value": "2"}
                            ],
                        },
                        "response": {}
                    }

        :return:
            {
                "name: "/home",
                "request": {
                    url: "https://httprunner.top/home",
                    params: {"v": "1", "w": "2"}
                }
            }
        """
        # 将url携带的参数进行分离
        url_params = ad_utils.covert_list_to_dict(entry_json["request"].get("queryString", []))
        url = entry_json['request'].get('url')
        if not url:
            logging.exception('请求缺少url信息')
            sys.exit(1)
        # 将url进行拆解
        parse_url = urlparse(url)
        if url_params:
            parse_url = parse_url._replace(query='')  # 清除url上的参数
            step_dict["request"]["url"] = parse_url.geturl()
            step_dict["request"]["params"] = url_params
        else:
            step_dict["request"]["url"] = parse_url.geturl()
        step_dict['name'] = parse_url.path

    def _gen_step(self, entry_json) -> dict:
        """
        将entry_json 转换成测试步骤需要用的的数据
        :param entry_json:
            entry_json (dict):
                    {
                        "request": {
                            "method": "POST",
                            "url": "https://httprunner.top/api/v1/Account/Login",
                            "headers": [],
                            "queryString": [],
                            "postData": {},
                        },
                        "response": {
                            "status": 200,
                            "headers": [],
                            "content": {}
                        }
                    }
        :return:
        """
        step_dict = {
            "name": "",
            "request": {},
            "validate": [],
            "json_validate": [],
            "header_validate": []
        }
        self.__make_request_url(step_dict, entry_json)
        self.__make_request_headers(step_dict, entry_json)
        self.__make_request_method(step_dict, entry_json)
        self.__make_request_data(step_dict, entry_json)
        self.__make_step_validate(step_dict, entry_json)

        return step_dict

    def generate_testcase_steps(self, fmt_version) -> list:
        """
        封装测试用例步骤
        :param fmt_version:
        :return:
        """

        def is_exclude_url(url, exclude_url: str) -> bool:
            """查看是否为剔除的url"""
            exclude_url_list = exclude_url.split('|')
            for exclude in exclude_url_list:
                if exclude and exclude in url:
                    return True
            return False

        entry_json = self.load_har_2_entry_json()
        test_steps = []
        # 去除不需要的url
        for entry in entry_json:
            url = entry["request"].get("url")
            if is_exclude_url(url, self.exclude_url):
                continue
            test_steps.append(self._gen_step(entry))
        return test_steps

    def _make_testcase(self, case_name: str, fmt_version: str) -> str:
        """
        :param fmt_version: 用例版本
        :return: 通过模板对用例转换后的内容
        """
        # 先把需要的用例步骤进行解析
        testcase_steps = self.generate_testcase_steps(fmt_version)
        testcase = {
            'model_name': case_name.capitalize(),
            'case_name': case_name,
            'testcase_steps': testcase_steps
        }
        temp = Template()
        if self.api_object:
            self.generate_api_case(testcase_steps)
            testcase['module_dir_list'] = set(self.module_dir)
            return temp.get_content('har2api_case.tpl', **testcase)
        return temp.get_content('har2case.tpl', **testcase)

    def find_object_func(self, url: str, method: str) -> dict:
        """
        根据url和请求方法获取到对应的接口
        :param url: 接口路径
        :param method: 请求方法
        :return: {'api_class': self.api_class, 'func_name': self.func_name, 'module_dir': self.module_dir}
        """
        url_list = url.split('/')
        url = '/'.join([url_list[-2], url_list[-1]])
        if not os.path.exists(self.api_object):
            logging.exception('api-object 路径有误')
            sys.exit(1)
        self.travel_api_object(self.api_object, url, method)
        api_func = {'api_class': self.api_class, 'func_name': self.func_name}
        self.api_class = ''
        self.func_name = ''
        return api_func

    def travel_api_object(self, api, url, method):
        """遍历目录获取对应的api"""
        if self.api_class or self.func_name:
            return
        if os.path.isfile(api):
            api = api.replace('\\', '/', -1)
            self.api_class, self.func_name = ad_utils.get_class_and_func(api, url, method)
            if self.api_class and self.func_name:
                file_path = re.search('api_object/(.*?).py', api).group(1)
                # 获取包路径
                file_path_list = file_path.split('/') if '/' in file_path else [file_path]
                self.module_dir.append('api_object.' + '.'.join(file_path_list))

        elif os.path.isdir(api):
            for api_file in os.listdir(api):
                os.path.join(api, api_file)
                self.travel_api_object(os.path.join(api, api_file), url, method)

    def generate_api_case(self, testcase_steps):
        """
        转换成api_object 模式的用例步骤
        :param testcase_steps:
        :return:
        """
        for step in testcase_steps:
            url = step['request']['url']
            method = step['request']['method']
            step.update(self.find_object_func(url, method))

    def generate_testcase(self, fmt_version: str = 'v1', testcase_path: str = 'testcase'):
        """
        将har文件转换成测试用例
        :param testcase_path: 用例存放地址 默认放在testcase目录 需要存在与TestBase统一目录
        :param fmt_version: 用例版本
        """
        # 1 先获取文输出文件名
        # 切割文件和扩展名
        har_file_dir = os.path.splitext(self.har_file)[0]

        logging.info('开始转换测试用例')
        case_name = ''
        if '/' in har_file_dir:
            case_name = har_file_dir.split('/')[-1]
        elif '\\' in har_file_dir:
            case_name = har_file_dir.split('\\')[-1]
        testcase_path = os.path.join(testcase_path, 'test_'+case_name + '.py')
        testcase_content = self._make_testcase(case_name, fmt_version)
        ad_utils.write(testcase_content, testcase_path)
        logging.info(f'完成{har_file_dir}的用例转换')


if __name__ == '__main__':
    pass
