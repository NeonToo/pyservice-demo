import datetime
import requests

import tornado.web
import tornado.ioloop
from tornado.httpserver import HTTPServer

from transport import http_transport

from py_zipkin import Encoding
from py_zipkin.zipkin import zipkin_span, ZipkinAttrs


class ServiceDHandler(tornado.web.RequestHandler):

    async def get(self):

        headers = self.request.headers

        # 属性传入到当前 span，已经是为当前 span 生成的了
        zipkin_attrs = ZipkinAttrs(
            trace_id=headers['X-B3-TraceID'],
            span_id=headers['X-B3-SpanID'],
            parent_span_id=headers['X-B3-ParentSpanID'],
            flags=headers.get('X-B3-Flags', ''),
            is_sampled=headers['X-B3-Sampled']
        )

        # self.write('Into Py-Service_D the header attributes: \n')
        # self.write('X-B3-SpanID: %s' % headers['X-B3-SpanID'])
        # self.write('X-B3-ParentSpanID: %s' % headers['X-B3-ParentSpanID'])

        with zipkin_span(
            service_name='py-service_D',
            span_name='py-span_D-index',
            zipkin_attrs=zipkin_attrs,
            transport_handler=handle_http_transport,
            port=9002,
            sample_rate=100,
            encoding=Encoding.V2_JSON
        ):
            self.write(handle_service())


# @zipkin_span(service_name='py-service_D', span_name='py-service_D')
def handle_service():
    return "--- Python Service_D %s --- " % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %p")


def handle_http_transport(encoded_span):
    headers = {"Content-Type": "application/json"}
    body = encoded_span
    zipkin_url = "http://localhost:9411/api/v2/spans"

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
