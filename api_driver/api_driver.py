# -*- coding:utf-8 -*-
# @Time     :2023/7/10 15:04
# @Author   :CHNJX
# @File     :api_driver.py
# @Desc     :
import subprocess
import time
from datetime import datetime

import pytest
from jinja2 import Environment, FileSystemLoader

from api_driver.template import Template


class TestResultPlugin:
    def __init__(self):
        self.results = {}
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.skip_count = 0
        self.error_count = 0

    def pytest_collection_modifyitems(self, config, items):
        # 统计被跳过的测试用例数量
        for item in items:
            if item.get_closest_marker("skip"):
                self.skip_count += 1

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            self.test_count += 1

            # 统计测试结果数量
            if report.outcome == "passed":
                self.pass_count += 1
            elif report.outcome == "failed":
                self.fail_count += 1
            elif report.outcome == "error":
                self.error_count += 1

            testcase_info = report.nodeid.split('::')
            test_suite = testcase_info[0].split('/')[-1]
            test_class = testcase_info[1] if len(testcase_info) == 3 else None
            test_name = testcase_info[-1]
            result = {
                'test_model': test_suite,
                'test_class': test_class,
                'test_name': test_name,
                'result': report.outcome,
                'details': str(report.longrepr),
            }

            if test_suite not in self.results:
                self.results[test_suite] = {}
            if test_class not in self.results[test_suite]:
                self.results[test_suite][test_class] = []
            self.results[test_suite][test_class].append(result)

    def get_results(self) -> dict:
        return {
            'test_count': self.test_count,
            'pass_count': self.pass_count,
            'fail_count': self.fail_count,
            'skip_count': self.skip_count,
            'error_count': self.error_count,
            'results': self.results
        }


class ApiDriver:

    def run_tests(self, testcases: str, report_file: str = None):
        plugin = TestResultPlugin()
        start_time = time.time()
        pytest.main([testcases, '-v', '-s'], plugins=[plugin])
        end_time = time.time()
        execution_time = "{:.2f}s".format(end_time - start_time)
        res = plugin.get_results()
        res['execution_time'] = execution_time

        # 生成HTML报告
        if report_file:
            self.generate_html_report(res, report_file)

        return res

    def generate_html_report(self, results, report_file):
        report_content = self.get_html_content(results)
        with open(report_file, 'w', encoding='utf-8') as report_file:
            report_file.write(report_content)

    def get_html_content(self, results) -> str:
        # 获取当前日期和时间
        current_datetime = datetime.now()
        # 格式化输出当前日期和时间
        formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
        template = Template()
        return template.get_content('report_template.html',
                                    current=formatted_datetime,
                                    execution_time=results['execution_time'],
                                    results=results)
