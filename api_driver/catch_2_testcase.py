import json
import os
from datetime import datetime

from mitmproxy import ctx

from api_driver.command import har2case
from api_driver.har_parser import HarParser


class ExportFilter:
    def __init__(self):
        """
        :param host: 域名
        :param path: 路径
        """
        self.entries = []
        self.exclude_url = ['js', 'png', 'gif', 'jpg', 'css', 'jpeg', 'ico']

    def load(self, loader):
        loader.add_option(
            name="host",
            typespec=str,
            default='',
            help="Add a host as a url filter condition",
        )
        loader.add_option(
            name="path",
            typespec=str,
            default='',
            help="Add a path as a url filter condition",
        )
        loader.add_option(
            name="name",
            typespec=str,
            default='',
            help="Testcase name",
        )
        loader.add_option(
            name="testcase_path",
            typespec=str,
            default='',
            help="Storage path of testcase",
        )
        loader.add_option(
            name="exclude",
            typespec=str,
            default='',
            help="Path to be eliminated",
        )
        loader.add_option(
            name="api",
            typespec=str,
            default='',
            help="The path of the api-object",
        )

    def response(self, flow):
        request_data = flow.request
        response_data = flow.response

        # 在这里使用传递的筛选关键词进行匹配
        host = ctx.options.host if ctx.options.host else ''
        path = ctx.options.path.split(',') if ctx.options.path else []

        if host not in request_data.pretty_url or (path and not any(p in request_data.pretty_url for p in path)):
            return

        if any(e in request_data.pretty_url for e in self.exclude_url):
            return

        started_datetime = datetime.fromtimestamp(request_data.timestamp_start)
        started_datetime_str = started_datetime.isoformat()

        entry = {
            "startedDateTime": started_datetime_str,
            "request": {
                "method": request_data.method,
                "url": request_data.url,
                "httpVersion": "HTTP/1.1",
                "cookies": [],
                "headers": [
                    {"name": h[0], "value": h[1]} for h in request_data.headers.items()
                ],
                "queryString": [],
                "postData": {},
                "headersSize": -1,
                "bodySize": len(request_data.content)
            },
            "response": {
                "status": response_data.status_code,
                "statusText": response_data.reason,
                "httpVersion": "HTTP/1.1",
                "cookies": [],
                "headers": [
                    {"name": h[0], "value": h[1]} for h in response_data.headers.items()
                ],
                "content": {
                    "size": len(response_data.content),
                    "mimeType": response_data.headers.get("Content-Type", ""),
                    "text": response_data.text  # 存储响应文本数据
                },
                "redirectURL": "",
                "headersSize": -1,
                "bodySize": len(response_data.content)
            },
            "cache": {},
            "timings": {},
            "serverIPAddress": "",
            "connection": "",
            "comment": ""
        }
        self.entries.append(entry)

    def done(self):
        har_data = {
            "log": {
                "version": "1.2",
                "creator": {
                    "name": "mitmproxy",
                    "version": "1.0"
                },
                "entries": self.entries
            }
        }
        testcase_name = ctx.options.name
        try:
            with open(f'har/{testcase_name}.har', 'w') as har_file:
                har_file.write(json.dumps(har_data, indent=2))
                har_file.flush()  # 确保数据被写入磁盘
        except Exception as e:
            # 写入失败，处理错误
            print(f"写入 HAR 文件时发生错误：{str(e)}")
            # 这里可以添加处理错误的逻辑
        else:
            # 写入成功，可以继续执行后续的代码
            # 调用 shell生成测试用例 命令
            testcase_path = ctx.options.testcase_path if ctx.options.testcase_path else 'testcase'
            api = ctx.options.api if ctx.options.api else ''
            exclude = ctx.options.exclude if ctx.options.exclude else ''
            har_file_path = os.path.join(os.getcwd(), f'har/{testcase_name}.har')
            har2case(['-h', har_file_path, '-t', testcase_path, '-a', api, '-e', exclude])
            # 这里可以添加后续代码逻辑


addons = [ExportFilter()]
