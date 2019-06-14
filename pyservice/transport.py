# -*- coding: UTF-8 -*-

from py_zipkin.transport import BaseTransportHandler
from kafka import KafkaProducer

import json
import requests

KAFKA_SERVER = '*.*.*.*:9092'
KAFKA_TOPIC = 'zipkin'
HTTP_API = 'http://localhost:9411/api/v2/spans'


class HttpTransport(BaseTransportHandler):

    def get_max_payload_bytes(self):
        return None

    def send(self, encoded_span):
        print(encoded_span)

        requests.post(
            HTTP_API,
            data=encoded_span,
            headers={'Content-Type': 'application/json'},
        )


class KafkaTransport(BaseTransportHandler):

    def __init__(self, max_payload_bytes=None):
        self.max_payload_bytes = max_payload_bytes
        self.payloads = []

    def get_payloads(self):
        return self.payloads

    def get_max_payload_bytes(self):
        if self.max_payload_bytes is not None:
            return self.max_payload_bytes

        # By default Kafka rejects messages bigger than 1000012 bytes.
        return 1000012

    def send(self, encoded_span):
        # print(encoded_span)
        # utf8_span = json.dumps(encoded_span, ensure_ascii=False).encode('utf-8')

        data_span = json.loads(encoded_span)
        print(data_span)

        producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER,
                                 value_serializer=lambda m: json.dumps(m).encode('utf-8'))

        # produce asynchronously with callbacks
        producer.send(KAFKA_TOPIC, data_span).add_callback(on_send_success).add_errback(on_send_error)
        producer.close()


def on_send_success(record_metadata):
    print('kafka message send')
    # print('kakfa topic： {}'.format(record_metadata.topic))
    # print('kakfa partition： {}'.format(record_metadata.partition))
    # print('kakfa offset： {}'.format(record_metadata.offset))


def on_send_error(excp):
    print('I am an *** errback *** %s', excp)
    # handle exception
