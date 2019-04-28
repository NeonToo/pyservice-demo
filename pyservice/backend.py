import datetime
import requests

import tornado.web
import tornado.ioloop
from tornado.httpserver import HTTPServer

from py_zipkin.zipkin import zipkin_span


class BackendHandler(tornado.web.RequestHandler):
    async def get(self):
        with zipkin_span(
                service_name='py-backend',
                span_name='py-backend-index',
                transport_handler=handle_http_transport,
                port=9001,
                sample_rate=100
        ):
            with zipkin_span(service_name='py-backend', span_name='py-backend'):
                self.write("From Python Backend %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %p"))

def handle_http_transport(encoded_span):
    headers = {"Content-Type": "application/x-thrift"}
    body=encoded_span
    zipkin_url="http://localhost:9411/api/v1/spans"

    requests.post(zipkin_url, data=body, headers=headers)


def init_backend():
    app = tornado.web.Application([
        (r"/api", BackendHandler)
    ])
    server = HTTPServer(app)
    server.listen(9001)

    print("Py-backend listening at port 9001\n")

    server.start(1)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    init_backend()
