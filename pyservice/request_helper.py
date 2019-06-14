# -*- coding: UTF-8 -*-

from py_zipkin.util import generate_random_64bit_string, generate_random_128bit_string
from py_zipkin.zipkin import ZipkinAttrs


def _get_headers(request):
    return request.headers


def create_zipkin_attr(request):

    headers = _get_headers(request)

    trace_id = headers.get('X-B3-TraceId', generate_random_128bit_string())
    span_id = headers.get('X-B3-SpanId', generate_random_64bit_string())
    parent_span_id = headers.get('X-B3-ParentSpanId', span_id)
    flags = headers.get('X-B3-Flags', '0')
    is_sampled = headers.get('X-B3-Sampled', False)

    return ZipkinAttrs(
        trace_id=trace_id,
        span_id=span_id,
        parent_span_id=parent_span_id,
        flags=flags,
        is_sampled=is_sampled
    )
