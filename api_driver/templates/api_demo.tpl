from api_object.http import Http


class ApiDemo(Http):
    def postman_echo(self, foo1, foo2):
        """
        示例接口
        :param foo1: 参数1
        :param foo2: 参数2
        """
        request_params = {
            'foo1': foo1,
            'foo2': foo2
        }
        return self.get_req(url='https://postman-echo.com/get', params=request_params)
