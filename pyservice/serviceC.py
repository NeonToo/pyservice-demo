import requests

import tornado.web
import tornado.ioloop
from tornado.httpserver import HTTPServer
from tornado.httpclient import AsyncHTTPClient

from py_zipkin.zipkin import zipkin_span, create_http_headers_for_new_span, ZipkinAttrs


class ServiceHandler(tornado.web.RequestHandler):
    async def get(self):

        root_headers = self.request.headers

        zipkin_attrs = ZipkinAttrs(
            trace_id=root_headers['X-B3-TraceID'],
            span_id=root_headers['X-B3-SpanID'],
            parent_span_id=root_headers['X-B3-ParentSpanID'],
            flags=root_headers.get('X-B3-Flags', '0'),
            is_sampled=root_headers['X-B3-Sampled']
        )

        with zipkin_span(
                service_name='py-service_C',
                span_name='py-span_C',
                zipkin_attrs=zipkin_attrs,
                transport_handler=handle_http_transport,
                port=9001,
                sample_rate=100
        ) as zipkin_context:
            # TODO D/E 的调用在一个trace中且 ParentSpanID 为 C 的 SpanID，但与 C 没有形成层次结构
            # with zipkin_span(service_name='py-service_D', span_name='py-service_D'):
            # 跨服务通知 Python Service_D, 必须用 create_http_headers_for_new_span()
            headers = {}
            headers.update(create_http_headers_for_new_span())
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
                self.write("Python Service_C calls: %s" % response.body)

            # with zipkin_span(service_name='py-service_E', span_name='py-service_E'):
            # 跨服务通知 Java Service_E, 必须用 create_http_headers_for_new_span()
            headers = create_http_headers_for_new_span()
            request = tornado.httpclient.HTTPRequest(
                url='http://localhost:9000/services/e',
                method='GET',
                headers=headers
            )

            try:
                response = await AsyncHTTPClient().fetch(request)
            except Exception as e:
                return "Error: %s" % e
            else:
                self.write("Python Service_C calls: %s" % response.body)


def handle_http_transport(encoded_span):
    zipkin_url = "http://localhost:9411/api/v1/spans"

    requests.post(
        zipkin_url,
        data=encoded_span,
        headers={"Content-Type": "application/x-thrift"}
    )


def init_service():
    app = tornado.web.Application([
        (r"/services/c", ServiceHandler)
    ])

    server = HTTPServer(app)
    server.listen(9001)

    print("Py-service_C listening at port 9001\n")

    server.start(1)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    init_service()
