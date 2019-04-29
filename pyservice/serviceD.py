import datetime
import requests

import tornado.web
import tornado.ioloop
from tornado.httpserver import HTTPServer

from py_zipkin.zipkin import zipkin_span, ZipkinAttrs


class ServiceDHandler(tornado.web.RequestHandler):

    async def get(self):

        headers = self.request.headers

        # parent span 的属性传入到当前 span
        zipkin_attrs = ZipkinAttrs(
            trace_id=headers['X-B3-TraceID'],
            span_id=headers['X-B3-SpanID'],
            parent_span_id=headers['X-B3-ParentSpanID'],
            flags=headers.get('X-B3-Flags', ''),
            is_sampled=headers['X-B3-Sampled']
        )

        with zipkin_span(
            service_name='py-service_D',
            span_name='py-span_D-index',
            zipkin_attrs=zipkin_attrs,
            transport_handler=handle_http_transport,
            port=9002,
            sample_rate=100
        ):
            self.write("--- Python Service_D %s --- " % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %p"))


def handle_http_transport(encoded_span):
    headers = {"Content-Type": "application/x-thrift"}
    body = encoded_span
    zipkin_url = "http://localhost:9411/api/v1/spans"

    requests.post(zipkin_url, data=body, headers=headers)


def init_service():
    app = tornado.web.Application([
        (r"/services/d", ServiceDHandler)
    ])

    server = HTTPServer(app)
    server.listen(9002)

    print("Py-service_D listening at port 9002\n")

    server.start(1)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    init_service()
