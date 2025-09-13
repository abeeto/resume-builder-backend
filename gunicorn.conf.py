import multiprocessing
import os

# Server socket
bind = '0.0.0.0:8000'
backlog = 2048

# Worker processes
workers = int(os.environ.get('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeout settings
timeout = 30
keepalive = 2
graceful_timeout = 30

# Logging
loglevel = os.environ.get('LOG_LEVEL', 'info')
accesslog = '-'  # Log to stdout
errorlog = '-'  # Log to stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'resume-builder-django'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Server mechanics
preload_app = True
daemon = False
pidfile = None
tmp_upload_dir = None

# SSL (uncomment if using HTTPS)
# keyfile = None
# certfile = None

# Django-specific settings
django_settings = os.environ.get('DJANGO_SETTINGS_MODULE', 'core.settings.production')
raw_env = [
    f'DJANGO_SETTINGS_MODULE={django_settings}',
]

# Restart workers after this many requests (helps with memory leaks)
max_requests = 1000
max_requests_jitter = 100

# Worker restart settings
graceful_timeout = 120
timeout = 120


def when_ready(server):
    server.log.info('Server is ready. Spawning workers')


def worker_int(worker):
    worker.log.info('worker received INT or QUIT signal')


def on_exit(server):
    server.log.info('Server is shutting down')


def on_starting(server):
    server.log.info('Server is starting')
