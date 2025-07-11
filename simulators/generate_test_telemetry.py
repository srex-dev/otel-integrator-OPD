from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: "otel-test-service"}))
)
tracer = trace.get_tracer(__name__)
span_exporter = OTLPSpanExporter()
span_processor = BatchSpanProcessor(span_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

def generate_span():
    with tracer.start_as_current_span("sample-span"):
        print("✅ Generated test span")

if __name__ == "__main__":
    generate_span()
