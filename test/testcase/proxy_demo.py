# -*- coding:utf-8 -*-
# @Time     :2023/8/20 12:03
# @Author   :CHNJX
# @File     :proxy_demo.py
# @Desc     :
import asyncio
import json
from jsonpath import jsonpath

from mitmproxy import http
from mitmproxy import options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy.http import HTTPFlow
import yaml
import jsonpath


class CustomAddon:
    def __init__(self, mock_file):
        self.mock_file = mock_file
        mock_data = self.load_config()
        self.host = mock_data['base_config']['base_host']
        self.mock_dict = mock_data['mock']

    def load_config(self):
        with open(self.mock_file, 'r') as file:
            return yaml.safe_load(file)

    def request(self, flow: HTTPFlow) -> None:
        for mock in self.mock_dict:
            request = mock.get('request')
            if not request:
                continue
            url = request.get('url', self.host)
            if url not in flow.request.pretty_url:
                continue
            filters = request.get('filters', [])

            if not filters or any(f in flow.request.pretty_url for f in filters):
                # 判断请求头
                if request['request_headers']:
                    for key, value in request['request_headers'].items():
                        flow.request.headers[key] = value
                if request['response_mock']:
                    self.rewrite_response(flow, request['response_mock'], 'request')
                if request['rewrite']:
                    rewrite_data = request['rewrite']
                    new_body = rewrite_data['body']
                    flow.request.text = json.dumps(new_body)
                if request['replace']:
                    replace_data = request['replace']
                    data = json.loads(flow.request.text)
                    self.replace_data(data, replace_data)
                    flow.request.text = json.dumps(data, ensure_ascii=False)
                break

    def response(self, flow: HTTPFlow):
        for mock in self.mock_dict:
            response: dict = mock.get('response')
            if not response:
                return
            url = response.get('url', self.host)
            if url not in flow.request.pretty_url:
                return

            filters = response.get('filter', [])
            if not filters or any(f in flow.request.pretty_url for f in filters):
                data = json.loads(flow.response.text)
                if 'rewrite' in response:
                    self.rewrite_response(flow, response['rewrite'], 'response')
                elif 'replace' in response:
                    self.replace_data(data, response['replace'])
                    flow.response.text = json.dumps(data, ensure_ascii=False)

                flow.response.text = json.dumps(data, ensure_ascii=False)

    def rewrite_response(self, flow, rewrite: dict, method: str):
        """
        重写response
        :param flow: http请求
        :param rewrite: 重写的数据
        :param method: 需要重写的方法 request or response
        :return:
        """
        if method not in ('request', 'response'):
            return

        status_code = rewrite.get('status_code', flow.response.status_code if method == 'response' else 200)
        body = rewrite.get('body', flow.response.text if method == 'response' else '')
        headers = rewrite.get('headers', flow.response.headers if method == 'response' else {})

        flow.response = http.Response.make(
            status_code,
            body,
            headers
        )

    def replace_data(self, data, replace_list):
        for r in replace_list:
            # 使用JSONPath表达式选择需要替换的元素
            key = list(r.keys())[0]
            matches = jsonpath.jsonpath(data, key)
            if matches:
                # 获取选中的元素值
                selected_value = matches[0]
                # 将该值替换为您希望的新值
                new_value = list(r.values())[0]
                # 将替换后的值重新设置回原始位置
                data = json.loads(json.dumps(data, ensure_ascii=False).replace(
                    selected_value, new_value))


async def main():
    config_path = "/Users/chnjx/PycharmProjects/api-driver/test/testcase/proxy.yml"  # 替换为你的 YAML 配置文件路径
    addon = CustomAddon(config_path)

    opts = options.Options(listen_host="0.0.0.0", listen_port=8889)
    master = DumpMaster(opts)
    master.addons.add(addon)

    try:
        print("Starting mitmproxy")
        await master.run()
    except KeyboardInterrupt:
        await master.shutdown()
        print("Mitmproxy has been shut down")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
