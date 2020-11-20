from __future__ import print_function

import unittest

import time
import mockserver
from mockserver.rest import ApiException
from pprint import pprint

# from mockserver_friendly import MockServerFriendlyClient, request, response




class MyTestCase(unittest.TestCase):
    def test_something(self):

        # client = MockServerFriendlyClient("http://localhost:1080")
        #
        # client.stub(
        #     request(method="GET", path="/item/public_token/exchange", querystring={"is": "good"}, headers={"so": "good"}),
        #     response(code=418, body="i'm a teapot", headers={"hi": "haa"})
        # )
        configuration = mockserver.Configuration()
        api_instance = mockserver.ControlApi(mockserver.ApiClient(configuration))
        expectations_api_instance = mockserver.ExpectationApi()
        expectations = []
        ports = mockserver.Ports()  # Ports | list of ports to bind to, where 0 indicates dynamically bind to any available port
        pprint(ports)

        try:
            # bind additional listening ports
            api_response = api_instance.bind_put(ports)
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling ControlApi->bind_put: %s\n" % e)


if __name__ == '__main__':
    unittest.main()
