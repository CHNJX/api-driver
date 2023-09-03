# -*- coding:utf-8 -*-
# @Time     :2023/7/23 21:59
# @Author   :CHNJX
# @File     :run_case.py
# @Desc     :

from api_driver.api_driver import ApiDriver

apd = ApiDriver()
res = apd.run_tests('/Users/chnjx/PycharmProjects/api-driver/test/testcase/test_demo.py')
report = apd.get_html_content(res)
apd.generate_html_report(res, 'report.html')
