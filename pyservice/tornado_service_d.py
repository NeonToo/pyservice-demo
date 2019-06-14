import datetime
import time

import tornado.web
import tornado.ioloop
from tornado.httpserver import HTTPServer

from py_zipkin import Encoding
from py_zipkin.zipkin import zipkin_span, ZipkinAttrs, get_default_tracer

from pyservice.transport import HttpTransport
from pyservice.util import get_local_host_ip
from pyservice.request_helper import create_zipkin_attr

LOCAL_HOST = get_local_host_ip()
LOCAL_PORT = 9001
SERVICE_NAME = 'py_service_d'
USE_128_TRACE_ID = True


class ServiceDHandler(tornado.web.RequestHandler):

    async def get(self):

        tracer = get_default_tracer()

        transport_handler = HttpTransport()
        span_name = self.request.path

        # get span context from request headers
        zipkin_attrs = create_zipkin_attr(self.request)

        with zipkin_span(
            use_128bit_trace_id=USE_128_TRACE_ID,
            service_name=SERVICE_NAME,
            span_name=span_name,
            zipkin_attrs=zipkin_attrs,
            transport_handler=transport_handler,
            host=LOCAL_HOST,
            port=LOCAL_PORT,
            encoding=Encoding.V2_JSON,
        ) as span:
            span.update_binary_annotations({
                'result': str(200)
            })

            # 模拟处理时间
            time.sleep(0.2)
            self.write(" *** Python Service_D %s *** " % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %p"))


def init_service():
    app = tornado.web.Application([
        (r"/services/d", ServiceDHandler)
    ])

    server = HTTPServer(app)
    server.listen(LOCAL_PORT)

    print("Py-service_D listening at port {}\n".format(LOCAL_PORT))

    server.start(1)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    init_service()
