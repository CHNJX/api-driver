import os
from os.path import join, dirname

from api_driver.har_parser import HarParser
from api_driver.project_generator import ProjectGenerator
from api_driver.swagger_generate import SwaggerGenerator


class TestCommand:
    def test_start_project(self):
        ProjectGenerator().project_generate('new_project')
        assert os.path.isdir(os.path.join('new_project', "api_object"))
        assert os.path.isdir(os.path.join('new_project', "testcase"))

    def test_swagger_generate(self):
        SwaggerGenerator().generate(join(dirname(__file__), 'swagger/swagger.json'),
                                    join(dirname(__file__), 'api_object'))
        assert os.path.exists(os.path.join(dirname(__file__) + "/api_object", "users.py"))

    def test_har2case_generate(self):
        har_file = join(dirname(__file__), 'data/demo.har')
        testcase_dir = join(dirname(__file__), 'testcase')
        har = HarParser(har_file_path=har_file)
        har.generate_testcase(testcase_path=testcase_dir)
        assert os.path.exists(os.path.join(dirname(__file__) + "/testcase", "test_demo.py"))