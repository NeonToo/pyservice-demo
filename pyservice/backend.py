import datetime
import requests

import tornado.web
import tornado.ioloop
from tornado.httpserver import HTTPServer
from tornado.httpclient import AsyncHTTPClient

from py_zipkin.zipkin import zipkin_span, create_http_headers_for_new_span


class BackendHandler(tornado.web.RequestHandler):
    async def get(self):
        with zipkin_span(
                service_name='py-backend',
                span_name='py-backend',
                transport_handler=handle_http_transport,
                port=9001,
                sample_rate=100
        ):
            self.write("From Python Backend Service %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %p"))


class CrossApiHandler(tornado.web.RequestHandler):
    async def get(self):
        with zipkin_span(
                service_name='py-backend',
                span_name='py-cross-api',
                transport_handler=handle_http_transport,
                port=9001,
                sample_rate=100
        ):
            # TODO create_http_headers_for_new_span() 对同一个服务内跨API的调用无效，会生成两个独立的span。直接本地调用方法？
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
                self.write("From Python Backend Cross API Service: %s" % response.body)


class CrossServiceHandler(tornado.web.RequestHandler):
    async def get(self):
        with zipkin_span(
                service_name='py-backend',
                span_name='py-cross-service',
                transport_handler=handle_http_transport,
                port=9001,
                sample_rate=100
        ):
            # 跨服务通知必须用 create_http_headers_for_new_span()
            headers = {}
            headers.update(create_http_headers_for_new_span())
            request = tornado.httpclient.HTTPRequest(
                url='http://localhost:9000/jv1',
                method='GET',
                headers=headers
            )

            try:
                response = await AsyncHTTPClient().fetch(request)
            except Exception as e:
                return "Error: %s" % e
            else:
                self.write("From Python Backend Cross API Service: %s" % response.body)


def handle_http_transport(encoded_span):
    headers = {"Content-Type": "application/x-thrift"}
    body=encoded_span
    zipkin_url="http://localhost:9411/api/v1/spans"

    requests.post(zipkin_url, data=body, headers=headers)


def init_backend():
    app = tornado.web.Application([
        (r"/py", BackendHandler),
        (r"/crs/api", CrossApiHandler),
        (r"/crs/service", CrossServiceHandler),
    ])
    server = HTTPServer(app)
    server.listen(9001)

    print("Py-backend listening at port 9001\n")

    server.start(1)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    init_backend()
