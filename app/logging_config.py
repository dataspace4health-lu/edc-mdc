import os
import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from opentelemetry import _logs
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource


class SplunkJSONFormatter(logging.Formatter):
    """
    JSON formatter for Splunk ingestion.

    Format requirements:
    - Single line per log entry
    - JSON format
    - Timestamp at the beginning
    - UTC timezone
    """

    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "dataset_id"):
            log_entry["dataset_id"] = record.dataset_id
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        # Return as single-line JSON
        return json.dumps(log_entry, ensure_ascii=False)


def configure_logging():
    """
    Configure application logging with JSON formatting for Splunk.

    Environment variables:
    - LOG_FILE_PATH: Path to write log file (e.g., /logs/metadata-capture.log)
    - LOG_LEVEL: Logging level (default: INFO)
    - LOG_FORMAT: 'json', 'text', or 'default' (default: 'default')
      - 'default': Uses uvicorn's colored logging (dev mode)
      - 'text': Plain text logs without colors
      - 'json': Structured JSON logs for Splunk

    If LOG_FILE_PATH is set, logs go to both stdout and file.
    If not set, logs only go to stdout (for local development).
    """
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file_path = os.getenv("LOG_FILE_PATH")
    log_format = os.getenv("LOG_FORMAT", "default")

    # If default format and no file path, don't configure - let uvicorn handle it
    if log_format == "default" and not log_file_path:
        print(
            f"Logging configured: level={log_level}, format=default (uvicorn colored logs)",
            file=sys.stderr,
        )
        return logging.getLogger(__name__)

    handlers = []

    # Choose formatter based on LOG_FORMAT
    if log_format == "text":
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        formatter = SplunkJSONFormatter()

    # Always log to stdout (Docker best practice)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    handlers.append(stdout_handler)

    # If LOG_FILE_PATH is set, also write to file
    if log_file_path:
        # Ensure directory exists
        log_dir = Path(log_file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(SplunkJSONFormatter())
        handlers.append(file_handler)

        print(
            f"Logging configured: level={log_level}, format={log_format}, file={log_file_path}",
            file=sys.stderr,
        )
    else:
        print(
            f"Logging configured: level={log_level}, format={log_format}, output=stdout only",
            file=sys.stderr,
        )

    # Add OTEL logging handler if OTL_URL is configured
    otel_url = os.getenv("OTL_URL")
    if otel_url:
        try:
            # Setup OTEL logging (same resource as tracing)
            resource = Resource(attributes={SERVICE_NAME: "metadata-collector"})
            logger_provider = LoggerProvider(resource=resource)

            # Setup exporter with auth header if token provided
            otel_token = os.getenv("OTL_TOKEN")
            headers = {"Authorization": f"Bearer {otel_token}"} if otel_token else {}

            # Create OTLP log exporter (use logs endpoint instead of traces)
            log_exporter = OTLPLogExporter(
                endpoint=otel_url.replace("/v1/traces", "/v1/logs"), headers=headers
            )

            # Add batch processor for efficient log export
            logger_provider.add_log_record_processor(
                BatchLogRecordProcessor(log_exporter)
            )

            # Set as global logger provider
            _logs.set_logger_provider(logger_provider)

            # Create handler and add to handlers list
            otel_handler = LoggingHandler(logger_provider=logger_provider)
            otel_handler.setLevel(getattr(logging, log_level))
            handlers.append(otel_handler)

            print(f"✅ OTEL logging enabled: {otel_url}", file=sys.stderr)
        except Exception as e:
            print(f"⚠️  Failed to configure OTEL logging: {e}", file=sys.stderr)

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        handlers=handlers,
        force=True,  # Override any existing configuration
    )

    # Also reconfigure uvicorn's loggers to use JSON format
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        logger = logging.getLogger(logger_name)
        logger.handlers = []
        for handler in handlers:
            logger.addHandler(handler)
        logger.propagate = False

    return logging.getLogger(__name__)
