import datetime
import requests

import tornado.web
import tornado.ioloop
from tornado.httpserver import HTTPServer
from tornado.httpclient import AsyncHTTPClient

from py_zipkin.zipkin import zipkin_span


class FrontendHandler(tornado.web.RequestHandler):
    # def get(self):
    #     self.write('Py-service OK')
    async def get(self):
        with zipkin_span(
                service_name='py-frontend',
                span_name='py-index',
                transport_handler=handle_http_transport,
                port=8082,
                sample_rate=100
        ):
            with zipkin_span(service_name='py-frontend', span_name='py-frontend'):
                http_client = AsyncHTTPClient()

                try:
                    response = await http_client.fetch("http://localhost:9000/api")
                except Exception as e:
                    print('Error: %s' % e)
                else:
                    self.write(response.body)
    # def handle_request(self, response):
    #     if response.error:
    #         print("Error: " + response.error)
    #     else:
    #         print(response.body)
    # def get(self):
    #     with zipkin_span(
    #             service_name='py-frontend',
    #             span_name='py-index',
    #             transport_handler=handle_http_transport,
    #             port=8082,
    #             sample_rate=100
    #     ):
    #         with zipkin_span(service_name='py-frontend', span_name='py-frontend'):
    #             self.write(do_stuff())


# class ServiceHandler(tornado.web.RequestHandler):
#     def get(self):
#         with zipkin_span(service_name='py-frontend', span_name='py-callback'):
#


def handle_http_transport(encoded_span):
    headers = {"Content-Type": "application/x-thrift"}
    body=encoded_span
    zipkin_url="http://localhost:9411/api/v1/spans"

    requests.post(zipkin_url, data=body, headers=headers)


def init_frontend():
    app = tornado.web.Application([
        (r"/", FrontendHandler),
        # (r"/api", ServiceHandler)
    ])
    server = HTTPServer(app)
    server.listen(8081)

    print("Py-frontend listening at port 8081\n")

    server.start(1)
    tornado.ioloop.IOLoop.current(instance=True).start()


if __name__ == "__main__":
    init_frontend()