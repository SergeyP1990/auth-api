from core.config import jaeger_settings as js
from jaeger_client import Config


def _setup_jaeger():
    jaeger_config = {
        "sampler": {
            "type": js.JAEGER_TYPE,
            "param": 1,
        },
        "local_agent": {
            "reporting_host": js.REPORTING_HOST,
            "reporting_port": js.REPORTING_PORT,
        },
        "logging": True,
    }

    config = Config(
        config=jaeger_config,
        service_name="async-api",
        validate=True,
    )
    return config.initialize_tracer()
