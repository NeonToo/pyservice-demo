import requests

import tornado.web
import tornado.ioloop
from tornado.httpserver import HTTPServer
from tornado.httpclient import AsyncHTTPClient

from py_zipkin import Encoding, Kind
from py_zipkin.zipkin import zipkin_span, create_http_headers_for_new_span, ZipkinAttrs, get_default_tracer

from pyservice.util import get_local_host_ip
from pyservice.transport import HttpTransport

LOCAL_HOST = get_local_host_ip()
LOCAL_PORT = 8081
SERVICE_NAME = 'py_service_c'
USE_128_TRACE_ID = True

class ServiceHandler(tornado.web.RequestHandler):

    async def get(self):

        tracer = get_default_tracer()

        transport_handler = HttpTransport()
        span_name = self.request.path

        # generate SERVER span
        with zipkin_span(
            use_128bit_trace_id=USE_128_TRACE_ID,
            service_name=SERVICE_NAME,
            span_name=span_name,
            transport_handler=transport_handler,
            host=LOCAL_HOST,
            port=LOCAL_PORT,
            sample_rate=100,
            encoding=Encoding.V2_JSON,
        ) as span:
            response_d = await call_service_d(tracer, span)
            self.write("*** Python Service_C *** calls: %s \n" % response_d.decode().strip())

            response_e = await call_service_b(tracer, span)
            self.write("\n *** Python Service_C *** calls: %s " % response_e.decode().strip())


# @zipkin_span(service_name='py-service_C', span_name='py-service_C->D')
async def call_service_d(tracer, span):

    # to call next service, generate a span context using create_http_headers_for_new_span()
    span_headers = create_http_headers_for_new_span(tracer=tracer)

    # trace_id, span_id, parent_id et.al all the same
    zipkin_attrs = ZipkinAttrs(
        trace_id=span_headers.get('X-B3-TraceId'),
        span_id=span_headers.get('X-B3-SpanId'),
        parent_span_id=span_headers.get('X-B3-ParentSpanId'),
        flags=span_headers.get('X-B3-Flags'),
        is_sampled=span_headers.get('X-B3-Sampled')
    )

    # generate CLIENT span
    with tracer.zipkin_span(
        service_name=SERVICE_NAME,
        span_name='/services/d',
        kind=Kind.CLIENT,
        transport_handler=HttpTransport(),
        zipkin_attrs=zipkin_attrs,
    ) as client_span_d:

        res_body = None
        res_code = '500'

        req = tornado.httpclient.HTTPRequest(
            url='http://localhost:9001/services/d',
            method='GET',
            headers=span_headers
        )

        try:
            res = await AsyncHTTPClient().fetch(req)
            res_code = res.code
            res_body = res.body.decode().strip()
        except Exception as e:
            return "Error: %s" % e
        else:
            pass
        finally:
            client_span_d.update_binary_annotations({
                "result": str(res_code)
            })
            span.update_binary_annotations({
                "result": str(res_code)
            })
            return res_body


# @zipkin_span(service_name='py-service_C', span_name='py-service_C->B')
async def call_service_b(tracer, span):
    # to call next service, generate a span context using create_http_headers_for_new_span()
    span_headers = create_http_headers_for_new_span(tracer=tracer)

    # trace_id, span_id, parent_id et.al all the same
    zipkin_attrs = ZipkinAttrs(
        trace_id=span_headers.get('X-B3-TraceId'),
        span_id=span_headers.get('X-B3-SpanId'),
        parent_span_id=span_headers.get('X-B3-ParentSpanId'),
        flags=span_headers.get('X-B3-Flags'),
        is_sampled=span_headers.get('X-B3-Sampled')
    )

    # generate CLIENT span
    with tracer.zipkin_span(
            service_name=SERVICE_NAME,
            span_name='/services/b',
            kind=Kind.CLIENT,
            transport_handler=HttpTransport(),
            zipkin_attrs=zipkin_attrs,
    ) as client_span_d:

        res_body = None
        res_code = '500'

        req = tornado.httpclient.HTTPRequest(
            url='http://localhost:9001/services/d',
            method='GET',
            headers=span_headers
        )

        try:
            res = await AsyncHTTPClient().fetch(req)
            res_code = res.code
            res_body = res.body.decode().strip()
        except Exception as e:
            return "Error: %s" % e
        else:
            pass
        finally:
            client_span_d.update_binary_annotations({
                "result": str(res_code)
            })
            span.update_binary_annotations({
                "result": str(res_code)
            })
            return res_body


def init_service():
    app = tornado.web.Application([
        (r"/", ServiceHandler)
    ])

    server = HTTPServer(app)
    server.listen(LOCAL_PORT)

    print("Py-service_C listening at port {}\n".format(LOCAL_PORT))

    server.start(1)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    init_service()
