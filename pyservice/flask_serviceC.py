import requests
from flask import Flask, request
from py_zipkin.zipkin import zipkin_span, create_http_headers_for_new_span, ZipkinAttrs
import time

app = Flask(__name__)

app.config.update({
    "ZIPKIN_HOST": "127.0.0.1",
    "ZIPKIN_PORT": "9411",
    "APP_PORT": 9001,
    # any other app config-y things
})


@zipkin_span(service_name='service_c', span_name='do_stuff')
def do_stuff():
    time.sleep(2)
    headers = create_http_headers_for_new_span()
    requests.get('http://localhost:9002/services/d', headers=headers)
    return 'OK'


def http_transport(encoded_span):
    # encoding prefix explained in https://github.com/Yelp/py_zipkin#transport
    #body = b"\x0c\x00\x00\x00\x01"+encoded_span
    body=encoded_span
    zipkin_url="http://127.0.0.1:9411/api/v1/spans"
    #zipkin_url = "http://{host}:{port}/api/v1/spans".format(
     #   host=app.config["ZIPKIN_HOST"], port=app.config["ZIPKIN_PORT"])
    headers = {"Content-Type": "application/x-thrift"}

    # You'd probably want to wrap this in a try/except in case POSTing fails
    r = requests.post(zipkin_url, data=body, headers=headers)
    print(type(encoded_span))
    print(encoded_span)
    print(body)
    print(r)
    print(r.content)


@app.route('/services/c')
def index():
    root_headers = request.headers

    # 属性传入到当前 span，已经是为当前 span 生成的了
    zipkin_attrs = ZipkinAttrs(
        trace_id=root_headers['X-B3-TraceID'],
        span_id=root_headers['X-B3-SpanID'],
        parent_span_id=root_headers['X-B3-ParentSpanID'],
        flags=root_headers.get('X-B3-Flags', '0'),
        is_sampled=root_headers['X-B3-Sampled']
    )

    with zipkin_span(
        service_name='service_c',
        span_name='index_service_c',
        zipkin_attrs=zipkin_attrs,
        transport_handler=http_transport,
        port=9001,
        sample_rate=100, #0.05, # Value between 0.0 and 100.0
    ):
        do_stuff()
        time.sleep(1)
    return 'OK', 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9001, debug=True)
