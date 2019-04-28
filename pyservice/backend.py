import tornado.web
import tornado.ioloop
from tornado.httpserver import HTTPServer


class BackendHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, Tornado")


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
