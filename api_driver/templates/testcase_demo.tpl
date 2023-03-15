from testcase.test_base import TestBase
from api_object.api_demo import ApiDemo


class TestcaseDemo(TestBase):
    api_demo = ApiDemo()

    def test_demo(self):
        resp = self.api_demo.postman_echo('bar1', 'bar2')
        assert resp['status_code'] == 200
        assert resp['args']['foo1'] == 'bar1'
        assert resp['args']['foo2'] == 'bar2'
