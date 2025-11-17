"""
Gunicorn configuration for CityVotes POC production deployment
"""

import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
backlog = 2048

# Worker processes
workers = os.environ.get('WEB_CONCURRENCY', 2)
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Restart workers after this many requests, with up to 50 requests variation
preload_app = True

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'cityvotes_poc'

# Server mechanics
daemon = False
pidfile = '/tmp/cityvotes_poc.pid'
tmp_upload_dir = None

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("CityVotes POC server is ready. Listening on: %s", server.address)

def worker_int(worker):
    """Called just after a worker has been killed by a signal."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)