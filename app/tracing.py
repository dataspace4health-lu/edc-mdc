import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

OTL_URL = os.getenv("OTL_URL")
OTL_TOKEN = os.getenv("OTL_TOKEN")

if OTL_URL:
    resource = Resource(attributes={SERVICE_NAME: "metadata-collector"})

    tracer_provider = TracerProvider(resource=resource)

    if OTL_TOKEN:
        headers = {"Authorization": "Bearer " + OTL_TOKEN}
    else:
        headers = {}

    exporter = OTLPSpanExporter(endpoint=OTL_URL, headers=headers)

    span_processor = BatchSpanProcessor(exporter)

    tracer_provider.add_span_processor(span_processor)

    trace.set_tracer_provider(tracer_provider)
