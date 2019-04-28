import tornado.web
import tornado.ioloop
from tornado.httpserver import HTTPServer


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, Tornado")


def init_app():
    app = tornado.web.Application([
        (r"/", MainHandler)
    ])
    server = HTTPServer(app)
    server.listen(8082)

    print("Py-service listening at port 8082\n")

    server.start(1)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    init_app()
