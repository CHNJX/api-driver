from api_object.http import Http


class Users(Http):
    base_url = "https://www.baodu.com"
    def users(self):
        """
        Get a list of users"""

        req_data = {
            "url": f"/users",
            "params": {},
            "json": {},
            "files": {}
        }
        return self.req(method="get", **req_data)

    def detail(self, userId):
        """
        Get a user by ID
        :param userId: The ID of the user to retrieve *
        """

        req_data = {
            "url": f"/users/{ userId }",
            "params": {
                "userId": userId
                },
            "json": {},
            "files": {}
        }
        return self.req(method="get", **req_data)