import datetime

import tornado.web
import tornado.ioloop
from tornado.httpserver import HTTPServer
from tornado.httpclient import HTTPClient


class FrontendHandler(tornado.web.RequestHandler):
    # def get(self):
    #     http_client = HTTPClient()
    #     response = http_client.fetch("http://localhost:9002/api")
    #     self.write(response.body)
    #     http_client.close()
    # def handle_request(self, response):
    #     if response.error:
    #         print("Error: " + response.error)
    #     else:
    #         print(response.body)
    def get(self):
        # self.write()
        self.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


def init_frontend():
    app = tornado.web.Application([
        (r"/", FrontendHandler)
    ])
    server = HTTPServer(app)
    server.listen(8082)

    print("Py-frontend listening at port 8082\n")

    server.start(1)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    init_frontend()
