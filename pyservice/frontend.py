import requests

import tornado.web
import tornado.ioloop
from tornado.httpserver import HTTPServer
from tornado.httpclient import AsyncHTTPClient

from py_zipkin.zipkin import zipkin_span, create_http_headers_for_new_span


class FrontendHandler(tornado.web.RequestHandler):
    async def get(self):
        with zipkin_span(
                service_name='py-frontend',
                span_name='py-frontend-index',
                transport_handler=handle_http_transport,
                port=8081,
                sample_rate=100
        ):
            # TODO ??? create_http_headers_for_new_span() 通知后端服务，但无效，仍然是两个独立的span
            headers = {}
            headers.update(create_http_headers_for_new_span())
            request = tornado.httpclient.HTTPRequest(
                url='http://localhost:9001/py',
                method='GET',
                headers=headers
            )

            try:
                response = await AsyncHTTPClient().fetch(request)
            except Exception as e:
                return "Error: %s" % e
            else:
                res = response
                self.write("From Python Backend Cross API Service: %s" % response.body)


def handle_http_transport(encoded_span):
    headers = {"Content-Type": "application/x-thrift"}
    body=encoded_span
    zipkin_url="http://localhost:9411/api/v1/spans"

    requests.post(zipkin_url, data=body, headers=headers)


def init_frontend():
    app = tornado.web.Application([
        (r"/", FrontendHandler)
    ])
    server = HTTPServer(app)
    server.listen(8081)

    print("Py-frontend listening at port 8081\n")

    server.start(1)
    tornado.ioloop.IOLoop.current(instance=True).start()


if __name__ == "__main__":
    init_frontend()
