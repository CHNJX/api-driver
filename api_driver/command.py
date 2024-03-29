# -*- coding:utf-8 -*-
# @Time     :2023/2/7 12:38
# @Author   :CHNJX
# @File     :command.py
# @Desc     :命令工具
import os
import subprocess
import sys
from os.path import dirname, exists
import click as click

from api_driver.har_parser import HarParser

sys.path.append(dirname(sys.path[0]))

from api_driver.project_generator import ProjectGenerator
from api_driver.swagger_generate import SwaggerGenerator

group = click.Group()


@click.command('start_project')
@click.option('-n', '--project-name', required=True, help='project name')
def start_project(project_name):
    """
    创建项目
    :param project_name: 项目名称
    """
    ProjectGenerator().project_generate(project_name)


@click.command('swagger2api')
@click.option('-s', '--swagger-doc',
              required=True, help='Swagger doc file.')
@click.option('-d', '--api-dir',
              required=False, help='api save dir.')
def swagger2api(swagger_doc, api_dir):
    """
    swagger文档转换成api-object
    :param swagger_doc: swagger.json 文件
    :param api_dir:  api存放路径 非必填
    """
    SwaggerGenerator().generate(swagger_doc, api_dir)


@click.command('run')
@click.option('-c', '--testcase',
              required=True, help='testcase')
@click.option('-t', '--tag',
              required=False, help='testcase')
@click.option('-r', '--reset', help='auto clear report', required=False, default='false',
              type=click.Choice(['true', 'false']))
@click.option('-t', '--threads', help='run with multiple threads', required=False)
def run(testcase, tag, reset, threads):
    """
    运行用例并集成allure报告
    :param threads: 运行的线程数
    :param testcase: 用例路径
    :param tag: 用例标签
    :param reset: 是否重置allure报告
    """""
    command = f'pytest -v -s {testcase}'
    if reset == 'true':
        if 'win' in sys.platform:
            subprocess.call(f'rmdir /Q /S allure-results', shell=True)
        else:
            subprocess.call(f'rmdir -rf allure-results', shell=True)
    if threads:
        command += f' -n {threads}'
    if tag:
        command += f' -m {tag}'

    subprocess.call(command + ' --alluredir=./allure-results', shell=True)


@click.command('har2case')
@click.option('-h', '--har',
              required=True, help='har file path')
@click.option('-a', '--api',
              required=False, help='api object dir', default=None)
@click.option('-t', '--testcase', help='testcase dir', required=False, default='testcase')
@click.option('-e', '--exclude', help='exclude url', required=False, default='')
def har2case(har, api, testcase, exclude):
    """
    将har转换成用例
    :param har: har文件路径
    :param api: har对应api-object文件
    :param testcase:  用例路径
    :param exclude:  过来的url
    :return:
    """
    hp = HarParser(har_file_path=har, api_object=api, exclude_url=exclude)
    hp.generate_testcase(testcase_path=testcase)


@click.command('capture2testcase')
@click.option('-n', '--name', help="testcase name", required=True)
@click.option('-fh', '--host', help="filter host", required=True)
@click.option('-fp', '--path', help="filter path", required=False, default='')
@click.option('-l', '--port', help="listening port", required=False, default='8888')
@click.option('-h', '--har',
              required=False, help='har file path')
@click.option('-a', '--api',
              required=False, help='api object dir', default='')
@click.option('-t', '--testcase', help='testcase dir', required=False, default='testcase')
@click.option('-e', '--exclude', help='exclude url', required=False, default='')
def capture2testcase(name, host, path, port, har, api, testcase, exclude):
    """
    抓取网络数据包并生成测试用例
    :param name: 测试用例名称
    :param host: 抓取的域名
    :param path: 抓取的路径
    :param port: 监听的端口
    :param har: 对应har文件名称
    :param api: 对应api-object路径
    :param testcase: 测试用例存放路径
    :param exclude: 剔除的url
    :return:
    """
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'capture2testcase.py'))
    # 构建 mitmproxy 命令
    mitmproxy_command = [
        "mitmproxy", "-s", script_path,
        "--set", f'name={name}',
        "--set", f'host={host}',
        "--set", f'path={path}',
        "--set", f'har={har}',
        "--set", f'api={api}',
        "--set", f'testcase_path={testcase}',
        "--set", f'exclude={exclude}',
        "-p", port
    ]
    try:
        # 启动 mitmproxy 命令
        subprocess.run(mitmproxy_command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        # 处理命令执行失败的情况
        click.echo(f"命令执行失败，返回代码 {e.returncode}")
    except Exception as ex:
        # 处理其他异常
        click.echo(f"发生异常：{str(ex)}")


group.add_command(start_project)
group.add_command(swagger2api)
group.add_command(run)
group.add_command(har2case)
group.add_command(capture2testcase)


def cmd():
    group.main()


if __name__ == '__main__':
    har2case()
