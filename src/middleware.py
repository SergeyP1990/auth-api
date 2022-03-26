from flask import Flask, request
from flask_opentracing import FlaskTracer

from tracer import _setup_jaeger


def init_trace(app: Flask):
    tracer = FlaskTracer(_setup_jaeger(), True, app=app)

    @tracer.trace()
    @app.before_request
    def before_request():
        request_id = request.headers.get("X-Request-Id")
        parent_span = tracer.get_span()
        parent_span.set_tag('http.request_id', request_id)
