import datetime

from py_zipkin import Encoding
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from transport import http_transport
from wsgiref.simple_server import make_server


@view_config(route_name='print_date')
def print_date(request):
    return Response(str(datetime.datetime.now()))


def main():
    settings = {}
    settings['service_name'] = 'backend'
    settings['zipkin.encoding'] = Encoding.V2_JSON
    settings['zipkin.transport_handler'] = http_transport

    config = Configurator(settings=settings)
    config.include('pyramid_zipkin')
    config.add_route('print_date', '/services/d')
    config.scan()

    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 9002, app)
    print("Py-service_D listening at port 9002\n")
    server.serve_forever()


if __name__ == '__main__':
    main()
