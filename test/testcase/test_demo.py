from test.testcase.http import Http
from test.testcase.test_base import TestBase
from hamcrest import *


class TestDemo(TestBase):

    def setup_class(self):
        self.http = Http()

    def test_demo(self):
        self.logger.info('用例名称：demo')
        self.logger.info('测试步骤：/api/v1/cleaning/pointTypes')
        req_data = {
            "url": "https://plan-test.ienjoys.com/api/v1/cleaning/pointTypes",
            "method": "GET",
            'params': {'name': '3', 'status': '1', 'businessType': '1', 'page': '1', 'pageSize': '10'},
            'headers': {
                'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJUb2tlbiI6IlpRaWtsaGR0aGFrbTZmeUo4MFN0NWJIMGExV3luRHdTSU1iNFhaTFI5SmVVU1FDSkRlVW5aeHlwUWNMK3owVlJ5bHA4Z1loMnIzV0pxL0xLaTE3ZnNWM3FTV05zVjlDUjFHcjlPSkwxNFZYVkVTWWNHRUtTTldZVFg3T2o3NGxHVnZBcTJQRkJlTDRibGFxSDEzKzRVNGorVXN1c1dEQkFkQmt2amNzOWhSRHhuajZnNGphU3MxY3RzdWtmdnU2TmFWT2FWL2tsQ2RQSnhkQ0l1Nms5M0JVbWk1djA3Zy9MbFdNTy9YNDJaQVN5MW1WenExM1p5b1RpWHZOOTQ4UTVQaDUzRzdqaXl1Qm1XQ0xhOERnREJLUFRDYURpRlcyeklVQkdWWDdiNjRuM3NVZHp3bjZpYTVad0dGRGtPL09rRFoxVTdLWmJ4UG9XVXlZcWNtMTJ5dz09IiwiZXhwIjoxNjc3ODI2OTgyfQ.aAR8_Dpw0zeja19rsfGLazJUwxBeRmlmitk16NKPK2k',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'},
        }

        resp = self.http.req(**req_data)
        # 断言
        try:
            self.logger.info("进行断言：查看请求是否是否正确")
            self.logger.info("resp['status_code'] == 100")
            assert resp['status_code'] == 100
        except Exception as e:
            self.logger.error(f"断言失败：{e.__str__()}")
            raise e
