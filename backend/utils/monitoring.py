"""
Monitoring & Observability Configuration
Includes: Sentry, Prometheus, Structured Logging
"""

import os
import logging
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from pythonjsonlogger import jsonlogger
from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_fastapi_instrumentator import Instrumentator


# ============================================
# SENTRY CONFIGURATION
# ============================================

def init_sentry():
    """Initialize Sentry for error tracking"""
    sentry_dsn = os.environ.get('SENTRY_DSN')
    
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                StarletteIntegration(transaction_style="endpoint"),
                FastApiIntegration(transaction_style="endpoint"),
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR
                ),
            ],
            traces_sample_rate=0.1,  # 10% des requêtes tracées
            profiles_sample_rate=0.1,  # 10% profiling
            environment=os.environ.get('ENV', 'production'),
            release=f"vectort@{os.environ.get('VERSION', '1.0.0')}",
            send_default_pii=False,  # GDPR compliance
            attach_stacktrace=True,
            before_send=before_send_sentry,
        )
        print("✅ Sentry initialized")
    else:
        print("⚠️ SENTRY_DSN not set, error tracking disabled")


def before_send_sentry(event, hint):
    """Filter sensitive data before sending to Sentry"""
    # Remove sensitive headers
    if 'request' in event:
        if 'headers' in event['request']:
            sensitive_headers = ['authorization', 'cookie', 'x-api-key']
            for header in sensitive_headers:
                if header in event['request']['headers']:
                    event['request']['headers'][header] = '[Filtered]'
    
    # Remove sensitive query params
    if 'query_string' in event.get('request', {}):
        event['request']['query_string'] = '[Filtered]'
    
    return event


# ============================================
# STRUCTURED LOGGING
# ============================================

def setup_logger():
    """Configure structured JSON logging"""
    logger = logging.getLogger()
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # JSON formatter
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    return logger


# ============================================
# PROMETHEUS METRICS
# ============================================

# Request metrics (handled by instrumentator)
# Custom business metrics

generation_counter = Counter(
    'vectort_generations_total',
    'Total number of code generations',
    ['status', 'model', 'framework', 'mode']
)

generation_duration = Histogram(
    'vectort_generation_duration_seconds',
    'Time spent generating code',
    ['model', 'framework', 'mode'],
    buckets=[1, 5, 10, 15, 20, 30, 45, 60, 90, 120]
)

llm_cost = Counter(
    'vectort_llm_cost_usd',
    'Total LLM API cost in USD',
    ['provider', 'model']
)

cache_hits = Counter(
    'vectort_cache_hits_total',
    'Number of cache hits',
    ['cache_type']
)

cache_misses = Counter(
    'vectort_cache_misses_total',
    'Number of cache misses',
    ['cache_type']
)

active_users = Gauge(
    'vectort_active_users',
    'Number of currently active users'
)

credits_consumed = Counter(
    'vectort_credits_consumed_total',
    'Total credits consumed',
    ['plan', 'operation']
)

deployment_counter = Counter(
    'vectort_deployments_total',
    'Total deployments initiated',
    ['platform', 'status']
)

oauth_logins = Counter(
    'vectort_oauth_logins_total',
    'OAuth login attempts',
    ['provider', 'status']
)

payment_transactions = Counter(
    'vectort_payment_transactions_total',
    'Payment transactions',
    ['status', 'package']
)

# Application info
app_info = Info('vectort_app', 'Vectort.io application info')


def init_prometheus(app):
    """Initialize Prometheus instrumentation"""
    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=False,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="vectort_http_requests_inprogress",
        inprogress_labels=True,
    )
    
    instrumentator.instrument(app)
    instrumentator.expose(app, endpoint="/api/metrics", include_in_schema=False)
    
    # Set app info
    app_info.info({
        'version': os.environ.get('VERSION', '1.0.0'),
        'environment': os.environ.get('ENV', 'production'),
        'python_version': '3.11',
        'fastapi_version': 'latest'
    })
    
    print("✅ Prometheus metrics initialized at /api/metrics")


# ============================================
# HELPER FUNCTIONS
# ============================================

def track_generation(
    status: str,
    model: str,
    framework: str,
    mode: str,
    duration: float,
    cost: float = 0
):
    """Track code generation metrics"""
    generation_counter.labels(
        status=status,
        model=model,
        framework=framework,
        mode=mode
    ).inc()
    
    generation_duration.labels(
        model=model,
        framework=framework,
        mode=mode
    ).observe(duration)
    
    if cost > 0:
        llm_cost.labels(
            provider=model.split('-')[0] if '-' in model else model,
            model=model
        ).inc(cost)


def track_cache(hit: bool, cache_type: str = "llm"):
    """Track cache hit/miss"""
    if hit:
        cache_hits.labels(cache_type=cache_type).inc()
    else:
        cache_misses.labels(cache_type=cache_type).inc()


def track_deployment(platform: str, status: str):
    """Track deployment"""
    deployment_counter.labels(
        platform=platform,
        status=status
    ).inc()


def track_oauth(provider: str, status: str):
    """Track OAuth login"""
    oauth_logins.labels(
        provider=provider,
        status=status
    ).inc()


def track_payment(status: str, package: str):
    """Track payment"""
    payment_transactions.labels(
        status=status,
        package=package
    ).inc()


def track_credits(plan: str, operation: str, amount: int):
    """Track credit consumption"""
    credits_consumed.labels(
        plan=plan,
        operation=operation
    ).inc(amount)


# ============================================
# LOGGING HELPERS
# ============================================

def log_generation_started(logger, user_id: str, project_id: str, framework: str, model: str):
    """Log generation start"""
    logger.info(
        "generation_started",
        extra={
            "user_id": user_id,
            "project_id": project_id,
            "framework": framework,
            "model": model,
            "event_type": "generation"
        }
    )


def log_generation_completed(logger, user_id: str, project_id: str, duration: float, code_length: int, cost: float):
    """Log generation completion"""
    logger.info(
        "generation_completed",
        extra={
            "user_id": user_id,
            "project_id": project_id,
            "duration_seconds": duration,
            "code_length": code_length,
            "cost_usd": cost,
            "event_type": "generation"
        }
    )


def log_generation_failed(logger, user_id: str, project_id: str, error: str, provider: str):
    """Log generation failure"""
    logger.error(
        "generation_failed",
        extra={
            "user_id": user_id,
            "project_id": project_id,
            "error": error,
            "provider": provider,
            "event_type": "generation"
        }
    )


def log_deployment(logger, user_id: str, project_id: str, platform: str, status: str):
    """Log deployment"""
    logger.info(
        "deployment",
        extra={
            "user_id": user_id,
            "project_id": project_id,
            "platform": platform,
            "status": status,
            "event_type": "deployment"
        }
    )


def log_payment(logger, user_id: str, amount: float, package: str, status: str):
    """Log payment"""
    logger.info(
        "payment",
        extra={
            "user_id": user_id,
            "amount_usd": amount,
            "package": package,
            "status": status,
            "event_type": "payment"
        }
    )


# Export all
__all__ = [
    'init_sentry',
    'setup_logger',
    'init_prometheus',
    'track_generation',
    'track_cache',
    'track_deployment',
    'track_oauth',
    'track_payment',
    'track_credits',
    'log_generation_started',
    'log_generation_completed',
    'log_generation_failed',
    'log_deployment',
    'log_payment',
    'generation_counter',
    'generation_duration',
    'llm_cost',
    'cache_hits',
    'cache_misses',
    'active_users',
]
