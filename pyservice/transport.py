# -*- coding: utf-8 -*-
# main.py
import requests


def handle_http_transport(encoded_span):
    headers = {"Content-Type": "application/x-thrift"}
    body=encoded_span
    zipkin_url="http://localhost:9411/api/v1/spans"

    requests.post(
        zipkin_url,
        data=body,
        headers=headers
    )
