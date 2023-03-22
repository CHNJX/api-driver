# -*- coding:utf-8 -*-
# @Time     :2023/2/1 3:22 下午
# @Author   :CHNJX
# @File     :swagger_generate.py
# @Desc     :将swagger转换成api-object
import os
import re
import sys
from os.path import dirname, exists, join

sys.path.append(dirname(sys.path[0]))

from api_driver.loader_swagger import load_swagger
from api_driver.tenplate import Template
from api_driver import ad_utils


class SwaggerGenerator:
    swagger_data = None

    def generate(self, swagger_doc, api_dir=None):
        """
        将swagger 装换成api-object
        :param swagger_doc: swagger文档
        :param api_dir:     api-object存放路径
        :return:
        """
        if not api_dir:
            api_dir = 'api_object'
        if '/' not in swagger_doc and '\\' not in swagger_doc:
            swagger_doc = 'swagger/' + swagger_doc
        self.swagger_data = load_swagger(swagger_doc)
        self._generate_template_path(self.swagger_data['paths'])
        tag_path_dict = self._generate_template_data(self.swagger_data)
        template = Template()
        for tag, paths in tag_path_dict.items():
            content = template.get_content('api.tpl', tag=tag, paths=paths)
            file_path = os.path.join(api_dir, tag.lower() + '.py')
            ad_utils.write(content, file_path)

    def _get_http_method(self, value: dict) -> str:
        """
        提取请求方式
        :param value: get:{} or post:{} or put:{} ...
        :return: request method: get/post/put/delete...
        """
        method_map = {
            'get': 'get',
            'post': 'post',
            'put': 'put',
            'delete': 'delete'
        }
        for method, attribute in method_map.items():
            if value.get(method):
                return attribute
        return ''

    def _transformation_parameters(self, parameters) -> list:
        """
        parameters dict => parameters list
        """
        return [param for param in parameters if
                param['name'] not in ('raw', 'root') and param['in'] == 'query']

    # 转换json参数
    def _transformation_data(self, parameters) -> list:
        """
        将json参数装换成json参数名称列表
        :return: [param1，param2...]
        """
        data_list = []
        for param in parameters:
            if param.get('schema'):
                if param['schema'].get('properties'):
                    data_list.extend(param['schema']['properties'].keys())
                elif param['schema'].get('$ref'):
                    data_ref: str = param['schema'].get('$ref')
                    data_link = data_ref.split('/')[-1]
                    data_list.extend(self.swagger_data['definitions'][data_link]['properties'].keys())

        return data_list

    def _transformation_file(self, parameters) -> list:
        """抽取文件类型参数"""
        files = []
        for param in parameters:
            if param['name'] == 'file':
                files.append(param['name'])
            elif param.get('schema'):
                if param['schema'].get('properties'):
                    if 'file' in param['schema']['properties'].keys():
                        files.append(param['name'])
        return files

    # 拼接参数列表
    def _transformation_params_list(self, params: dict, data_params: list, files: list) -> list:
        params_name_list: list = [param['name'] for param in params]
        params_name_list.extend(data_params)
        params_name_list.extend(files)
        return params_name_list

    def _transform_url(self, path, method):
        """对url进行转换 适应restful风格"""
        path_name_list: list[str] = path.split('/')
        pat = re.compile(r'[@_!#$%^&*()<>?/\|}{~:]')
        res = {}
        if 'id' in path_name_list[-1].lower() or pat.search(path_name_list[-1]):
            res['url_param'] = re.sub('[\W_]+', '', path_name_list[-1])
            if method == 'get':
                res['name'] = '_get'
            elif method == 'post':
                res['name'] = '_post'
            elif method == 'put':
                res['name'] = '_put'
            elif method == 'delete':
                res['name'] = '_delete'
            res['name'] = path_name_list[-2] + res['name']
            path_name_list.pop(-1)
            res['url'] = '/'.join(path_name_list)
        else:
            res['url_param'] = ''
            res['url'] = path
            res['name'] = path_name_list[-1].split('?')[0]
        return res

    def _generate_template_path(self, swagger_paths):
        """
        对path是进行解析
        :param swagger_paths: swagger_docs 解析的path字典
        :return:
        """
        for path, value in swagger_paths.items():
            method_attribute = self._get_http_method(value)
            value['method'] = method_attribute
            value['tag'] = value[method_attribute]['tags'][0]
            value['desc'] = value[method_attribute]['summary']
            value['content-type'] = value[method_attribute]['consumes'][0] if value[method_attribute].get(
                'consumes') else ''
            parameters = value[method_attribute]['parameters'] if value[method_attribute].get('parameters') else ''
            value['parameters'] = self._transformation_parameters(parameters)
            value['data'] = self._transformation_data(parameters)
            value['files'] = self._transformation_file(parameters)
            value['params_list'] = self._transformation_params_list(value['parameters'], value['data'], value['files'])
            value.update(self._transform_url(path, method_attribute))

    def _generate_template_data(self, swagger_data) -> dict:
        """将数据改造后存入字典"""
        tag_path_dict = {tag['name'].replace('/', '-', -1).capitalize():
                             {name: path for name, path in swagger_data['paths'].items()
                              if path['tag'].replace('/', '-', -1) == tag['name'].replace('/', '-', -1)}
                         for tag in swagger_data['tags']}

        return tag_path_dict
