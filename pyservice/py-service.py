import requests

import tornado.web
import tornado.ioloop
from tornado.httpserver import HTTPServer
from tornado.httpclient import AsyncHTTPClient

from py_zipkin import Encoding
from py_zipkin.zipkin import zipkin_span, create_http_headers_for_new_span, ZipkinAttrs


class ServiceHandler(tornado.web.RequestHandler):

    async def get(self):

        with zipkin_span(
                service_name='py-service',
                span_name='py-span-index',
                transport_handler=handle_http_transport,
                port=9001,
                sample_rate=100,
                encoding=Encoding.V2_JSON
        ):
            response_d = await call_service_d()
            self.write("Python Service_C calls: %s" % response_d)

            response_e = await call_service_b()
            self.write("Python Service_C calls: %s" % response_e)


@zipkin_span(service_name='py-service', span_name='py-service->D')
async def call_service_d():
    # 跨服务通知 Python Service_D, 必须用 create_http_headers_for_new_span() 为当前调用生成 span header 传给下一个服务
    headers = create_http_headers_for_new_span()
    request = tornado.httpclient.HTTPRequest(
        url='http://localhost:9002/services/d',
        method='GET',
        headers=headers
    )

    try:
        response = await AsyncHTTPClient().fetch(request)
    except Exception as e:
        return "Error: %s" % e
    else:
        return response.body


@zipkin_span(service_name='py-service', span_name='py-service->B')
async def call_service_b():
    # 跨服务通知 Java Service_B, 必须用 create_http_headers_for_new_span()
    headers = create_http_headers_for_new_span()
    request = tornado.httpclient.HTTPRequest(
        url='http://localhost:9000/services/b',
        method='GET',
        headers=headers
    )

    try:
        response = await AsyncHTTPClient().fetch(request)
    except Exception as e:
        return "Error: %s" % e
    else:
        return response.body


def handle_http_transport(encoded_span):
    zipkin_url = "http://localhost:9411/api/v2/spans"

    requests.post(
        zipkin_url,
        data=encoded_span,
        headers={"Content-Type": "application/json"}
    )


def init_service():
    app = tornado.web.Application([
        (r"/services/py", ServiceHandler)
    ])

    server = HTTPServer(app)
    server.listen(9001)

    print("Py-service_C listening at port 9001\n")

    server.start(1)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    init_service()
